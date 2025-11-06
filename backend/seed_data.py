"""
Seed database with initial test data for new simplified schema
"""
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models import User, Customer, Baustelle, LeistungsverzeichnisEntry, Worktime, BaustelleRate, SpecialDay
from datetime import date, timedelta
from decimal import Decimal


def seed_database():
    """Seed the database with test data"""
    print("Initializing database...")
    init_db()

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping...")
            return

        print("Creating users...")
        # Create users with extended fields
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            is_admin=True,
            first_name="Admin",
            last_name="User"
        )
        employee1 = User(
            username="max.mueller",
            email="max.mueller@example.com",
            password_hash=get_password_hash("password123"),
            is_admin=False,
            first_name="Max",
            last_name="Müller",
            employee_type="Geselle"
        )
        employee2 = User(
            username="anna.schmidt",
            email="anna.schmidt@example.com",
            password_hash=get_password_hash("password123"),
            is_admin=False,
            first_name="Anna",
            last_name="Schmidt",
            employee_type="Meister"
        )
        employee3 = User(
            username="thomas.weber",
            email="thomas.weber@example.com",
            password_hash=get_password_hash("password123"),
            is_admin=False,
            first_name="Thomas",
            last_name="Weber",
            employee_type="Polier"
        )

        db.add_all([admin_user, employee1, employee2, employee3])
        db.commit()

        print("Creating customers...")
        # Create customers
        customer1 = Customer(
            name="Müller GmbH",
            customer_number="C001",
            active=True
        )
        customer2 = Customer(
            name="Schmidt & Partner",
            customer_number="C002",
            active=True
        )

        db.add_all([customer1, customer2])
        db.commit()

        print("Creating baustellen (construction sites)...")
        # Create baustellen
        baustellen = [
            Baustelle(customer_id=customer1.id, name="Baustelle Hauptstraße", address="Hauptstraße 1, 80331 München", active=True),
            Baustelle(customer_id=customer1.id, name="Baustelle Berliner Allee", address="Berliner Allee 50, 10117 Berlin", active=True),
            Baustelle(customer_id=customer2.id, name="Baustelle Frankfurt Main", address="Mainzer Landstraße 100, 60327 Frankfurt", active=True),
        ]

        db.add_all(baustellen)
        db.commit()

        print("Creating Leistungsverzeichnis entries...")
        # Create LV entries for each baustelle
        lv_entries = []

        # Baustelle 1 LV entries
        lv_entries.extend([
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[0].id,
                position_number=None,
                description="Freitext",
                is_freitext=True,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[0].id,
                position_number="1.1",
                description="Erdarbeiten",
                unit="m³",
                is_freitext=False,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[0].id,
                position_number="2.1",
                description="Betonarbeiten",
                unit="m³",
                is_freitext=False,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[0].id,
                position_number="3.1",
                description="Maurerarbeiten",
                unit="m²",
                is_freitext=False,
                active=True
            ),
        ])

        # Baustelle 2 LV entries
        lv_entries.extend([
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[1].id,
                position_number=None,
                description="Freitext",
                is_freitext=True,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[1].id,
                position_number="1.1",
                description="Aushubarbeiten",
                unit="m³",
                is_freitext=False,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[1].id,
                position_number="2.1",
                description="Fundamentarbeiten",
                unit="m²",
                is_freitext=False,
                active=True
            ),
        ])

        # Baustelle 3 LV entries
        lv_entries.extend([
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[2].id,
                position_number=None,
                description="Freitext",
                is_freitext=True,
                active=True
            ),
            LeistungsverzeichnisEntry(
                baustelle_id=baustellen[2].id,
                position_number="1.1",
                description="Abbrucharbeiten",
                unit="Std",
                is_freitext=False,
                active=True
            ),
        ])

        db.add_all(lv_entries)
        db.commit()

        print("Creating worktime entries (new schema)...")
        # Create sample worktime entries with new schema
        today = date.today()

        worktimes = [
            # Regular LV entry worktime
            Worktime(
                user_id=employee1.id,
                customer_id=customer1.id,
                baustelle_id=baustellen[0].id,
                lv_entry_id=lv_entries[1].id,  # Erdarbeiten
                date=today,
                worked_hours=8,
                freitext_description=None,
                processed=False
            ),
            # Freitext worktime
            Worktime(
                user_id=employee1.id,
                customer_id=customer1.id,
                baustelle_id=baustellen[1].id,
                lv_entry_id=None,
                date=today,
                worked_hours=4,
                freitext_description="Sonstige Arbeiten - Reinigung und Vorbereitung",
                processed=False
            ),
        ]

        db.add_all(worktimes)
        db.commit()

        print("Creating baustelle rates...")
        # Create hourly rates for each baustelle and employee type
        rates = []
        for baustelle in baustellen:
            # Rates for Baustelle 1 (higher rates)
            if baustelle.id == baustellen[0].id:
                rates.extend([
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Geselle",
                        hourly_rate=Decimal("45.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Meister",
                        hourly_rate=Decimal("65.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Polier",
                        hourly_rate=Decimal("75.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                ])
            # Rates for other baustellen (standard rates)
            else:
                rates.extend([
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Geselle",
                        hourly_rate=Decimal("40.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Meister",
                        hourly_rate=Decimal("55.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                    BaustelleRate(
                        baustelle_id=baustelle.id,
                        employee_type="Polier",
                        hourly_rate=Decimal("70.00"),
                        valid_from=date(2025, 1, 1)
                    ),
                ])

        db.add_all(rates)
        db.commit()

        print("Creating special days...")
        # Create sample special days
        special_days = [
            # Max Müller has a vacation day
            SpecialDay(
                user_id=employee1.id,
                date=today - timedelta(days=2),
                day_type="Urlaub",
                description="Familienurlaub",
                created_by=admin_user.id
            ),
            # Anna Schmidt was sick
            SpecialDay(
                user_id=employee2.id,
                date=today - timedelta(days=1),
                day_type="Krank",
                description="Erkältung",
                created_by=admin_user.id
            ),
        ]

        db.add_all(special_days)
        db.commit()

        print("✓ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: username='admin', password='admin123'")
        print("  Employees:")
        print("    - username='max.mueller', password='password123' (Geselle)")
        print("    - username='anna.schmidt', password='password123' (Meister)")
        print("    - username='thomas.weber', password='password123' (Polier)")
        print("\nData created:")
        print(f"  - 4 Users (1 admin, 3 employees)")
        print(f"  - {len(baustellen)} Baustellen")
        print(f"  - {len(lv_entries)} Leistungsverzeichnis entries")
        print(f"  - {len(worktimes)} Worktime entries")
        print(f"  - {len(rates)} Baustelle rates")
        print(f"  - {len(special_days)} Special days")

    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
