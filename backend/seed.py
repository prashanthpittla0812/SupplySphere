"""SupplySphere Database Seeder.

Usage:
    python seed.py                          # Full seed (roles, users, demo data)
    python seed.py --users-only             # Only reset demo user passwords

Auto-seed is also triggered on app startup via lifespan handler.
"""

import asyncio
import sys

from app.db.seeds.runner import seed_all


def main():
    users_only = "--users-only" in sys.argv
    asyncio.run(seed_all(users_only=users_only))


if __name__ == "__main__":
    main()
