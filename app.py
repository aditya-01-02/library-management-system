"""
APP.PY - Ultra Simple Gradio Interface

Improvements:
1. Horizontal layouts (side-by-side sections)
2. Minimal book/user lists (detailed info only when searched)
3. Book copies support (multiple copies for printed, unlimited for digital)

To run: python app.py
"""

import gradio as gr
from database import Database
from library_service import LibraryService

# Initialize the system
db = Database()
library = LibraryService(db)

# ==================== SIMPLE FUNCTIONS ====================

def add_book_function(isbn, title, author, genre, book_type, copies):
    """Add a book with number of copies (only for printed books)"""
    if not isbn or not title or not author or not genre:
        return "❌ Please fill all fields!"
    
    # Digital books don't need copies - set to unlimited (999)
    if book_type == "Digital":
        copies = 999  # Unlimited for digital
        success, message = library.add_book(isbn, title, author, genre, book_type, copies)
        return message.replace("999 copies", "digital copy (unlimited)")
    
    # Printed books need at least 1 copy
    if copies < 1:
        return "❌ Number of copies must be at least 1!"
    
    success, message = library.add_book(isbn, title, author, genre, book_type, copies)
    return message


def register_user_function(user_id, name, membership):
    """Register a user"""
    if not user_id or not name:
        return "❌ Please fill all fields!"
    
    success, message = library.add_user(user_id, name, membership)
    return message


def borrow_book_function(user_id, isbn):
    """Borrow a book"""
    if not user_id or not isbn:
        return "❌ Please enter User ID and ISBN!"
    
    success, message = library.borrow_book(user_id, isbn)
    return message


def return_book_function(user_id, isbn):
    """Return a book"""
    if not user_id or not isbn:
        return "❌ Please enter User ID and ISBN!"
    
    success, message = library.return_book(user_id, isbn)
    return message


def show_all_books_minimal():
    """Show MINIMAL list of books"""
    books = library.get_all_books_summary()
    
    if not books:
        return "📚 No books in library yet!"
    
    output = "📚 ALL BOOKS (Summary)\n"
    output += "=" * 70 + "\n\n"
    
    for book in books:
        output += f"• {book['Title']} by {book['Author']}\n"
        output += f"  ISBN: {book['ISBN']} | {book['Availability']}\n\n"
    
    return output


def show_book_details_function(isbn):
    """Show DETAILED book information"""
    if not isbn:
        return "❌ Please enter ISBN!"
    
    details, error = library.get_book_details(isbn)
    
    if error:
        return f"❌ {error}"
    
    output = f"📖 BOOK DETAILS\n"
    output += "=" * 70 + "\n\n"
    output += f"Title: {details['Title']}\n"
    output += f"Author: {details['Author']}\n"
    output += f"ISBN: {details['ISBN']}\n"
    output += f"Genre: {details['Genre']}\n"
    output += f"Type: {details['Type']}\n"
    
    # Show copies info differently for Digital vs Printed
    if details['Type'] == 'Digital':
        output += f"Availability: Unlimited (Digital)\n"
        output += f"Currently Borrowed: {details['Borrowed Copies']}\n"
    else:
        output += f"Total Copies: {details['Total Copies']}\n"
        output += f"Available Copies: {details['Available Copies']}\n"
        output += f"Borrowed Copies: {details['Borrowed Copies']}\n"
    
    output += f"Total Times Borrowed: {details['Total Borrows']}\n"
    output += f"Status: {details['Status']}\n"
    
    return output


def show_all_users_minimal():
    """Show MINIMAL list of users"""
    users = library.get_all_users_summary()
    
    if not users:
        return "👥 No users registered yet!"
    
    output = "👥 ALL USERS (Summary)\n"
    output += "=" * 70 + "\n\n"
    
    for user in users:
        output += f"• {user['Name']} (ID: {user['User ID']})\n"
        output += f"  Membership: {user['Membership']}\n\n"
    
    return output


def show_user_details_function(user_id):
    """Show DETAILED user information"""
    if not user_id:
        return "❌ Please enter User ID!"
    
    details, error = library.get_user_details(user_id)
    
    if error:
        return f"❌ {error}"
    
    output = f"👤 USER DETAILS\n"
    output += "=" * 70 + "\n\n"
    output += f"Name: {details['Name']}\n"
    output += f"User ID: {details['User ID']}\n"
    output += f"Membership: {details['Membership']}\n"
    output += f"Max Books Allowed: {details['Max Books Allowed']}\n"
    output += f"Borrow Period: {details['Borrow Period']}\n"
    output += f"Books Currently Borrowed: {details['Books Currently Borrowed']}\n"
    output += f"Outstanding Fines: {details['Outstanding Fines']}\n"
    output += f"Can Borrow: {details['Can Borrow']}\n"
    
    return output


