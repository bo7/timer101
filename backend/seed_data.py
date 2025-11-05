"""
Seed database with initial test data
"""
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models import User, Customer, Location, Worktime
from datetime import datetime, timedelta


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
        employee2 = User(
            username="anna.schmidt",
            email="anna.schmidt@example.com",
            password_hash=get_password_hash("password123"),
            is_admin=False
        )

        db.add_all([admin_user, employee1, employee2])
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
        customer3 = Customer(
            name="Bauer AG",
            customer_number="C003",
            active=True
        )
        customer4 = Customer(
            name="Weber Industries",
            customer_number="C004",
            active=True
        )

        db.add_all([customer1, customer2, customer3, customer4])
        db.commit()

        print("Creating locations...")
        # Create locations
        locations = [
            Location(customer_id=customer1.id, name="Hauptsitz München", address="Hauptstraße 1, 80331 München", active=True),
            Location(customer_id=customer1.id, name="Filiale Berlin", address="Berliner Allee 50, 10117 Berlin", active=True),
            Location(customer_id=customer2.id, name="Büro Frankfurt", address="Mainzer Landstraße 100, 60327 Frankfurt", active=True),
            Location(customer_id=customer2.id, name="Lager Hamburg", address="Hafenstraße 20, 20459 Hamburg", active=True),
            Location(customer_id=customer3.id, name="Werk Stuttgart", address="Industriestraße 10, 70565 Stuttgart", active=True),
            Location(customer_id=customer3.id, name="Zentrale Köln", address="Domstraße 5, 50667 Köln", active=True),
            Location(customer_id=customer4.id, name="Büro Düsseldorf", address="Königsallee 60, 40212 Düsseldorf", active=True),
        ]

        db.add_all(locations)
        db.commit()

        print("Creating worktime entries...")
        # Create sample worktime entries for the last few days
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        worktimes = [
            # Today - employee1
            Worktime(
                user_id=employee1.id,
                customer_id=customer1.id,
                location_id=locations[0].id,
                description="Installation der neuen Software",
                start_time=today.replace(hour=8, minute=0),
                end_time=today.replace(hour=12, minute=0),
                break_minutes=0,
                worked_minutes=240,
                processed=False
            ),
            Worktime(
                user_id=employee1.id,
                customer_id=customer2.id,
                location_id=locations[2].id,
                description="Wartungsarbeiten",
                start_time=today.replace(hour=13, minute=0),
                end_time=today.replace(hour=17, minute=30),
                break_minutes=30,
                worked_minutes=240,
                processed=False
            ),

            # Yesterday - employee1
            Worktime(
                user_id=employee1.id,
                customer_id=customer3.id,
                location_id=locations[4].id,
                description="Netzwerk-Setup",
                start_time=(today - timedelta(days=1)).replace(hour=9, minute=0),
                end_time=(today - timedelta(days=1)).replace(hour=17, minute=0),
                break_minutes=60,
                worked_minutes=420,
                processed=True
            ),

            # 2 days ago - employee1
            Worktime(
                user_id=employee1.id,
                customer_id=customer1.id,
                location_id=locations[1].id,
                description="Server Migration",
                start_time=(today - timedelta(days=2)).replace(hour=8, minute=30),
                end_time=(today - timedelta(days=2)).replace(hour=16, minute=30),
                break_minutes=45,
                worked_minutes=435,
                processed=True
            ),

            # Today - employee2
            Worktime(
                user_id=employee2.id,
                customer_id=customer4.id,
                location_id=locations[6].id,
                description="Schulung der Mitarbeiter",
                start_time=today.replace(hour=9, minute=0),
                end_time=today.replace(hour=15, minute=0),
                break_minutes=45,
                worked_minutes=315,
                processed=False
            ),
        ]

        db.add_all(worktimes)
        db.commit()

        print("✓ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: username='admin', password='admin123'")
        print("  Employee 1: username='max.mueller', password='password123'")
        print("  Employee 2: username='anna.schmidt', password='password123'")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
