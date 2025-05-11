import sqlite3
from datetime import datetime

def add_created_at_column():
    # Connect to the database
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    
    try:
        # Add the created_at column
        cursor.execute('ALTER TABLE user ADD COLUMN created_at DATETIME')
        
        # Update existing rows with current timestamp
        current_time = datetime.utcnow().isoformat()
        cursor.execute('UPDATE user SET created_at = ?', (current_time,))
        
        # Commit the changes
        conn.commit()
        print("Successfully added created_at column and updated existing rows")
        
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Column already exists")
        else:
            print(f"An error occurred: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_created_at_column() 