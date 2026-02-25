"""
LIBRARY_SERVICE.PY - Main Library Operations

This file does all the library operations:
- Add books and users
- Borrow and return books
- Calculate fines
- Get statistics
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
        Add a new book to the library
        Returns: Message string (always)
        """
        
        # STEP 1: Check if ISBN already exists
        check_query = 'SELECT isbn FROM books WHERE isbn=?'
        existing = self.db.run_query(check_query, (isbn,))
        
        # STEP 2: Return error if duplicate
        if existing:
            return "X This ISBN already exists!"
        
        # STEP 3: Add book to database
        add_query = 'INSERT INTO books VALUES (?,?,?,?,?,?,?,?)'
        self.db.run_query(add_query, (isbn, title, author, genre, book_type, copies, copies, 0))
        
        # STEP 4: Return success message
        return f" Added {copies} copies of '{title}' successfully!"
    
    
    def get_all_books_summary(self):
        """
        Get list of all books with basic info
        Returns: List of dictionaries (always)
        """
        
        # STEP 1: Get all books from database
        query = 'SELECT isbn, title, author, available_copies, total_copies, type FROM books'
        rows = self.db.run_query(query)
        
        # STEP 2: Return empty list if no books
        if not rows:
            return []
        
        # STEP 3: Format each book
        book_list = []
        for row in rows:
            isbn, title, author, available, total, book_type = row
            
            # Determine availability status
            if book_type == "Digital":
                status = " Unlimited (Digital)"
            elif available > 0:
                status = f" {available}/{total} available"
            else:
                status = "X All borrowed"
            
            # Create book dictionary
            book_dict = {
                'ISBN': isbn,
                'Title': title,
                'Author': author,
                'Availability': status
            }
            book_list.append(book_dict)
        
        # STEP 4: Return list
        return book_list
    
    
    def get_book_details(self, isbn):
        """
        Get detailed information about a specific book
        Returns: Message string with details or error (always)
        """
        
        # STEP 1: Query book from database
        query = 'SELECT * FROM books WHERE isbn=?'
        result = self.db.run_query(query, (isbn,))
        
        # STEP 2: Return error if not found
        if not result:
            return "X Book not found!"
        
        # STEP 3: Extract book data
        isbn, title, author, genre, book_type, total_copies, available_copies, borrow_count = result[0]
        
        # STEP 4: Format detailed information
        details = f" {title}\n" + "="*70 + "\n\n"
        details += f"Author: {author}\n"
        details += f"ISBN: {isbn}\n"
        details += f"Genre: {genre}\n"
        details += f"Type: {book_type}\n"
        
        if book_type == 'Digital':
            details += f"Availability: Unlimited (Digital)\n"
            details += f"Borrowed: {borrow_count} times\n"
        else:
            details += f"Total Copies: {total_copies}\n"
            details += f"Available: {available_copies}\n"
            details += f"Borrowed: {total_copies - available_copies}\n"
        
        details += f"Total Borrows: {borrow_count}\n"
        
        # STEP 5: Return formatted string
        return details
    
    
    def search_books(self, search_text):
        """
        Search books by title or author
        Returns: List of tuples (always)
        """
        
        # STEP 1: Create search query with LIKE
        query = 'SELECT * FROM books WHERE title LIKE ? OR author LIKE ?'
        search_pattern = f'%{search_text}%'
        
        # STEP 2: Execute and return results
        results = self.db.run_query(query, (search_pattern, search_pattern))
        return results
    
    # ==================== USER OPERATIONS ====================
    
    def add_user(self, user_id, name, membership):
        """
        Register a new user
        Returns: Message string (always)
        """
        
        # STEP 1: Check if user ID already exists
        check_query = 'SELECT user_id FROM users WHERE user_id=?'
        existing = self.db.run_query(check_query, (user_id,))
        
        # STEP 2: Return error if duplicate
        if existing:
            return "X This User ID already exists!"
        
        # STEP 3: Add user to database
        add_query = 'INSERT INTO users VALUES (?,?,?,?)'
        self.db.run_query(add_query, (user_id, name, membership, 0.0))
        
        # STEP 4: Return success message
        return f" User '{name}' registered successfully!"
    
    
    def get_all_users_summary(self):
        """
        Get list of all users with basic info
        Returns: List of dictionaries (always)
        """
        
        # STEP 1: Get all users from database
        query = 'SELECT user_id, name, membership FROM users'
        rows = self.db.run_query(query)
        
        # STEP 2: Return empty list if no users
        if not rows:
            return []
        
        # STEP 3: Format each user
        user_list = []
        for row in rows:
            user_id, name, membership = row
            
            user_dict = {
                'User ID': user_id,
                'Name': name,
                'Membership': membership
            }
            user_list.append(user_dict)
        
        # STEP 4: Return list
        return user_list
    
    
    def get_user_details(self, user_id):
        """
        Get detailed information about a specific user
        Returns: Message string with details or error (always)
        """
        
        # STEP 1: Query user from database
        query = 'SELECT * FROM users WHERE user_id=?'
        result = self.db.run_query(query, (user_id,))
        
        # STEP 2: Return error if not found
        if not result:
            return "X User not found!"
        
        # STEP 3: Extract user data
        user_id, name, membership, fines = result[0]
        
        # STEP 4: Create User object to get limits
        user = User(user_id, name, membership)
        user.fines = fines
        
        # STEP 5: Count borrowed books
        count_query = 'SELECT COUNT(*) FROM borrowed WHERE user_id=?'
        borrowed_count = self.db.run_query(count_query, (user_id,))[0][0]
        
        # STEP 6: Format detailed information
        details = f"👤 {name}\n" + "="*70 + "\n\n"
        details += f"User ID: {user_id}\n"
        details += f"Membership: {membership}\n"
        details += f"Max Books Allowed: {user.max_books()}\n"
        details += f"Borrow Period: {user.max_days()} days\n"
        details += f"Currently Borrowed: {borrowed_count}\n"
        details += f"Outstanding Fines: ${fines:.2f}\n"
        details += f"Can Borrow: {'Yes' if fines <= 10 else 'No (Pay fines first)'}\n"
        
        # STEP 7: Return formatted string
        return details
    
    
    def get_user(self, user_id):
        """
        Get User object (for internal use)
        Returns: User object or None
        """
        
        # STEP 1: Query user from database
        query = 'SELECT * FROM users WHERE user_id=?'
        result = self.db.run_query(query, (user_id,))
        
        # STEP 2: Return None if not found
        if not result:
            return None
        
        # STEP 3: Unpack data directly
        user_id, name, membership, fines = result[0]
        
        # STEP 4: Create and return User object
        user = User(user_id, name, membership)
        user.fines = fines
        return user
    
    # ==================== BORROW/RETURN OPERATIONS ====================
    
    def borrow_book(self, user_id, isbn):
        """
        User borrows a book (SIMPLIFIED - broken into helpers)
        Returns: Message string (always)
        """
        
        # STEP 1: Check if user can borrow
        error = self._check_user_can_borrow(user_id)
        if error:
            return error
        
        # STEP 2: Check if book is available
        title, error = self._check_book_available(isbn)
        if error:
            return error
        
        # STEP 3: Process the borrow
        self._process_borrow(user_id, isbn)
        
        # STEP 4: Return success message
        return f" Successfully borrowed '{title}'! 📚"
    
    
    def _check_user_can_borrow(self, user_id):
        """
        Helper: Check if user is allowed to borrow
        Returns: Error message or None
        """
        
        # Get user
        user = self.get_user(user_id)
        if not user:
            return "X User not found!"
        
        # Check fines
        if user.fines > 10:
            return f"X Please pay fines first: ${user.fines:.2f}"
        
        # Check borrow limit
        count_query = 'SELECT COUNT(*) FROM borrowed WHERE user_id=?'
        borrowed_count = self.db.run_query(count_query, (user_id,))[0][0]
        
        if borrowed_count >= user.max_books():
            return f"X Limit reached! You can borrow {user.max_books()} books max"
        
        return None  # No error
    
    
    def _check_book_available(self, isbn):
        """
        Helper: Check if book exists and has available copies
        Returns: (title, error_message) - error is None if OK
        """
        
        # Get book info
        book_query = 'SELECT title, available_copies FROM books WHERE isbn=?'
        book_result = self.db.run_query(book_query, (isbn,))
        
        # Check if book exists
        if not book_result:
            return None, " X Book not found!"
        
        # Extract data
        title, available_copies = book_result[0]
        
        # Check if copies available
        if available_copies <= 0:
            return None, f" X All copies of '{title}' are currently borrowed"
        
        return title, None  # Return title, no error
    
    
    def _process_borrow(self, user_id, isbn):
        """
        Helper: Actually process the borrow (update database)
        Returns: Nothing
        """
        
        # Decrease available copies and increase borrow count
        update_query = 'UPDATE books SET available_copies=available_copies-1, borrow_count=borrow_count+1 WHERE isbn=?'
        self.db.run_query(update_query, (isbn,))
        
        # Record the borrow with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        record_query = 'INSERT INTO borrowed VALUES (?,?,?)'
        self.db.run_query(record_query, (user_id, isbn, today))
    
    
    def return_book(self, user_id, isbn):
        """
        User returns a book (SIMPLIFIED - broken into helpers)
        Returns: Message string (always)
        """
        
        # STEP 1: Check if user has this book
        borrow_date_str, error = self._check_user_has_book(user_id, isbn)
        if error:
            return error
        
        # STEP 2: Get book title
        title = self._get_book_title(isbn)
        
        # STEP 3: Calculate if overdue and get fine
        fine_message = self._calculate_return_fine(user_id, borrow_date_str)
        
        # STEP 4: Process the return (remove from borrowed, add copy back)
        self._process_return(user_id, isbn)
        
        # STEP 5: Return success message (with fine if applicable)
        return f" Returned '{title}'{fine_message}"
    
    
    def _check_user_has_book(self, user_id, isbn):
        """
        Helper: Check if user borrowed this book
        Returns: (borrow_date, error_message) - error is None if OK
        """
        
        # Check if borrowed
        check_query = 'SELECT borrow_date FROM borrowed WHERE user_id=? AND isbn=?'
        result = self.db.run_query(check_query, (user_id, isbn))
        
        if not result:
            return None, "❌ You didn't borrow this book!"
        
        borrow_date_str = result[0][0]
        return borrow_date_str, None  # Return date, no error
    
    
    def _get_book_title(self, isbn):
        """
        Helper: Get book title
        Returns: Title string
        """
        
        title_query = 'SELECT title FROM books WHERE isbn=?'
        title = self.db.run_query(title_query, (isbn,))[0][0]
        return title
    
    
    def _calculate_return_fine(self, user_id, borrow_date_str):
        """
        Helper: Calculate fine if book is overdue
        Returns: Fine message string (empty if no fine)
        """
        
        # Calculate days borrowed
        borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d')
        today = datetime.now()
        days_borrowed = (today - borrow_date).days
        
        # Get user's allowed days
        user = self.get_user(user_id)
        allowed_days = user.max_days()
        
        # Calculate overdue days
        overdue_days = days_borrowed - allowed_days
        
        # If not overdue, return empty string
        if overdue_days <= 0:
            return ""
        
        # Calculate fine
        fine = overdue_days * self.FINE_PER_DAY
        
        # Add fine to user's account
        fine_query = 'UPDATE users SET fines=fines+? WHERE user_id=?'
        self.db.run_query(fine_query, (fine, user_id))
        
        # Return fine message
        return f"\n⚠️ Late by {overdue_days} days. Fine: ${fine:.2f}"
    
    
    def _process_return(self, user_id, isbn):
        """
        Helper: Process the return (update database)
        Returns: Nothing
        """
        
        # Remove from borrowed table
        delete_query = 'DELETE FROM borrowed WHERE user_id=? AND isbn=? LIMIT 1'
        self.db.run_query(delete_query, (user_id, isbn))
        
        # Increase available copies
        update_query = 'UPDATE books SET available_copies=available_copies+1 WHERE isbn=?'
        self.db.run_query(update_query, (isbn,))
    
    
    def get_borrowed_books(self, user_id):
        """
        Get books borrowed by a user (SIMPLIFIED - no JOIN)
        Returns: List of dictionaries (always)
        """
        
        # STEP 1: Get borrowed ISBNs and dates
        query = 'SELECT isbn, borrow_date FROM borrowed WHERE user_id=?'
        borrowed_records = self.db.run_query(query, (user_id,))
        
        # STEP 2: Return empty list if nothing borrowed
        if not borrowed_records:
            return []
        
        # STEP 3: Get user object
        user = self.get_user(user_id)
        if not user:
            return []
        
        # STEP 4: For each borrowed book, get details
        borrowed_list = []
        for isbn, borrow_date_str in borrowed_records:
            
            # Get book title and author
            book_query = 'SELECT title, author FROM books WHERE isbn=?'
            book_info = self.db.run_query(book_query, (isbn,))
            title, author = book_info[0]
            
            # Calculate days borrowed
            borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d')
            days_borrowed = (datetime.now() - borrow_date).days
            days_remaining = user.max_days() - days_borrowed
            
            # Determine status
            if days_remaining >= 0:
                status = f"✅ Due in {days_remaining} days"
            else:
                status = f"⚠️ Overdue by {-days_remaining} days"
            
            # Add to list
            borrowed_list.append({
                'ISBN': isbn,
                'Title': title,
                'Author': author,
                'Days Borrowed': days_borrowed,
                'Status': status
            })
        
        # STEP 5: Return list
        return borrowed_list
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_stats(self):
        """
        Get library statistics
        Returns: Dictionary (always)
        """
        
        # STEP 1: Count total books
        query1 = 'SELECT COUNT(*) FROM books'
        total_books = self.db.run_query(query1)[0][0]
        
        # STEP 2: Count total users
        query2 = 'SELECT COUNT(*) FROM users'
        total_users = self.db.run_query(query2)[0][0]
        
        # STEP 3: Count borrowed books
        query3 = 'SELECT COUNT(*) FROM borrowed'
        books_borrowed = self.db.run_query(query3)[0][0]
        
        # STEP 4: Sum all fines
        query4 = 'SELECT SUM(fines) FROM users'
        fines_result = self.db.run_query(query4)[0][0]
        total_fines = fines_result if fines_result else 0
        
        # STEP 5: Return dictionary
        return {
            'total_books': total_books,
            'total_users': total_users,
            'books_borrowed': books_borrowed,
            'total_fines': total_fines
        }
    
    
    def get_popular_books(self, limit=5):
        """
        Get most borrowed books
        Returns: List of tuples (always)
        """
        
        # Query books ordered by popularity
        query = '''
            SELECT title, author, borrow_count 
            FROM books 
            ORDER BY borrow_count DESC 
            LIMIT ?
        '''
        
        return self.db.run_query(query, (limit,))