import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_connection():
    """
    Tests the database connection using the DB_URL from the .env file.
    """
    load_dotenv()
    db_url = os.getenv("DB_URL")

    if not db_url:
        print("DB_URL not found in .env file.")
        return

    print(f"Attempting to connect to the database...")

    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            # Test the connection with a simple query
            result = connection.execute(text("SELECT 1"))
            for row in result:
                print("Connection successful: Received ->", row[0])
        print("Database connection successful!")
    except OperationalError as e:
        print(f"Database connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_connection()

