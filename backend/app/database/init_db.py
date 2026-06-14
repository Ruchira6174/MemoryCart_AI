#!/usr/bin/env python
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to path to ensure imports work correctly when run as standalone script
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.database.connection import engine, Base, SessionLocal
from app.models.memory import User, Memory
from app.models.order import Order
from app.models.refund import Refund

def init_db():
    print("Dropping existing tables and creating new ones...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Inserting sample users...")
        john = User(user_id=1, name="John")
        sarah = User(user_id=2, name="Sarah")
        db.add_all([john, sarah])
        db.commit()

        print("Inserting sample orders...")
        order1 = Order(
            order_id=1001,
            user_id=john.user_id,
            product_name="Premium Headphones (ORD1001)",
            status="delivered",
            delivery_date=datetime.utcnow() - timedelta(days=2)
        )
        order2 = Order(
            order_id=1002,
            user_id=sarah.user_id,
            product_name="Ergonomic Keyboard (ORD1002)",
            status="shipped",
            delivery_date=datetime.utcnow() + timedelta(days=3)
        )
        db.add_all([order1, order2])
        db.commit()

        print("Inserting sample refunds...")
        refund1 = Refund(
            refund_id=1001,
            order_id=order1.order_id,
            status="processed",
            amount=129.99
        )
        db.add(refund1)
        db.commit()

        print("Inserting sample memories...")
        memory1 = Memory(
            user_id=john.user_id,
            summary="Previous order issue regarding delivery delay on premium headphones.",
            issue_type="ORDER"
        )
        memory2 = Memory(
            user_id=sarah.user_id,
            summary="Refund discussion regarding return policy details.",
            issue_type="REFUND"
        )
        db.add_all([memory1, memory2])
        db.commit()

        print("Database successfully seeded!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred while seeding the database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
