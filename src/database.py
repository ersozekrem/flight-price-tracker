# src/database.py
import sqlite3
from datetime import datetime
import json
from pathlib import Path

class FlightDatabase:
    def __init__(self, db_path='data/flight_history.db'):
        """Initialize database connection"""
        # Create data directory if it doesn't exist
        Path('data').mkdir(exist_ok=True)
        
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for search metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flight_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_date DATE,
                return_date DATE,
                search_type TEXT
            )
        ''')
        
        # Table for individual flights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER NOT NULL,
                price REAL,
                airline TEXT,
                departure_time TEXT,
                arrival_time TEXT,
                duration TEXT,
                stops INTEGER,
                flight_details TEXT,
                raw_text TEXT,
                FOREIGN KEY (search_id) REFERENCES flight_searches(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully!")
    
    def save_search(self, origin, destination, flights_data, departure_date=None, return_date=None):
        """Save a complete search and its results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert search record
            cursor.execute('''
                INSERT INTO flight_searches (origin, destination, departure_date, return_date)
                VALUES (?, ?, ?, ?)
            ''', (origin, destination, departure_date, return_date))
            
            search_id = cursor.lastrowid
            
            # Insert each flight
            for flight in flights_data:
                cursor.execute('''
                    INSERT INTO flights (
                        search_id, price, airline, departure_time, 
                        arrival_time, duration, stops, flight_details, raw_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    search_id,
                    flight.get('price'),
                    flight.get('airline'),
                    flight.get('departure'),
                    flight.get('arrival'),
                    flight.get('duration'),
                    flight.get('stops'),
                    flight.get('details'),
                    flight.get('raw_text')
                ))
            
            conn.commit()
            print(f"✅ Saved {len(flights_data)} flights to database!")
            return search_id
            
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_price_history(self, origin, destination, days=30):
        """Get price history for a route"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                fs.search_date,
                MIN(f.price) as min_price,
                AVG(f.price) as avg_price,
                MAX(f.price) as max_price
            FROM flight_searches fs
            JOIN flights f ON fs.id = f.search_id
            WHERE fs.origin = ? AND fs.destination = ?
                AND fs.search_date >= datetime('now', '-' || ? || ' days')
                AND f.price IS NOT NULL
            GROUP BY DATE(fs.search_date)
            ORDER BY fs.search_date
        ''', (origin, destination, days))
        
        results = cursor.fetchall()
        conn.close()
        
        return results


# Test function
if __name__ == "__main__":
    # Test database creation
    db = FlightDatabase()
    print("Database initialized!")
