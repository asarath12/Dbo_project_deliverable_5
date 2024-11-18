import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, host, user, password, database):
        # Initialize the connection to the MySQL database
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                print("Connected to the database.")
        except Error as e:
            # If there's an error while connecting, print the error and set connection to None
            print(f"Error connecting to database: {e}")
            self.connection = None

    def create_record(self, table):
        # Method to insert a new record into the specified table
        if table == "accident":
            severity = input("Enter severity: ")
            date = input("Enter date (YYYY-MM-DD): ")
            time = input("Enter time (HH:MM:SS): ")
            vehicle_id = int(input("Enter vehicle ID (must exist in vehicle table): "))
            road_id = int(input("Enter road ID (must exist in road table): "))
            query = "INSERT INTO accident (Severity, Date, Time, VehicleID, RoadID) VALUES (%s, %s, %s, %s, %s);"
            params = (severity, date, time, vehicle_id, road_id)
        elif table == "address":
            # Collect data for the 'address' table
            user_id = int(input("Enter user ID (must exist in user table): "))
            pincode = input("Enter pincode: ")
            state = input("Enter state: ")
            country = input("Enter country: ")
            query = "INSERT INTO address (UserID, Pincode, State, Country) VALUES (%s, %s, %s, %s);"
            params = (user_id, pincode, state, country)
        # Similar data collection and insertion for other tables
        elif table == "camera":
            status = input("Enter status: ")
            last_inspection = input("Enter last inspection date (YYYY-MM-DD): ")
            query = "INSERT INTO camera (Status, LastInspection) VALUES (%s, %s);"
            params = (status, last_inspection)
        elif table == "phonenumber":
            user_id = int(input("Enter user ID (must exist in user table): "))
            phone_number = input("Enter phone number: ")
            query = "INSERT INTO phonenumber (UserID, PhoneNumber) VALUES (%s, %s);"
            params = (user_id, phone_number)
        elif table == "road":
            road_name = input("Enter road name: ")
            road_type = input("Enter road type: ")
            num_lanes = int(input("Enter number of lanes: "))
            query = "INSERT INTO road (RoadName, RoadType, NumLanes) VALUES (%s, %s, %s);"
            params = (road_name, road_type, num_lanes)
        elif table == "roadcamera":
            road_id = int(input("Enter road ID (must exist in road table): "))
            camera_id = int(input("Enter camera ID (must exist in camera table): "))
            query = "INSERT INTO roadcamera (RoadID, CameraID) VALUES (%s, %s);"
            params = (road_id, camera_id)
        elif table == "user":
            user_id = input("Enter user id: ")
            user_name = input("Enter user name: ")
            user_role = input("Enter user role: ")
            query = "INSERT INTO user (UserID, UserName, UserRole) VALUES (%s, %s, %s);"
            params = (user_id, user_name, user_role)
        elif table == "vehicle":
            license_plate = input("Enter license plate: ")
            vehicle_type = input("Enter vehicle type: ")
            owner_name = input("Enter owner name: ")
            query = "INSERT INTO vehicle (LicensePlate, VehicleType, OwnerName) VALUES (%s, %s, %s);"
            params = (license_plate, vehicle_type, owner_name)
        elif table == "vehicleviolation":
            vehicle_id = int(input("Enter vehicle ID (must exist in vehicle table): "))
            violation_id = int(input("Enter violation ID (must exist in violation table): "))
            query = "INSERT INTO vehicleviolation (VehicleID, ViolationID) VALUES (%s, %s);"
            params = (vehicle_id, violation_id)
        elif table == "violation":
            violation_type = input("Enter violation type: ")
            fine_amount = float(input("Enter fine amount: "))
            query = "INSERT INTO violation (ViolationType, FineAmount) VALUES (%s, %s);"
            params = (violation_type, fine_amount)

        try:
            # Execute the query and commit the transaction
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print(f"Record created successfully in {table}.")
        except Error as e:
            # Handle any errors during insertion
            print(f"Error inserting record into {table}: {e}")
        finally:
            cursor.close()


    def read_record(self, table):
        # Method to read and display all records from a specified table
        query = f"SELECT * FROM {table};"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()

            if records:
                # Display records if found
                print(f"\nContents of the '{table}' table:")
                for record in records:
                    print(record)
            else:
                print(f"\nNo records found in the '{table}' table.")

        except Error as e:
            # Handle any errors during reading
            print(f"Error reading records from {table}: {e}")
        finally:
            cursor.close()

    def get_columns(self, table):
        """Fetches column names for the selected table."""
        query = f"SHOW COLUMNS FROM {table};"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = cursor.fetchall()
            # Return the column names
            return [col[0] for col in columns]
        except Error as e:
            # Handle any errors during column fetching
            print(f"Error fetching columns from {table}: {e}")
            return []
        finally:
            cursor.close()

    def update_record(self, table):
        # Method to update a record in the specified table
        primary_keys = {
            "accident": "AccidentID",
            "address": "AddressID",
            "camera": "CameraID",
            "phonenumber": "PhoneID",
            "road": "RoadID",
            "roadcamera": ("RoadID", "CameraID"),
            "user": "UserID",
            "vehicle": "VehicleID",
            "vehicleviolation": ("VehicleID", "ViolationID"),
            "violation": "ViolationID"
        }

        primary_key = primary_keys.get(table)
        
        if isinstance(primary_key, tuple):
            # For tables with composite primary keys, collect all keys
            key_values = {}
            for key in primary_key:
                key_values[key] = input(f"Enter {key} of the record you want to update: ")
        else:
            # For tables with a single primary key
            record_id = input(f"Enter {primary_key} of the record you want to update: ")

        columns = self.get_columns(table)
        if not columns:
            print(f"Could not retrieve columns for the table {table}.")
            return

        # Display columns and allow user to select one for updating
        print("\nSelect the column to update:")
        for i, column in enumerate(columns, 1):
            print(f"{i}. {column}")

        column_choice = int(input("Enter column number: "))
        if 1 <= column_choice <= len(columns):
            column_name = columns[column_choice - 1]
            new_value = input(f"Enter the new value for {column_name}: ")
        else:
            print("Invalid column choice. Please try again.")
            return

        # Construct the update query
        if isinstance(primary_key, tuple):
            where_clause = " AND ".join([f"{key} = %s" for key in primary_key])
            query = f"UPDATE {table} SET {column_name} = %s WHERE {where_clause};"
            params = [new_value] + list(key_values.values())
        else:
            query = f"UPDATE {table} SET {column_name} = %s WHERE {primary_key} = %s;"
            params = (new_value, record_id)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"Record updated successfully in {table}.")
            else:
                print("No matching record found or no update was made.")
        except Error as e:
            print(f"Error updating record in {table}: {e}")
        finally:
            cursor.close()

    def delete_record(self, table):
        # Method to delete a record from the specified table
        primary_keys = {
            "accident": "AccidentID",
            "address": "AddressID",
            "camera": "CameraID",
            "phonenumber": "PhoneID",
            "road": "RoadID",
            "roadcamera": ("RoadID", "CameraID"),
            "user": "UserID",
            "vehicle": "VehicleID",
            "vehicleviolation": ("VehicleID", "ViolationID"),
            "violation": "ViolationID"
        }

        # Get the primary key(s) for the specified table
        primary_key = primary_keys.get(table)
        
        if isinstance(primary_key, tuple):
            # For tables with composite primary keys, collect values for all keys
            key_values = {}
            for key in primary_key:
                key_values[key] = input(f"Enter {key} of the record you want to delete: ")
        else:
            # For tables with a single primary key
            record_id = input(f"Enter {primary_key} of the record you want to delete: ")

        # Construct the DELETE query
        if isinstance(primary_key, tuple):
            # For composite keys, create a WHERE clause with multiple conditions
            where_clause = " AND ".join([f"{key} = %s" for key in primary_key])
            query = f"DELETE FROM {table} WHERE {where_clause};"
            params = list(key_values.values())
        else:
            # For single keys, create a simple WHERE clause
            query = f"DELETE FROM {table} WHERE {primary_key} = %s;"
            params = (record_id,)

        try:
            # Execute the DELETE query and commit changes
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"Record deleted successfully from {table}.")
            else:
                print("No matching record found.")
        except Error as e:
            # Handle any errors during deletion
            print(f"Error deleting record from {table}: {e}")
        finally:
            cursor.close()
            
    def set_operations_query(self):
        query = """
            (SELECT VehicleID FROM accident)
            UNION
            (SELECT VehicleID FROM vehicleviolation)
            EXCEPT
            (SELECT VehicleID FROM accident
             INTERSECT
             SELECT VehicleID FROM vehicleviolation);
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Vehicles involved in either accidents or violations, but not both:")
            for result in results:
                print(result)
        except Error as e:
            print(f"Error executing set operations query: {e}")
        finally:
            cursor.close()
            
    def set_membership_query(self):
        vehicle_id = int(input("Enter Vehicle ID to check membership: "))
        query = """
            SELECT CASE 
                WHEN EXISTS (SELECT 1 FROM accident WHERE VehicleID = %s) AND 
                     EXISTS (SELECT 1 FROM vehicleviolation WHERE VehicleID = %s)
                THEN 'Yes'
                ELSE 'No'
            END AS InBothTables;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (vehicle_id, vehicle_id))
            result = cursor.fetchone()
            print(f"Is vehicle ID {vehicle_id} in both accident and vehicleviolation tables? {result[0]}")
        except Error as e:
            print(f"Error executing set membership query: {e}")
        finally:
            cursor.close()
            
    def set_comparison_query(self):
        query = """
            SELECT ViolationType, AVG(FineAmount) AS AvgFine
            FROM violation
            GROUP BY ViolationType
            ORDER BY AvgFine DESC;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Average fine amount by violation type:")
            for result in results:
                print(f"ViolationType: {result[0]}, AvgFine: {result[1]}")
        except Error as e:
            print(f"Error executing set comparison query: {e}")
        finally:
            cursor.close()
            
    def subquery_with_clause(self):
        query = """
            WITH TotalFines AS (
                SELECT VehicleID, SUM(FineAmount) AS TotalFine
                FROM vehicleviolation
                JOIN violation ON vehicleviolation.ViolationID = violation.ViolationID
                GROUP BY VehicleID
            )
            SELECT VehicleID, TotalFine
            FROM TotalFines
            ORDER BY TotalFine DESC;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Total fines per vehicle:")
            for result in results:
                print(result)
        except Error as e:
            print(f"Error executing CTE query: {e}")
        finally:
            cursor.close()
            
    def advanced_aggregate_query(self):
        query = """
            SELECT Severity, COUNT(*) AS AccidentCount
            FROM accident
            GROUP BY Severity WITH ROLLUP;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Accident count by severity (including total):")
            for result in results:
                print(result)
        except Error as e:
            print(f"Error executing advanced aggregate query: {e}")
        finally:
            cursor.close()
            
    def olap_query(self):
        query = """
        SELECT vehicleviolation.VehicleID, vehicleviolation.ViolationID, violation.FineAmount,
               RANK() OVER (PARTITION BY vehicleviolation.VehicleID ORDER BY violation.FineAmount DESC) AS FineRank
        FROM vehicleviolation
        JOIN violation ON vehicleviolation.ViolationID = violation.ViolationID;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Fine rank per vehicle:")
            for result in results:
                print(result)
        except Error as e:
            print(f"Error executing OLAP query: {e}")
        finally:
            cursor.close()
            
    def close_connection(self):
        # Close the database connection if it is open
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

