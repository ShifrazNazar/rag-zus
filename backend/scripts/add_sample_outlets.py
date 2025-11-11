"""
Script to add sample outlet data to the database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import SessionLocal, Outlet, init_db

# Initialize database
init_db()

# Sample outlet data
sample_outlets = [
    {
        "name": "ZUS Coffee 1 Utama",
        "location": "1 Utama Shopping Centre, Bandar Utama",
        "district": "Petaling Jaya",
        "hours": "8:00 AM - 10:00 PM",
        "services": "WiFi, Parking, Drive-thru, Dine-in",
        "lat": 3.1502,
        "lon": 101.6167
    },
    {
        "name": "ZUS Coffee KLCC",
        "location": "Suria KLCC, Kuala Lumpur City Centre",
        "district": "Kuala Lumpur",
        "hours": "9:00 AM - 10:00 PM",
        "services": "WiFi, Parking, Dine-in, Takeaway",
        "lat": 3.1579,
        "lon": 101.7116
    },
    {
        "name": "ZUS Coffee Subang Jaya",
        "location": "Empire Shopping Gallery, Subang Jaya",
        "district": "Subang Jaya",
        "hours": "8:00 AM - 11:00 PM",
        "services": "WiFi, Parking, Dine-in",
        "lat": 3.0738,
        "lon": 101.5931
    },
    {
        "name": "ZUS Coffee Sunway Pyramid",
        "location": "Sunway Pyramid Shopping Mall",
        "district": "Petaling Jaya",
        "hours": "10:00 AM - 10:00 PM",
        "services": "WiFi, Parking, Dine-in, Delivery",
        "lat": 3.0731,
        "lon": 101.6067
    },
    {
        "name": "ZUS Coffee Pavilion",
        "location": "Pavilion Kuala Lumpur",
        "district": "Kuala Lumpur",
        "hours": "9:00 AM - 10:00 PM",
        "services": "WiFi, Parking, Dine-in",
        "lat": 3.1492,
        "lon": 101.7128
    },
    {
        "name": "ZUS Coffee Mid Valley",
        "location": "Mid Valley Megamall",
        "district": "Kuala Lumpur",
        "hours": "9:00 AM - 10:00 PM",
        "services": "WiFi, Parking, Dine-in, Takeaway",
        "lat": 3.1181,
        "lon": 101.6769
    },
    {
        "name": "ZUS Coffee Bangsar",
        "location": "Bangsar Shopping Centre",
        "district": "Kuala Lumpur",
        "hours": "8:00 AM - 10:00 PM",
        "services": "WiFi, Dine-in, Takeaway",
        "lat": 3.1594,
        "lon": 101.6697
    },
    {
        "name": "ZUS Coffee Mont Kiara",
        "location": "Mont Kiara Mall",
        "district": "Kuala Lumpur",
        "hours": "8:00 AM - 9:00 PM",
        "services": "WiFi, Parking, Dine-in",
        "lat": 3.1736,
        "lon": 101.6553
    }
]


def add_sample_outlets():
    """Add sample outlets to the database."""
    db = SessionLocal()
    try:
        # Check if outlets already exist
        existing_count = db.query(Outlet).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} outlets.")
            response = input("Do you want to add more? (y/n): ")
            if response.lower() != 'y':
                print("Skipping...")
                return
        
        # Add sample outlets
        for outlet_data in sample_outlets:
            outlet = Outlet(**outlet_data)
            db.add(outlet)
        
        db.commit()
        print(f"✓ Added {len(sample_outlets)} sample outlets to the database")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding outlets: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_outlets()

