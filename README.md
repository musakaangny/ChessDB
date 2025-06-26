# CMPE 321 Project 3 - ChessDB Application

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip (Python package manager)

## Installation

1. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a MySQL database:

   ```bash
   mysql -u root -p
   CREATE DATABASE chessdb;
   EXIT;
   ```

4. Create a `.env` file in the project root with your database credentials:

   ```bash
   DB_NAME=chessdb
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. Set up the database tables:

   ```bash
   mysql -u root -p chessdb < sql/tables.sql
   mysql -u root -p chessdb < sql/constraints.sql
   mysql -u root -p chessdb < sql/triggers.sql
   ```

## Running the Application

1. Start the development server:

   ```bash
   python manage.py runserver
   ```

2. Access the application at: <http://127.0.0.1:8000/>
