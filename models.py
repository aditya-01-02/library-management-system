"""
MODELS.PY - Book and User Classes

This file defines the structure of:
1. Book - what information a book has
2. User - what information a user has

How to explain: "These are like blueprints or templates.
They define what properties a Book or User should have."
"""

class Book:
    """
    Represents a book in the library
    
    Properties:
    - isbn: Unique identifier (like a barcode)
    - title: Name of the book
    - author: Who wrote it
    - genre: Category (Fiction, Science, etc.)
    - type: Digital or Printed
    - available: Can it be borrowed? (True/False)
    - borrow_count: How many times it's been borrowed
    """
    
    def __init__(self, isbn, title, author, genre, book_type):
        """Create a new book with given information"""
        
        # Basic book information
        self.isbn = isbn              
        self.title = title            
        self.author = author          
        self.genre = genre            
        self.type = book_type         
        
        # Status information
        self.available = True         # New books are available
        self.borrow_count = 0         # Not borrowed yet


class User:
    """
    Represents a library member
    
    Properties:
    - user_id: Unique identifier
    - name: User's name
    - membership: Basic, Premium, or VIP
    - fines: Money owed for late returns
    
    Membership Rules:
    - Basic: Borrow 3 books for 14 days
    - Premium: Borrow 5 books for 21 days
    - VIP: Borrow 10 books for 30 days
    """
    
    # Membership rules: (max_books, max_days)
    RULES = {
        "Basic": (3, 14),      
        "Premium": (5, 21),    
        "VIP": (10, 30)        
    }
    
    def __init__(self, user_id, name, membership="Basic"):
        """Create a new user with given information"""
        
        # Basic user information
        self.user_id = user_id        
        self.name = name              
        self.membership = membership  
        self.fines = 0.0             # No fines initially
    
    def max_books(self):
        """
        Returns maximum books this user can borrow
        
        Example: Basic user can borrow 3 books
        """
        max_books_allowed = self.RULES[self.membership][0]
        return max_books_allowed
    
    def max_days(self):
        """
        Returns how many days user can keep books
        
        Example: Basic user can keep books for 14 days
        """
        max_days_allowed = self.RULES[self.membership][1]
        return max_days_allowed