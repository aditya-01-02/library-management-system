"""
APP.PY - Super Simple Gradio Interface

How to run: python app.py

Explanation: This file creates the web interface using Gradio.
It connects buttons to functions from library_service.py
"""

import gradio as gr
from database import Database
from library_service import LibraryService

# Setup
db = Database()
library = LibraryService(db)

# ==================== UI FUNCTIONS (Simple Wrappers) ====================

def add_book(isbn, title, author, genre, book_type, copies):
    """Add book - handles digital (unlimited) vs printed (specified copies)"""
    if not all([isbn, title, author, genre]):
        return "❌ Fill all fields!"
    
    # Digital books = unlimited (ignore copy count)
    if book_type == "Digital":
        copies = 999
        _, msg = library.add_book(isbn, title, author, genre, book_type, copies)
        return msg.replace("999 copies", "digital copy (unlimited)")
    
    # Printed books = need at least 1 copy
    if copies < 1:
        return "❌ At least 1 copy needed!"
    
    _, msg = library.add_book(isbn, title, author, genre, book_type, copies)
    return msg

def register_user(user_id, name, membership):
    """Register new user"""
    if not user_id or not name:
        return "❌ Fill all fields!"
    _, msg = library.add_user(user_id, name, membership)
    return msg

def borrow(user_id, isbn):
    """Borrow a book"""
    if not user_id or not isbn:
        return "❌ Enter User ID and ISBN!"
    _, msg = library.borrow_book(user_id, isbn)
    return msg

def return_book(user_id, isbn):
    """Return a book"""
    if not user_id or not isbn:
        return "❌ Enter User ID and ISBN!"
    _, msg = library.return_book(user_id, isbn)
    return msg

def format_books():
    """Show all books (minimal)"""
    books = library.get_all_books_summary()
    if not books:
        return "📚 No books yet!"
    
    result = "📚 ALL BOOKS\n" + "="*70 + "\n\n"
    for b in books:
        result += f"• {b['Title']} by {b['Author']}\n"
        result += f"  ISBN: {b['ISBN']} | {b['Availability']}\n\n"
    return result

def book_details(isbn):
    """Show detailed book info"""
    if not isbn:
        return "❌ Enter ISBN!"
    
    details, error = library.get_book_details(isbn)
    if error:
        return f"❌ {error}"
    
    result = f"📖 {details['Title']}\n" + "="*70 + "\n\n"
    result += f"Author: {details['Author']}\n"
    result += f"ISBN: {details['ISBN']}\n"
    result += f"Genre: {details['Genre']}\n"
    result += f"Type: {details['Type']}\n"
    
    if details['Type'] == 'Digital':
        result += f"Availability: Unlimited (Digital)\n"
        result += f"Borrowed: {details['Borrowed Copies']} users\n"
    else:
        result += f"Total Copies: {details['Total Copies']}\n"
        result += f"Available: {details['Available Copies']}\n"
        result += f"Borrowed: {details['Borrowed Copies']}\n"
    
    result += f"Total Borrows: {details['Total Borrows']}\n"
    return result

def format_users():
    """Show all users (minimal)"""
    users = library.get_all_users_summary()
    if not users:
        return "👥 No users yet!"
    
    result = "👥 ALL USERS\n" + "="*70 + "\n\n"
    for u in users:
        result += f"• {u['Name']} (ID: {u['User ID']})\n"
        result += f"  Membership: {u['Membership']}\n\n"
    return result

def user_details(user_id):
    """Show detailed user info"""
    if not user_id:
        return "❌ Enter User ID!"
    
    details, error = library.get_user_details(user_id)
    if error:
        return f"❌ {error}"
    
    result = f"👤 {details['Name']}\n" + "="*70 + "\n\n"
    result += f"User ID: {details['User ID']}\n"
    result += f"Membership: {details['Membership']}\n"
    result += f"Max Books: {details['Max Books Allowed']}\n"
    result += f"Borrow Period: {details['Borrow Period']}\n"
    result += f"Currently Borrowed: {details['Books Currently Borrowed']}\n"
    result += f"Fines: {details['Outstanding Fines']}\n"
    result += f"Can Borrow: {details['Can Borrow']}\n"
    return result

def borrowed_books(user_id):
    """Show user's borrowed books"""
    if not user_id:
        return "❌ Enter User ID!"
    
    books = library.get_borrowed_books(user_id)
    if not books:
        return f"📖 No borrowed books"
    
    result = f"📖 BORROWED (User: {user_id})\n" + "="*70 + "\n\n"
    for b in books:
        result += f"• {b['Title']} by {b['Author']}\n"
        result += f"  ISBN: {b['ISBN']} | Days: {b['Days Borrowed']}\n"
        result += f"  {b['Status']}\n\n"
    return result

def stats():
    """Show statistics"""
    s = library.get_stats()
    popular = library.get_popular_books(5)
    
    result = "📊 STATISTICS\n" + "="*70 + "\n\n"
    result += f"📚 Total Books: {s['total_books']}\n"
    result += f"👥 Total Users: {s['total_users']}\n"
    result += f"📖 Borrowed: {s['books_borrowed']}\n"
    result += f"💰 Fines: ${s['total_fines']:.2f}\n\n"
    result += "🔥 POPULAR BOOKS\n" + "-"*70 + "\n"
    
    if popular:
        for i, (title, author, count) in enumerate(popular, 1):
            result += f"{i}. {title} by {author} ({count})\n"
    else:
        result += "No borrows yet\n"
    
    return result