def main():
    # Instantiate the DatabaseManager with connection details
    db = DatabaseManager(host="localhost", user="root", password="password", database="grp4-deliverable5")

    # List of available tables
    tables = ["accident", "address", "camera", "phonenumber", "road", "roadcamera", 
              "user", "vehicle", "vehicleviolation", "violation"]
    
    while True:
        # Display the main menu
        print("\nMenu:")
        print("1. Create a new record")
        print("2. Read a record")
        print("3. Update a record")
        print("4. Delete a record")
        print("5. Complex Queries")
        print("6. Exit")

        # Get user choice
        choice = input("Enter your choice (1-6): ")

        if choice in ['1', '2', '3', '4']:
            # Display table options for the selected operation
            print("\nSelect a table:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            table_choice = int(input("Enter table number: "))

            # Validate the selected table choice
            if 1 <= table_choice <= len(tables):
                selected_table = tables[table_choice - 1]
                if choice == '1':
                    db.create_record(selected_table)
                elif choice == '2':
                    db.read_record(selected_table)
                elif choice == '3':
                    db.update_record(selected_table)
                elif choice == '4':
                    db.delete_record(selected_table)
            else:
                print("Invalid table choice. Please try again.")
        elif choice == '5':
            # Display the complex queries menu
            print("\nComplex Queries:")
            print("1. Set Operations")
            print("2. Set Membership")
            print("3. Set Comparison")
            print("4. Subquery with WITH Clause (CTE)")
            print("5. Advanced Aggregates (ROLLUP)")
            print("6. OLAP Query")

            # Get the user's choice for the complex query
            query_choice = input("Enter query choice (1-6): ")

            # Call the appropriate complex query based on user's choice
            if query_choice == '1':
                db.set_operations_query()
            elif query_choice == '2':
                db.set_membership_query()
            elif query_choice == '3':
                db.set_comparison_query()
            elif query_choice == '4':
                db.subquery_with_clause()
            elif query_choice == '5':
                db.advanced_aggregate_query()
            elif query_choice == '6':
                db.olap_query()
            else:
                print("Invalid query choice. Please try again.")
        elif choice == '6':
            # Exit the application and close the database connection
            db.close_connection()
            print("Exiting the application.")
            break
        else:
            # Handle invalid menu choices
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()