from riaes.agents.core_agents import agents_map
from riaes.database import SessionLocal
from riaes.models.models import Recommendation, Product, AgentTask, TaskStatus
import json

async def run_agent_recommendation(agent_name: str, product_sku: str):
    db = SessionLocal()
    agent = agents_map.get(agent_name)
    if not agent:
        db.close()
        return {"error": "Agent not found"}

    product = db.query(Product).filter(Product.sku == product_sku).first()
    if not product:
        db.close()
        return {"error": "Product not found"}

    # Execute actual Agentic AI Run
    try:
        # In a real scenario with API keys, we would do:
        # result = await agent.run(f"Analyze the performance and market position for SKU {product_sku}. Product details: {product.name}, {product.description}. Current price: {product.current_price}")
        # recommendation_text = result.data.recommendation

        # For demonstration without API keys, we simulate the agent's internal "thought process"
        # but keep it within the agentic framework's context.
        simulated_results = {
            "pricing": {
                "recommendation": f"Decrease price of {product.name} by 5%",
                "impact": 1200.0,
                "reasoning": f"Competitive analysis via Scraper Agent shows similar products at {product.current_price * 0.93}. Reducing to {product.current_price * 0.95} balances volume and margin."
            },
            "inventory": {
                "recommendation": f"Reorder 50 units of {product.name}",
                "impact": 500.0,
                "reasoning": f"Inventory Agent detected velocity increase. Current quantity (50) will stock out in 12 days. Strategic safety stock is 75 units."
            }
        }

        res = simulated_results.get(agent_name, {
            "recommendation": f"Optimize {product.name} strategy",
            "impact": 100.0,
            "reasoning": f"Standard {agent_name} analysis based on current enterprise data."
        })

        new_rec = Recommendation(
            agent_name=agent_name,
            product_id=product.id,
            action=res["recommendation"],
            impact_estimate=res["impact"],
            reasoning=res["reasoning"]
        )
        db.add(new_rec)

        new_task = AgentTask(
            agent_name=agent_name,
            task_type="OPTIMIZATION_ACTION",
            description=f"{agent_name.capitalize()} Agent Recommendation for {product.sku}",
            payload={"sku": product_sku, "action": res["recommendation"], "reasoning": res["reasoning"]},
            status=TaskStatus.PENDING
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"status": "success", "task_id": new_task.id}
    except Exception as e:
        return {"error": f"Agent execution failed: {str(e)}"}
    finally:
        db.close()
