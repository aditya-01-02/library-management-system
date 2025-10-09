# 📚 Library Management System

A simple yet powerful Library Management System built with Python, Gradio, and SQLite.
It supports managing books (digital & printed), user registration, borrowing & returning, fines, and statistics; all via an easy-to-use web interface powered by Gradio.

## ✨ Features

* Books Management
  * Add new books (Printed or Digital) with copies
  * Search by title or author
  * View quick summaries or detailed book info

* User Management
  * Register new users (Basic, Premium, VIP)
  * View user details and membership limits
  * Borrow & Return
  * Borrow/return books with copy tracking
  * Automatic fine calculation for overdue returns

* Statistics Dashboard
  * Total books, users, and borrowed books
  * Outstanding fines
  * Most popular books

## 📂 Project Structure
| File                     | Description                                                                    |
| ------------------------ | ------------------------------------------------------------------------------ |
| **`app.py`**             | 🎨 Gradio-based user interface (UI layer)                                      |
| **`database.py`**        | 🗄️ Database manager (SQLite) creates tables and runs queries                |
| **`library_service.py`** | 🧠 Application logic (core library operations: add, borrow, return, fines, stats) |
| **`models.py`**          | 📝 Data models (Book & User classes, membership rules)                         |

## 🛠️ Tech Stack
* Python (3.8+)

* Libraries:
  * gradio (UI)
  * sqlite3 (database)

* Structure/Design:
  * app.py → UI layer
  * library_service.py → Application logic
  * database.py → Data persistence
  * models.py → Data structure definitions

## 🚀 Getting Started
1️⃣ Clone the Repository
<pre>git clone https://github.com/aditya-01-02/library-management-system.git
cd library-management-system</pre>

2️⃣ Install Dependencies
<pre>pip install gradio
(sqlite3 is included with Python by default)</pre>

3️⃣ Run the Application
<pre>python app.py</pre>

This will:
1. Initialize the database (library.db)
2. Start the Gradio interface
3. Open the app in your browser

## 📊 Example Screens
* Add Book & View Details
* Register User & View Details
* Borrow/Return with status updates
* Statistics Dashboard with most popular books

🎯 Skills Demonstrated
* Backend: database design, queries, application logic
* Frontend/UI: interactive interface with Gradio
* Data Modeling: classes for books & users with rules
* Software Architecture: separation of concerns (UI, logic, DB, models)
* Problem Solving: managing copies, fines, borrow limits
