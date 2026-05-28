from riaes.database import engine, Base
from riaes.models.models import Product, Inventory, CompetitorPrice, AgentTask, Recommendation

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("RIAES Database initialized.")
