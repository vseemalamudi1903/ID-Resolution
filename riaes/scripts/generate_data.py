from riaes.database import SessionLocal
from riaes.models.models import Product, Inventory, CompetitorPrice
from datetime import datetime, timezone

def generate_sample_data():
    db = SessionLocal()

    if db.query(Product).count() > 0:
        db.close()
        return

    products = [
        Product(sku="DSG-1001", name="Pro Running Shoes", description="Elite performance running shoes.", category="Footwear", base_price=120.0, current_price=120.0, cost=60.0),
        Product(sku="AMZ-2002", name="Wireless Headphones", description="Noise-canceling over-ear headphones.", category="Electronics", base_price=199.0, current_price=199.0, cost=100.0),
        Product(sku="WMT-3003", name="Mountain Bike", description="Durable mountain bike for all terrains.", category="Sports", base_price=450.0, current_price=450.0, cost=250.0),
        Product(sku="TGT-4004", name="Smart Coffee Maker", description="Programmable coffee maker with app control.", category="Home", base_price=89.0, current_price=89.0, cost=45.0)
    ]

    db.add_all(products)
    db.commit()

    for p in products:
        inv = Inventory(product_id=p.id, quantity_on_hand=50, location="Warehouse-A")
        db.add(inv)

    comp_prices = [
        CompetitorPrice(product_id=products[0].id, competitor_name="Dicks Sporting Goods", price=115.0, is_on_sale=True),
        CompetitorPrice(product_id=products[1].id, competitor_name="Amazon", price=189.0, is_on_sale=False),
        CompetitorPrice(product_id=products[2].id, competitor_name="Walmart", price=430.0, is_on_sale=True),
        CompetitorPrice(product_id=products[3].id, competitor_name="Target", price=85.0, is_on_sale=False)
    ]
    db.add_all(comp_prices)

    db.commit()
    db.close()
    print("RIAES Sample data generated.")

if __name__ == "__main__":
    generate_sample_data()
