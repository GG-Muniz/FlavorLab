"""
Utility script to create an admin user and a demo user.

Usage (from backend directory):
  .\\venv\\Scripts\\Activate.ps1
  python -m scripts.seed_users --admin-email admin@example.com --admin-password StrongPass123 \
      --demo-email demo@flavorlab.local --demo-password DemoPass123

Behavior:
  - Admin: created if missing; if exists, password is not changed unless --force-admin is passed.
  - Demo: upsert behavior; if a user with the demo email exists, it is updated (password reset),
          otherwise it is created. This lets you re-create demo accounts freely during testing.
"""

import argparse
from app.database import SessionLocal, create_tables, ensure_user_columns
from app.services.auth import AuthService
from app import models


def create_admin(db, email: str, password: str, force: bool = False):
    existing = AuthService.get_user_by_email(db, email)
    if existing:
        if force:
            existing.hashed_password = AuthService.get_password_hash(password)
            existing.is_verified = True
            existing.is_active = True
            db.commit()
            print(f"[Admin] Updated password for {email}")
        else:
            print(f"[Admin] User already exists: {email} (use --force-admin to reset password)")
        return existing
    user = AuthService.create_user(db, email=email, password=password, username='admin', first_name='Admin', last_name='User', is_active=True)
    user.is_verified = True
    db.commit()
    print(f"[Admin] Created {email}")
    return user


def upsert_demo(db, email: str, password: str):
    existing = AuthService.get_user_by_email(db, email)
    if existing:
        existing.hashed_password = AuthService.get_password_hash(password)
        existing.is_active = True
        existing.is_verified = True
        existing.first_name = 'Demo'
        existing.last_name = 'User'
        db.commit()
        print(f"[Demo] Updated demo account: {email}")
        return existing
    user = AuthService.create_user(db, email=email, password=password, username='demo', first_name='Demo', last_name='User', is_active=True)
    user.is_verified = True
    db.commit()
    print(f"[Demo] Created demo account: {email}")
    return user


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-email', required=True)
    parser.add_argument('--admin-password', required=True)
    parser.add_argument('--force-admin', action='store_true')
    parser.add_argument('--demo-email', required=True)
    parser.add_argument('--demo-password', required=True)
    args = parser.parse_args()

    # Ensure tables/columns exist
    create_tables()
    ensure_user_columns()

    with SessionLocal() as db:
        create_admin(db, args.admin_email, args.admin_password, force=args.force_admin)
        upsert_demo(db, args.demo_email, args.demo_password)


if __name__ == '__main__':
    main()


