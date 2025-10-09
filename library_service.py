"""
LIBRARY_SERVICE.PY - The Brain of the System

This file does all the library operations:
- Add books and users
- Borrow and return books (with copy management)
- Calculate fines
- Get statistics

How to explain: "This is the business logic layer. 
It takes requests from the UI, validates them, 
updates the database, and returns results."
"""

from datetime import datetime
from models import User

class LibraryService:
    """Handles all library operations"""
    
    # Fine amount per day for late returns
    FINE_PER_DAY = 0.50
    
    def __init__(self, database):
        """Initialize with database connection"""
        self.db = database
    
    # ==================== BOOK OPERATIONS ====================
    
    def add_book(self, isbn, title, author, genre, book_type, copies):
        """
        Add a new book to the library with number of copies
        
        Steps:
        1. Check if ISBN already exists
        2. If yes, return error
        3. If no, add book to database with copies
        4. Return success message
        """
        
        # Step 1: Check if book exists
        check_query = 'SELECT isbn FROM books WHERE isbn=?'
        existing = self.db.run_query(check_query, (isbn,))
        
        # Step 2: If exists, return error
        if existing:
            return False, "This ISBN already exists!"
        
        # Step 3: Add book to database
        # Both total_copies and available_copies are set to the same value initially
        add_query = 'INSERT INTO books VALUES (?,?,?,?,?,?,?,?)'
        self.db.run_query(add_query, (isbn, title, author, genre, book_type, copies, copies, 0))
        
        # Step 4: Return success
        return True, f"Added {copies} copies of '{title}' successfully!"
    
    
    def get_all_books_summary(self):
        """
        Get MINIMAL list of all books (just title, author, availability)
        
        Steps:
        1. Query all books from database
        2. For each book, show only basic info
        3. Return list
        """
        
        # Step 1: Get all books
        query = 'SELECT isbn, title, author, available_copies, total_copies, type FROM books'
        rows = self.db.run_query(query)
        
        # Step 2: Format each book (minimal info)
        book_list = []
        
        for row in rows:
            isbn = row[0]
            title = row[1]
            author = row[2]
            available = row[3]
            total = row[4]
            book_type = row[5]
            
            # Different status for Digital vs Printed
            if book_type == "Digital":
                status = "✅ Unlimited (Digital)"
            elif available > 0:
                status = f"✅ {available}/{total} available"
            else:
                status = "❌ All borrowed"
            
            # Minimal dictionary
            book_dict = {
                'ISBN': isbn,
                'Title': title,
                'Author': author,
                'Availability': status
            }
            
            book_list.append(book_dict)
        
        return book_list
    
    
    def get_book_details(self, isbn):
        """
        Get DETAILED information about a specific book
        
        Steps:
        1. Query book from database
        2. If not found, return error
        3. Format all detailed information
        4. Return complete details
        """
        
        # Step 1: Query book
        query = 'SELECT * FROM books WHERE isbn=?'
        result = self.db.run_query(query, (isbn,))
        
        # Step 2: Check if found
        if not result:
            return None, "Book not found!"
        
        # Step 3: Extract all data
        row = result[0]
        isbn = row[0]
        title = row[1]
        author = row[2]
        genre = row[3]
        book_type = row[4]
        total_copies = row[5]
        available_copies = row[6]
        borrow_count = row[7]
        
        # Step 4: Format detailed info
        details = {
            'ISBN': isbn,
            'Title': title,
            'Author': author,
            'Genre': genre,
            'Type': book_type,
            'Total Copies': total_copies,
            'Available Copies': available_copies,
            'Borrowed Copies': total_copies - available_copies,
            'Total Borrows': borrow_count,
            'Status': 'Available' if available_copies > 0 else 'All borrowed'
        }
        
        return details, None
    
    
    def search_books(self, search_text):
        """
        Search books by title or author
        
        Steps:
        1. Create search query with LIKE
        2. Execute query
        3. Return results
        """
        
        # Step 1: Create query
        query = 'SELECT * FROM books WHERE title LIKE ? OR author LIKE ?'
        search_pattern = f'%{search_text}%'
        
        # Step 2: Execute
        results = self.db.run_query(query, (search_pattern, search_pattern))
        
        # Step 3: Return
        return results
    
    # ==================== USER OPERATIONS ====================
    
    def add_user(self, user_id, name, membership):
        """
        Register a new user
        
        Steps:
        1. Check if user ID already exists
        2. If yes, return error
        3. If no, add user to database
        4. Return success message
        """
        
        # Step 1: Check if user exists
        check_query = 'SELECT user_id FROM users WHERE user_id=?'
        existing = self.db.run_query(check_query, (user_id,))
        
        # Step 2: If exists, return error
        if existing:
            return False, "This User ID already exists!"
        
        # Step 3: Add user to database
        add_query = 'INSERT INTO users VALUES (?,?,?,?)'
        self.db.run_query(add_query, (user_id, name, membership, 0.0))
        
        # Step 4: Return success
        return True, f"User '{name}' registered successfully!"
    
    
    def get_all_users_summary(self):
        """
        Get MINIMAL list of all users (just name, ID, membership)
        
        Steps:
        1. Query all users from database
        2. For each user, show only basic info
        3. Return list
        """
        
        # Step 1: Get all users
        query = 'SELECT user_id, name, membership FROM users'
        rows = self.db.run_query(query)
        
        # Step 2: Format each user (minimal info)
        user_list = []
        
        for row in rows:
            user_id = row[0]
            name = row[1]
            membership = row[2]
            
            # Minimal dictionary
            user_dict = {
                'User ID': user_id,
                'Name': name,
                'Membership': membership
            }
            
            user_list.append(user_dict)
        
        return user_list
    
    
    def get_user_details(self, user_id):
        """
        Get DETAILED information about a specific user
        
        Steps:
        1. Query user from database
        2. If not found, return error
        3. Count borrowed books
        4. Format all detailed information
        5. Return complete details
        """
        
        # Step 1: Query user
        query = 'SELECT * FROM users WHERE user_id=?'
        result = self.db.run_query(query, (user_id,))
        
        # Step 2: Check if found
        if not result:
            return None, "User not found!"
        
        # Step 3: Extract data
        row = result[0]
        user_id = row[0]
        name = row[1]
        membership = row[2]
        fines = row[3]
        
        # Create User object to get limits
        user = User(user_id, name, membership)
        user.fines = fines
        
        # Step 4: Count borrowed books
        count_query = 'SELECT COUNT(*) FROM borrowed WHERE user_id=?'
        borrowed_count = self.db.run_query(count_query, (user_id,))[0][0]
        
        # Step 5: Format detailed info
        details = {
            'User ID': user_id,
            'Name': name,
            'Membership': membership,
            'Max Books Allowed': user.max_books(),
            'Borrow Period': f"{user.max_days()} days",
            'Books Currently Borrowed': borrowed_count,
            'Outstanding Fines': f"${fines:.2f}",
            'Can Borrow': 'Yes' if fines <= 10 else 'No (Pay fines first)'
        }
        
        return details, None
    
    
    def get_user(self, user_id):
        """
        Get user object (for internal use)
        
        Steps:
        1. Query user from database
        2. If not found, return None
        3. Create User object
        4. Set fines
        5. Return user object
        """
        
        # Step 1: Query user
        query = 'SELECT * FROM users WHERE user_id=?'
        result = self.db.run_query(query, (user_id,))
        
        # Step 2: Check if found
        if not result:
            return None
        
        # Step 3: Extract data
        user_id = result[0][0]
        name = result[0][1]
        membership = result[0][2]
        fines = result[0][3]
        
        # Step 4: Create User object
        user = User(user_id, name, membership)
        user.fines = fines
        
        # Step 5: Return
        return user
    
    # ==================== BORROW/RETURN OPERATIONS ====================
    
    def borrow_book(self, user_id, isbn):
        """
        User borrows a book (decreases available_copies by 1)
        
        Steps:
        1. Get user details
        2. Check if user has too many fines
        3. Check if user reached borrow limit
        4. Check if book exists and has available copies
        5. Decrease available_copies by 1
        6. Record the borrow
        7. Increase borrow_count
        8. Return success message
        """
        
        # Step 1: Get user
        user = self.get_user(user_id)
        if not user:
            return False, "User not found!"
        
        # Step 2: Check fines
        if user.fines > 10:
            return False, f"Please pay fines first: ${user.fines:.2f}"
        
        # Step 3: Check borrow limit
        count_query = 'SELECT COUNT(*) FROM borrowed WHERE user_id=?'
        borrowed_count = self.db.run_query(count_query, (user_id,))[0][0]
        
        if borrowed_count >= user.max_books():
            max_allowed = user.max_books()
            return False, f"Limit reached! You can borrow {max_allowed} books max"
        
        # Step 4: Check if book exists and has available copies
        book_query = 'SELECT title, available_copies FROM books WHERE isbn=?'
        book_result = self.db.run_query(book_query, (isbn,))
        
        if not book_result:
            return False, "Book not found!"
        
        title = book_result[0][0]
        available_copies = book_result[0][1]
        
        if available_copies <= 0:
            return False, f"All copies of '{title}' are currently borrowed"
        
        # Step 5: Decrease available_copies by 1
        update_query = 'UPDATE books SET available_copies=available_copies-1, borrow_count=borrow_count+1 WHERE isbn=?'
        self.db.run_query(update_query, (isbn,))
        
        # Step 6: Record the borrow
        today = datetime.now().strftime('%Y-%m-%d')
        record_query = 'INSERT INTO borrowed VALUES (?,?,?)'
        self.db.run_query(record_query, (user_id, isbn, today))
        
        # Step 7: Return success
        return True, f"Successfully borrowed '{title}'! 📚"
    
    
    def return_book(self, user_id, isbn):
        """
        User returns a book (increases available_copies by 1)
        
        Steps:
        1. Check if user borrowed this book
        2. Calculate how many days it was borrowed
        3. Get user's allowed days
        4. Calculate if overdue
        5. Remove from borrowed records
        6. Increase available_copies by 1
        7. If overdue, add fine
        8. Return message
        """
        
        # Step 1: Check if borrowed
        check_query = 'SELECT borrow_date FROM borrowed WHERE user_id=? AND isbn=?'
        result = self.db.run_query(check_query, (user_id, isbn))
        
        if not result:
            return False, "You didn't borrow this book!"
        
        # Step 2: Calculate days borrowed
        borrow_date_str = result[0][0]
        borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d')
        today = datetime.now()
        days_borrowed = (today - borrow_date).days
        
        # Step 3: Get user's allowed days
        user = self.get_user(user_id)
        allowed_days = user.max_days()
        
        # Step 4: Calculate overdue
        overdue_days = days_borrowed - allowed_days
        
        # Step 5: Get book title
        title_query = 'SELECT title FROM books WHERE isbn=?'
        title = self.db.run_query(title_query, (isbn,))[0][0]
        
        # Step 6: Remove from borrowed
        delete_query = 'DELETE FROM borrowed WHERE user_id=? AND isbn=? LIMIT 1'
        self.db.run_query(delete_query, (user_id, isbn))
        
        # Step 7: Increase available_copies by 1
        update_query = 'UPDATE books SET available_copies=available_copies+1 WHERE isbn=?'
        self.db.run_query(update_query, (isbn,))
        
        # Step 8: Calculate fine if overdue
        message = f"Returned '{title}' ✅"
        
        if overdue_days > 0:
            fine = overdue_days * self.FINE_PER_DAY
            fine_query = 'UPDATE users SET fines=fines+? WHERE user_id=?'
            self.db.run_query(fine_query, (fine, user_id))
            message = message + f"\n⚠️ Late by {overdue_days} days. Fine: ${fine:.2f}"
        
        # Step 9: Return message
        return True, message
    
    
    def get_borrowed_books(self, user_id):
        """
        Get books borrowed by a user
        
        Steps:
        1. Query borrowed books with book details (JOIN)
        2. Get user to check allowed days
        3. For each book, calculate status
        4. Format into dictionary
        5. Return list
        """
        
        # Step 1: Query with JOIN to get book details
        query = '''
            SELECT b.isbn, b.title, b.author, br.borrow_date
            FROM borrowed br
            JOIN books b ON br.isbn = b.isbn
            WHERE br.user_id = ?
        '''
        rows = self.db.run_query(query, (user_id,))
        
        # Step 2: Get user
        user = self.get_user(user_id)
        if not user:
            return []
        
        # Step 3 & 4: Format each book
        borrowed_list = []
        
        for row in rows:
            # Extract data
            isbn = row[0]
            title = row[1]
            author = row[2]
            borrow_date_str = row[3]
            
            # Calculate days
            borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d')
            days_borrowed = (datetime.now() - borrow_date).days
            days_remaining = user.max_days() - days_borrowed
            
            # Determine status
            if days_remaining >= 0:
                status = f"✅ Due in {days_remaining} days"
            else:
                status = f"⚠️ Overdue by {-days_remaining} days"
            
            # Create dictionary
            book_dict = {
                'ISBN': isbn,
                'Title': title,
                'Author': author,
                'Days Borrowed': days_borrowed,
                'Status': status
            }
            
            # Add to list
            borrowed_list.append(book_dict)
        
        # Step 5: Return list
        return borrowed_list
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_stats(self):
        """
        Get library statistics
        
        Steps:
        1. Count total books
        2. Count total users
        3. Count borrowed books
        4. Sum all fines
        5. Return as dictionary
        """
        
        # Step 1: Count books
        query1 = 'SELECT COUNT(*) FROM books'
        total_books = self.db.run_query(query1)[0][0]
        
        # Step 2: Count users
        query2 = 'SELECT COUNT(*) FROM users'
        total_users = self.db.run_query(query2)[0][0]
        
        # Step 3: Count borrowed
        query3 = 'SELECT COUNT(*) FROM borrowed'
        books_borrowed = self.db.run_query(query3)[0][0]
        
        # Step 4: Sum fines
        query4 = 'SELECT SUM(fines) FROM users'
        fines_result = self.db.run_query(query4)[0][0]
        
        # Handle null result
        if fines_result:
            total_fines = fines_result
        else:
            total_fines = 0
        
        # Step 5: Create dictionary
        stats = {
            'total_books': total_books,
            'total_users': total_users,
            'books_borrowed': books_borrowed,
            'total_fines': total_fines
        }
        
        # Step 6: Return
        return stats
    
    
    def get_popular_books(self, limit=5):
        """
        Get most borrowed books
        
        Steps:
        1. Query books ordered by borrow count
        2. Limit results
        3. Return list
        """
        
        # Step 1 & 2: Query with ORDER BY and LIMIT
        query = '''
            SELECT title, author, borrow_count 
            FROM books 
            ORDER BY borrow_count DESC 
            LIMIT ?
        '''
        
        # Step 3: Return results
        return self.db.run_query(query, (limit,))