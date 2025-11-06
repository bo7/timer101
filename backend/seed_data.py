"""
Seed database with initial test data for new simplified schema
"""
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models import User, Customer, Baustelle, LeistungsverzeichnisEntry, Worktime
from datetime import date


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
        # Create users
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            is_admin=True
        )
        employee1 = User(
            username="max.mueller",
            email="max.mueller@example.com",
            password_hash=get_password_hash("password123"),
            is_admin=False
        )

        db.add_all([admin_user, employee1])
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

        print("✓ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: username='admin', password='admin123'")
        print("  Employee: username='max.mueller', password='password123'")
        print("\nData created:")
        print(f"  - {len(baustellen)} Baustellen")
        print(f"  - {len(lv_entries)} Leistungsverzeichnis entries")
        print(f"  - {len(worktimes)} Worktime entries (new schema with hours)")

    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