def search(text):
    """Search books"""
    if not text:
        return "❌ Enter search term!"
    
    results = library.search_books(text)
    if not results:
        return f"🔍 No books found"
    
    result = f"🔍 SEARCH: '{text}'\n" + "="*70 + "\n\n"
    for r in results:
        isbn, title, author, _, book_type, total, available = r[0:7]
        
        if book_type == "Digital":
            status = "✅ Unlimited"
        elif available > 0:
            status = f"✅ {available}/{total}"
        else:
            status = "❌ All borrowed"
        
        result += f"• {title} by {author}\n"
        result += f"  ISBN: {isbn} | {status}\n\n"
    
    return result

# ==================== GRADIO UI ====================

with gr.Blocks(title="Library System", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("# 📚 Library Management System")
    
    with gr.Tabs():
        
        # TAB 1: BOOKS
        with gr.Tab("📖 Books"):
            with gr.Row():
                # Add Book
                with gr.Column():
                    gr.Markdown("### ➕ Add Book")
                    isbn_in = gr.Textbox(label="ISBN", placeholder="001")
                    title_in = gr.Textbox(label="Title", placeholder="Harry Potter")
                    author_in = gr.Textbox(label="Author", placeholder="J.K. Rowling")
                    genre_in = gr.Textbox(label="Genre", placeholder="Fiction")
                    type_in = gr.Radio(["Digital", "Printed"], label="Type", value="Printed")
                    copies_in = gr.Number(label="Copies (Printed only)", value=1, minimum=1)
                    add_btn = gr.Button("➕ Add", variant="primary")
                    add_out = gr.Textbox(label="Result")
                    
                    add_btn.click(add_book, [isbn_in, title_in, author_in, genre_in, type_in, copies_in], add_out)
                
                # Book Details
                with gr.Column():
                    gr.Markdown("### 📖 Book Details")
                    detail_isbn = gr.Textbox(label="ISBN", placeholder="001")
                    detail_btn = gr.Button("🔍 Get Details")
                    detail_out = gr.Textbox(label="Details", lines=10)
                    
                    detail_btn.click(book_details, detail_isbn, detail_out)
            
            gr.Markdown("---")
            
            with gr.Row():
                # View All
                with gr.Column():
                    gr.Markdown("### 📚 All Books")
                    view_btn = gr.Button("Show All")
                    view_out = gr.Textbox(label="Books", lines=10)
                    view_btn.click(format_books, outputs=view_out)
                
                # Search
                with gr.Column():
                    gr.Markdown("### 🔍 Search")
                    search_in = gr.Textbox(label="Search", placeholder="Harry")
                    search_btn = gr.Button("Search")
                    search_out = gr.Textbox(label="Results", lines=10)
                    search_btn.click(search, search_in, search_out)
        
        # TAB 2: USERS
        with gr.Tab("👥 Users"):
            with gr.Row():
                # Register
                with gr.Column():
                    gr.Markdown("### ➕ Register User")
                    uid_in = gr.Textbox(label="User ID", placeholder="U001")
                    name_in = gr.Textbox(label="Name", placeholder="John Doe")
                    mem_in = gr.Radio(["Basic", "Premium", "VIP"], label="Membership", value="Basic")
                    gr.Markdown("*Basic: 3 books, 14 days | Premium: 5, 21 | VIP: 10, 30*")
                    reg_btn = gr.Button("➕ Register", variant="primary")
                    reg_out = gr.Textbox(label="Result")
                    
                    reg_btn.click(register_user, [uid_in, name_in, mem_in], reg_out)
                
                # User Details
                with gr.Column():
                    gr.Markdown("### 👤 User Details")
                    user_detail_id = gr.Textbox(label="User ID", placeholder="U001")
                    user_detail_btn = gr.Button("🔍 Get Details")
                    user_detail_out = gr.Textbox(label="Details", lines=10)
                    
                    user_detail_btn.click(user_details, user_detail_id, user_detail_out)
            
            gr.Markdown("---")
            gr.Markdown("### 👥 All Users")
            users_btn = gr.Button("Show All")
            users_out = gr.Textbox(label="Users", lines=10)
            users_btn.click(format_users, outputs=users_out)
        
        # TAB 3: BORROW & RETURN
        with gr.Tab("📚 Borrow & Return"):
            with gr.Row():
                # Borrow
                with gr.Column():
                    gr.Markdown("### 📤 Borrow")
                    b_user = gr.Textbox(label="User ID", placeholder="U001")
                    b_isbn = gr.Textbox(label="ISBN", placeholder="001")
                    b_btn = gr.Button("📤 Borrow", variant="primary")
                    b_out = gr.Textbox(label="Result")
                    
                    b_btn.click(borrow, [b_user, b_isbn], b_out)
                
                # Return
                with gr.Column():
                    gr.Markdown("### 📥 Return")
                    r_user = gr.Textbox(label="User ID", placeholder="U001")
                    r_isbn = gr.Textbox(label="ISBN", placeholder="001")
                    r_btn = gr.Button("📥 Return", variant="primary")
                    r_out = gr.Textbox(label="Result")
                    
                    r_btn.click(return_book, [r_user, r_isbn], r_out)
            
            gr.Markdown("---")
            gr.Markdown("### 📋 My Books")
            my_user = gr.Textbox(label="User ID", placeholder="U001")
            my_btn = gr.Button("📖 Show My Books")
            my_out = gr.Textbox(label="Borrowed", lines=10)
            my_btn.click(borrowed_books, my_user, my_out)
        
        # TAB 4: STATISTICS
        with gr.Tab("📊 Stats"):
            gr.Markdown("### 📊 Statistics")
            stats_btn = gr.Button("📊 View Stats", variant="primary")
            stats_out = gr.Textbox(label="Statistics", lines=15)
            stats_btn.click(stats, outputs=stats_out)

# ==================== LAUNCH ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 LIBRARY SYSTEM STARTING")
    print("="*70)
    print("✅ Ready!")
    print("📱 Opening browser...\n")
    app.launch()