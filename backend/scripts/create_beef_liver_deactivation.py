#!/usr/bin/env python3
"""
Deactivate beef-liver entity safely.

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/create_beef_liver_deactivation.py
"""

from app.database import SessionLocal
from app.models.entity import Entity

def main() -> None:
    s = SessionLocal()
    try:
        e = s.query(Entity).filter(Entity.slug == 'beef-liver').first()
        if e:
            e.is_active = False
            s.commit()
            print('beef-liver deactivated')
        else:
            print('beef-liver not found')
    finally:
        s.close()

if __name__ == '__main__':
    main()