def show_borrowed_books_function(user_id):
    """Show borrowed books for a user"""
    if not user_id:
        return "❌ Please enter User ID!"
    
    books = library.get_borrowed_books(user_id)
    
    if not books:
        return f"📖 User {user_id} has no borrowed books."
    
    output = f"📖 BORROWED BOOKS (User: {user_id})\n"
    output += "=" * 70 + "\n\n"
    
    for book in books:
        output += f"• {book['Title']} by {book['Author']}\n"
        output += f"  ISBN: {book['ISBN']}\n"
        output += f"  Days Borrowed: {book['Days Borrowed']}\n"
        output += f"  {book['Status']}\n\n"
    
    return output


def show_statistics_function():
    """Show library statistics"""
    stats = library.get_stats()
    
    output = "📊 LIBRARY STATISTICS\n"
    output += "=" * 70 + "\n\n"
    output += f"📚 Total Books: {stats['total_books']}\n"
    output += f"👥 Total Users: {stats['total_users']}\n"
    output += f"📖 Books Borrowed: {stats['books_borrowed']}\n"
    output += f"💰 Total Fines: ${stats['total_fines']:.2f}\n\n"
    
    popular = library.get_popular_books(5)
    
    output += "🔥 MOST POPULAR BOOKS\n"
    output += "-" * 70 + "\n"
    
    if popular:
        count = 1
        for title, author, borrows in popular:
            output += f"{count}. {title} by {author} ({borrows} borrows)\n"
            count = count + 1
    else:
        output += "No books borrowed yet\n"
    
    return output


def search_books_function(search_text):
    """Search for books"""
    if not search_text:
        return "❌ Please enter a search term!"
    
    results = library.search_books(search_text)
    
    if not results:
        return f"🔍 No books found for '{search_text}'"
    
    output = f"🔍 SEARCH RESULTS for '{search_text}'\n"
    output += "=" * 70 + "\n\n"
    
    for book in results:
        isbn = book[0]
        title = book[1]
        author = book[2]
        book_type = book[4]
        total = book[5]
        available = book[6]
        
        # Different status for Digital vs Printed
        if book_type == "Digital":
            status = "✅ Unlimited (Digital)"
        elif available > 0:
            status = f"✅ {available}/{total} available"
        else:
            status = "❌ All borrowed"
        
        output += f"• {title} by {author}\n"
        output += f"  ISBN: {isbn} | {status}\n\n"
    
    return output


# ==================== GRADIO INTERFACE ====================

app = gr.Blocks(title="Library System", theme=gr.themes.Soft())

