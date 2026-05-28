from fastapi import APIRouter, BackgroundTasks
from riaes.core.agent_manager import run_agent_recommendation

router = APIRouter()

@router.get("/")
async def list_agents():
    return {"agents": ["data_load", "strategy", "competitive_intel", "pricing", "inventory", "monday_morning", "promotions", "assortment", "planning"]}

@router.post("/{agent_name}/run")
async def trigger_agent(agent_name: str, sku: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_agent_recommendation, agent_name, sku)
    return {"message": f"Agent {agent_name} triggered for SKU {sku}. Check portal for recommendations."}
