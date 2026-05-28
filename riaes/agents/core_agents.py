from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List, Optional
import os

class AgentResponse(BaseModel):
    agent_name: str
    recommendation: str
    impact_estimate: float
    reasoning: str

model_name = os.getenv('AGENT_MODEL', 'test')

data_load_agent = Agent(
    model_name,
    system_prompt='You are the Data Load Agent. Your goal is to transform fragmented merchandising data into decision-ready intelligence.'
)

strategy_agent = Agent(
    model_name,
    system_prompt='You are the Strategy Agent. Monitor business health and translate objectives into prioritized actions.'
)

competitive_intel_agent = Agent(
    model_name,
    system_prompt='You are the Competitive Intelligence Agent. Provide an always-current view of competitive position across matched SKUs.'
)

pricing_agent = Agent(
    model_name,
    system_prompt='You are the Pricing Agent. Identify ticket price and promotional opportunities optimized for margin and volume.'
)

inventory_agent = Agent(
    model_name,
    system_prompt='You are the Inventory Agent. Identify where capital is trapped and where inventory levels need to move.'
)

monday_morning_agent = Agent(
    model_name,
    system_prompt='You are the Monday Morning Agent. Explain what happened last week and what to do next.'
)

promotions_agent = Agent(
    model_name,
    system_prompt='You are the Promotions Agent. Measure the true net impact of every promotion across the full customer basket.'
)

assortment_agent = Agent(
    model_name,
    system_prompt='You are the Assortment Agent. Optimize product mix breadth and depth using attribute-level and competitive data.'
)

planning_agent = Agent(
    model_name,
    system_prompt='You are the Planning Agent. Align receipts to real demand to prevent overbuy and underbuy.'
)

agents_map = {
    "data_load": data_load_agent,
    "strategy": strategy_agent,
    "competitive_intel": competitive_intel_agent,
    "pricing": pricing_agent,
    "inventory": inventory_agent,
    "monday_morning": monday_morning_agent,
    "promotions": promotions_agent,
    "assortment": assortment_agent,
    "planning": planning_agent
}
