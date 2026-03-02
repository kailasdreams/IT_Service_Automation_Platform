"""Seed database with initial data."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.database import AsyncSessionLocal, init_db
from backend.models import User, Integration
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Create admin user if not exists
        r = await db.execute(select(User).where(User.username == "admin"))
        if not r.scalar_one_or_none():
            user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
            )
            db.add(user)
            print("Created admin user (password: admin123)")

        # Create sample integrations
        integrations = [
            ("SolarWinds", "nms"),
            ("Nagios", "nms"),
            ("ServiceNow", "itsm"),
            ("Slack", "chat"),
        ]
        for name, itype in integrations:
            r = await db.execute(select(Integration).where(Integration.name == name))
            if not r.scalar_one_or_none():
                db.add(Integration(name=name, type=itype, enabled=True))
                print(f"Created integration: {name}")

        await db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
