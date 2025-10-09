"""
DATABASE.PY - Database Manager

This file handles the database:
1. Creates the database file (library.db)
2. Creates tables (books, users, borrowed)
3. Runs SQL queries

How to explain: "This is the database layer. 
It creates tables and executes SQL queries. 
Think of it as the storage system."
"""

import sqlite3

class Database:
    """Simple database manager - only 2 methods!"""
    
    def __init__(self):
        """Initialize database and create tables"""
        self.db_name = 'library.db'
        self.setup_tables()
    
    def setup_tables(self):
        """
        Create all database tables if they don't exist
        
        Tables:
        1. books - stores all book information
        2. users - stores all user information  
        3. borrowed - tracks which user borrowed which book
        """
        
        # Connect to database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Table 1: Books
        # Stores: ISBN (unique ID), title, author, genre, type,
        #         total_copies (how many copies library has),
        #         available_copies (how many can be borrowed now),
        #         borrow_count (popularity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                genre TEXT,
                type TEXT,
                total_copies INTEGER,
                available_copies INTEGER,
                borrow_count INTEGER
            )
        ''')
        
        # Table 2: Users
        # Stores: user_id (unique ID), name, membership tier, fines owed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                membership TEXT,
                fines REAL
            )
        ''')
        
        # Table 3: Borrowed Books
        # Stores: which user borrowed which book and when
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowed (
                user_id TEXT,
                isbn TEXT,
                borrow_date TEXT
            )
        ''')
        
        # Save changes and close
        conn.commit()
        conn.close()
    
    def run_query(self, query, params=()):
        """
        Execute any SQL query and return results
        
        How it works:
        1. Connect to database
        2. Execute the SQL query
        3. Get results
        4. Save changes
        5. Close connection
        6. Return results
        """
        
        # Step 1: Connect
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Step 2: Execute query
        cursor.execute(query, params)
        
        # Step 3: Get results
        results = cursor.fetchall()
        
        # Step 4: Save changes
        conn.commit()
        
        # Step 5: Close connection
        conn.close()
        
        # Step 6: Return results
        return results