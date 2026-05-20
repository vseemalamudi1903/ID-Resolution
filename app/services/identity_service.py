import uuid
import json
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import Profile, Identifier, IdentityTrait, BehavioralEvent, InterestScore
from datetime import datetime, timezone

class IdentityResolutionService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_identifier(self, id_type: str, id_value: str) -> Optional[Profile]:
        identifier = self.db.query(Identifier).filter(
            Identifier.type == id_type,
            Identifier.value == id_value
        ).first()
        return identifier.profile if identifier else None

    def get_profile_by_traits(self, traits: List[dict]) -> Optional[Profile]:
        # Probabilistic matching: require BOTH IP and Fingerprint to match
        ip = next((t['value'] for t in traits if t['type'] == 'ip'), None)
        fp = next((t['value'] for t in traits if t['type'] == 'fingerprint'), None)

        if not ip or not fp:
            return None

        # Find profiles that have both matching traits
        matching_profiles = self.db.query(Profile).join(IdentityTrait).filter(
            IdentityTrait.type == 'ip',
            IdentityTrait.value == ip
        ).intersect(
            self.db.query(Profile).join(IdentityTrait).filter(
                IdentityTrait.type == 'fingerprint',
                IdentityTrait.value == fp
            )
        ).all()

        return matching_profiles[0] if matching_profiles else None

    def create_profile(self) -> Profile:
        profile = Profile(canonical_id=str(uuid.uuid4()))
        self.db.add(profile)
        self.db.flush() # Use flush instead of commit to keep transaction open
        return profile

    def link_identifier(self, profile: Profile, id_type: str, id_value: str) -> Profile:
        existing = self.db.query(Identifier).filter(
            Identifier.type == id_type,
            Identifier.value == id_value
        ).first()

        if existing:
            if existing.profile_id != profile.id:
                # Merge profiles
                profile = self.merge_profiles(profile, existing.profile)
            return profile

        new_id = Identifier(profile_id=profile.id, type=id_type, value=id_value)
        self.db.add(new_id)
        self.db.flush()
        return profile

    def update_traits(self, profile: Profile, traits: List[dict]):
        for trait_data in traits:
            existing = self.db.query(IdentityTrait).filter(
                IdentityTrait.profile_id == profile.id,
                IdentityTrait.type == trait_data['type']
            ).first()

            if existing:
                existing.value = trait_data['value']
                existing.last_seen = datetime.now(timezone.utc)
            else:
                new_trait = IdentityTrait(
                    profile_id=profile.id,
                    type=trait_data['type'],
                    value=trait_data['value']
                )
                self.db.add(new_trait)
        self.db.flush()

    def merge_profiles(self, primary: Profile, secondary: Profile) -> Profile:
        if primary.id == secondary.id:
            return primary

        # Move identifiers
        for identifier in list(secondary.identifiers):
            identifier.profile_id = primary.id

        # Move traits
        for trait in list(secondary.traits):
            existing_trait = next((t for t in primary.traits if t.type == trait.type), None)
            if existing_trait:
                existing_trait.value = trait.value
                self.db.delete(trait)
            else:
                trait.profile_id = primary.id

        # Move behavioral events
        for event in list(secondary.events):
            event.profile_id = primary.id

        # Merge interest scores
        primary_scores = {ps.category: ps for ps in primary.interest_scores}
        for s_score in list(secondary.interest_scores):
            if s_score.category in primary_scores:
                primary_scores[s_score.category].score += s_score.score
                self.db.delete(s_score)
            else:
                s_score.profile_id = primary.id
                primary.interest_scores.append(s_score)

        self.db.delete(secondary)
        self.db.flush()
        return primary

    def resolve_and_track(self, identifiers: List[dict], traits: List[dict], event: Optional[dict]):
        try:
            # 1. Try to find all profiles associated with these identifiers
            matching_profiles = []
            for id_info in identifiers:
                p = self.get_profile_by_identifier(id_info['type'], id_info['value'])
                if p and p not in matching_profiles:
                    matching_profiles.append(p)

            # 2. If no profiles found by identifiers, try probabilistic
            if not matching_profiles:
                p = self.get_profile_by_traits(traits)
                if p:
                    matching_profiles.append(p)

            # 3. Resolve to a single profile
            if not matching_profiles:
                found_profile = self.create_profile()
            else:
                def has_loyalty(profile):
                    return any(ident.type == 'loyalty_id' for ident in profile.identifiers)

                matching_profiles.sort(key=has_loyalty, reverse=True)
                found_profile = matching_profiles[0]
                for other_profile in matching_profiles[1:]:
                    found_profile = self.merge_profiles(found_profile, other_profile)

                self.db.flush()

            # 4. Link all identifiers
            for id_info in identifiers:
                found_profile = self.link_identifier(found_profile, id_info['type'], id_info['value'])

            # 5. Update traits
            self.update_traits(found_profile, traits)

            # 6. Record event and update scores
            if event:
                self.record_event(found_profile, event)

            self.db.commit()
            self.db.refresh(found_profile)
            return found_profile
        except Exception:
            self.db.rollback()
            raise

    def record_event(self, profile: Profile, event_data: dict):
        event = BehavioralEvent(
            profile_id=profile.id,
            event_type=event_data['event_type'],
            category=event_data.get('category'),
            metadata_json=json.dumps(event_data.get('metadata', {}))
        )
        self.db.add(event)

        if event.category:
            weights = {
                'purchase': 5.0,
                'customer_review': 3.0,
                'product_view': 2.0,
                'page_view': 1.0,
                'client_event': 1.0
            }
            weight = weights.get(event.event_type.lower(), 1.0)
            self.update_interest_score(profile, event.category, weight)
        self.db.flush()

    def update_interest_score(self, profile: Profile, category: str, weight: float = 1.0):
        score = self.db.query(InterestScore).filter(
            InterestScore.profile_id == profile.id,
            InterestScore.category == category
        ).first()

        if score:
            score.score += weight
        else:
            score = InterestScore(profile_id=profile.id, category=category, score=weight)
            self.db.add(score)
        self.db.flush()
