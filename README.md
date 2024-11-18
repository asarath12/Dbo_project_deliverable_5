# Road Traffic Management System 🚦

# Project Description 📄
The Road Traffic Management System is a web application designed to efficiently manage road traffic data, such as accidents, vehicle violations, and camera operations. It allows users to perform various database queries using complex SQL operations such as set operations, subqueries with WITH clauses, advanced aggregates, and OLAP queries. The system also provides a user-friendly interface for CRUD operations, and features robust error handling to ensure smooth user experience.

# Features ✨
- **Complex SQL Queries:**
  
  - **Set Operations:** Union, Intersect, Difference, Symmetric Difference.
  - **Subqueries with CTE:** Total fines, road accidents, user violations.
  - **Advanced Aggregate Queries:** Rollup, running totals, and averages.
  - **OLAP Queries:** Ranking, partitioning, and percentage contribution.
 
- **User-Friendly Interface**:

    - Intuitive navigation with dropdown menus and buttons.
    - Interactive query execution with real-time results display.
   
- **CRUD Operations**:

    - Create, View, Update, and Delete records in all tables
   
- **Error Handling**:
      
    - Provides meaningful error messages for invalid operations.
    - Ensures graceful degradation and prevents application crashes.
 
# **Technologies Used** 💻

- Backend: Flask (Python)
- Frontend: HTML, CSS, Bootstrap
- Database: MySQL
- Other Tools:
  - Loom for demonstration video
  - Git for version control
 
# Installation 🛠️

Follow these steps to set up and run the project on your local machine:

## Prerequisites:

- Python 3.8 or above
- MySQL server
- Required Python libraries (listed in requirements.txt)

## Steps to run the project

1. Clone the repository:

```bash
https://github.com/asarath12/Dbo_project_deliverable_5.git
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Update the database connection credentials in the code:

```bash
db = DatabaseManager(host="localhost", user="root", password="YourPassword", database="YourDatabase")
```
Ensure the database schema is set up with the required tables and relationships.

4. Run the application:

```bash
python .\run.py
```

5. Access the application at http://127.0.0.1:8000.

## How to Use 🚀

### Running Queries:

  - Navigate to the Complex Queries section.
  - Select a query type (e.g., Set Operations, Subquery with CTE, OLAP Queries) from the dropdown.
  - View and analyze the results on a new page.

### CRUD Operations: 

  - Use the Manage Records section to Create, View, Update, or Delete records.
  - Ensure proper IDs and values are provided for valid operations.

## Screenshots of website 📸

### Home Page 

![Home Page](images/home_page_1.png "Home Page")

![Home Page](images/home_page_2.png "Home Page")

![Home Page](images/home_page_3.png "Home Page")

# Demonstration 🎥

Watch the full functionality demonstration of the application on Loom: Loom Video Link