with app:
    # Title
    gr.Markdown("# 📚 Library Management System")
    gr.Markdown("### Manage books, users, and borrowing easily!")
    
    # Create tabs
    with gr.Tabs():
        
        # ========== TAB 1: BOOKS ==========
        with gr.Tab("📖 Books"):
            
            # HORIZONTAL LAYOUT: Add Book & Book Details side by side
            with gr.Row():
                # Left Column: Add Book
                with gr.Column():
                    gr.Markdown("## ➕ Add New Book")
                    
                    add_isbn = gr.Textbox(label="ISBN", placeholder="001")
                    add_title = gr.Textbox(label="Title", placeholder="Harry Potter")
                    add_author = gr.Textbox(label="Author", placeholder="J.K. Rowling")
                    add_genre = gr.Textbox(label="Genre", placeholder="Fiction")
                    add_type = gr.Radio(["Digital", "Printed"], label="Type", value="Printed")
                    add_copies = gr.Number(
                        label="Number of Copies (for Printed books only)", 
                        value=1, 
                        minimum=1,
                        info="Digital books have unlimited copies"
                    )
                    
                    add_btn = gr.Button("➕ Add Book", variant="primary")
                    add_output = gr.Textbox(label="Result", lines=2)
                    
                    add_btn.click(
                        add_book_function,
                        [add_isbn, add_title, add_author, add_genre, add_type, add_copies],
                        add_output
                    )
                
                # Right Column: Book Details
                with gr.Column():
                    gr.Markdown("## 📖 Get Book Details")
                    gr.Markdown("*Enter ISBN to see full information about a book*")
                    
                    detail_isbn = gr.Textbox(label="Book ISBN", placeholder="001")
                    detail_btn = gr.Button("🔍 Get Details", variant="secondary")
                    detail_output = gr.Textbox(label="Book Details", lines=12)
                    
                    detail_btn.click(
                        show_book_details_function,
                        detail_isbn,
                        detail_output
                    )
            
            gr.Markdown("---")
            
            # HORIZONTAL LAYOUT: View All & Search side by side
            with gr.Row():
                # Left: View All Books (Minimal)
                with gr.Column():
                    gr.Markdown("## 📚 All Books (Quick View)")
                    
                    view_books_btn = gr.Button("Show All Books")
                    view_books_output = gr.Textbox(label="Books Summary", lines=10)
                    
                    view_books_btn.click(show_all_books_minimal, outputs=view_books_output)
                
                # Right: Search Books
                with gr.Column():
                    gr.Markdown("## 🔍 Search Books")
                    
                    search_input = gr.Textbox(label="Search by Title or Author", placeholder="Harry")
                    search_btn = gr.Button("Search")
                    search_output = gr.Textbox(label="Search Results", lines=10)
                    
                    search_btn.click(search_books_function, search_input, search_output)
        
        # ========== TAB 2: USERS ==========
        with gr.Tab("👥 Users"):
            
            # HORIZONTAL LAYOUT: Register User & User Details side by side
            with gr.Row():
                # Left Column: Register User
                with gr.Column():
                    gr.Markdown("## ➕ Register New User")
                    
                    reg_user_id = gr.Textbox(label="User ID", placeholder="U001")
                    reg_name = gr.Textbox(label="Name", placeholder="John Doe")
                    reg_membership = gr.Radio(
                        ["Basic", "Premium", "VIP"],
                        label="Membership",
                        value="Basic"
                    )
                    
                    gr.Markdown("**Membership Benefits:**")
                    gr.Markdown("• Basic: 3 books, 14 days")
                    gr.Markdown("• Premium: 5 books, 21 days")
                    gr.Markdown("• VIP: 10 books, 30 days")
                    
                    reg_btn = gr.Button("➕ Register User", variant="primary")
                    reg_output = gr.Textbox(label="Result", lines=2)
                    
                    reg_btn.click(
                        register_user_function,
                        [reg_user_id, reg_name, reg_membership],
                        reg_output
                    )
                
                # Right Column: User Details
                with gr.Column():
                    gr.Markdown("## 👤 Get User Details")
                    gr.Markdown("*Enter User ID to see full information*")
                    
                    user_detail_id = gr.Textbox(label="User ID", placeholder="U001")
                    user_detail_btn = gr.Button("🔍 Get Details", variant="secondary")
                    user_detail_output = gr.Textbox(label="User Details", lines=12)
                    
                    user_detail_btn.click(
                        show_user_details_function,
                        user_detail_id,
                        user_detail_output
                    )
            
            gr.Markdown("---")
            
            # View All Users (Minimal)
            gr.Markdown("## 👥 All Users (Quick View)")
            
            view_users_btn = gr.Button("Show All Users")
            view_users_output = gr.Textbox(label="Users Summary", lines=10)
            
            view_users_btn.click(show_all_users_minimal, outputs=view_users_output)
        
        # ========== TAB 3: BORROW & RETURN ==========
        with gr.Tab("📚 Borrow & Return"):
            
            # HORIZONTAL LAYOUT: Borrow & Return side by side
            with gr.Row():
                # Left: Borrow
                with gr.Column():
                    gr.Markdown("## 📤 Borrow Book")
                    
                    borrow_user = gr.Textbox(label="Your User ID", placeholder="U001")
                    borrow_isbn = gr.Textbox(label="Book ISBN", placeholder="001")
                    borrow_btn = gr.Button("📤 Borrow", variant="primary", size="lg")
                    borrow_output = gr.Textbox(label="Result", lines=3)
                    
                    borrow_btn.click(
                        borrow_book_function,
                        [borrow_user, borrow_isbn],
                        borrow_output
                    )
                
                # Right: Return
                with gr.Column():
                    gr.Markdown("## 📥 Return Book")
                    
                    return_user = gr.Textbox(label="Your User ID", placeholder="U001")
                    return_isbn = gr.Textbox(label="Book ISBN", placeholder="001")
                    return_btn = gr.Button("📥 Return", variant="primary", size="lg")
                    return_output = gr.Textbox(label="Result", lines=3)
                    
                    return_btn.click(
                        return_book_function,
                        [return_user, return_isbn],
                        return_output
                    )
            
            gr.Markdown("---")
            gr.Markdown("## 📋 My Borrowed Books")
            
            borrowed_user = gr.Textbox(label="Your User ID", placeholder="U001")
            borrowed_btn = gr.Button("📖 Show My Books")
            borrowed_output = gr.Textbox(label="Borrowed Books", lines=10)
            
            borrowed_btn.click(
                show_borrowed_books_function,
                borrowed_user,
                borrowed_output
            )
        
        # ========== TAB 4: STATISTICS ==========
        with gr.Tab("📊 Statistics"):
            gr.Markdown("## 📊 Library Statistics")
            gr.Markdown("*View overall library statistics and popular books*")
            
            stats_btn = gr.Button("📊 View Statistics", variant="primary", size="lg")
            stats_output = gr.Textbox(label="Statistics", lines=20)
            
            stats_btn.click(show_statistics_function, outputs=stats_output)

# ==================== LAUNCH ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 STARTING LIBRARY MANAGEMENT SYSTEM")
    print("="*70)
    print("✅ Database ready")
    print("✅ Library service ready")
    print("✅ Gradio interface loading...")
    print("\n📌 New Features:")
    print("   • Book copies support (add multiple copies)")
    print("   • Digital books = unlimited copies")
    print("   • Horizontal layouts (side-by-side)")
    print("   • Minimal lists (details only when searched)")
    print("\n📱 Opening browser...\n")
    
    app.launch()