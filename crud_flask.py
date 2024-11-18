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
            print(f"Error connecting to database: {e}")
            self.connection = None

    def create_record(self, table, data):
        """Insert a new record into the specified table, with data provided as a dictionary."""
        # Mapping of table-specific insert queries
        queries = {
            "accident": "INSERT INTO accident (Severity, Date, Time, VehicleID, RoadID) VALUES (%s, %s, %s, %s, %s);",
            "address": "INSERT INTO address (UserID, Pincode, State, Country) VALUES (%s, %s, %s, %s);",
            "camera": "INSERT INTO camera (Status, LastInspection) VALUES (%s, %s);",
            "phonenumber": "INSERT INTO phonenumber (UserID, PhoneNumber) VALUES (%s, %s);",
            "road": "INSERT INTO road (RoadName, RoadType, NumLanes) VALUES (%s, %s, %s);",
            "roadcamera": "INSERT INTO roadcamera (RoadID, CameraID) VALUES (%s, %s);",
            "user": "INSERT INTO user (UserID, UserName, UserRole) VALUES (%s, %s, %s);",
            "vehicle": "INSERT INTO vehicle (LicensePlate, VehicleType, OwnerName) VALUES (%s, %s, %s);",
            "vehicleviolation": "INSERT INTO vehicleviolation (VehicleID, ViolationID) VALUES (%s, %s);",
            "violation": "INSERT INTO violation (ViolationType, FineAmount) VALUES (%s, %s);"
        }

        query = queries.get(table)
        if not query:
            raise ValueError(f"Table '{table}' not supported for insert operations.")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            print(f"Record created successfully in {table}.")
            return True
        except Error as e:
            print(f"Error inserting record into {table}: {e}")
            return False
        finally:
            cursor.close()

    def read_record(self, table):
        """Fetch all records from a specified table and return as a list of dictionaries."""
        query = f"SELECT * FROM {table};"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            records = cursor.fetchall()  # List of dictionaries
            return records
            
        except Error as e:
            print(f"Error reading records from {table}: {e}")
            return []
        finally:
            cursor.close()

    def get_columns(self, table):
        """Fetch column names for the selected table and return as a list."""
        query = f"SHOW COLUMNS FROM {table};"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.fetchall()]
            return columns
        except Error as e:
            print(f"Error fetching columns from {table}: {e}")
            return []
        finally:
            cursor.close()
    
    def update_record(self, table, primary_key_values, update_data):
        """Update a record in the specified table based on primary key(s) and new data."""
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
        
        if not update_data:
            print("No data provided to update.")
            return False  # Early exit if there's no data to update

        # Determine WHERE clause and parameters for composite or single primary key
        if isinstance(primary_key, tuple):
            where_clause = " AND ".join([f"{key} = %s" for key in primary_key])
            params = list(update_data.values()) + list(primary_key_values)
        else:
            where_clause = f"{primary_key} = %s"
            params = list(update_data.values()) + [primary_key_values]

        # Construct SET clause from update_data keys
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"

        # Debugging output for troubleshooting
        print("Executing Query:", query)
        print("With Parameters:", params)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                print(f"Record updated successfully in {table}.")
                return True
            else:
                print("No matching record found or no update was made.")
                return False
        except Error as e:
            print(f"Error updating record in {table}: {e}")
            return False
        finally:
            cursor.close()


    def delete_record(self, table, primary_key_values):
        """Delete a record from the specified table based on primary key(s)."""
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
            where_clause = " AND ".join([f"{key} = %s" for key in primary_key])
            params = primary_key_values
        else:
            where_clause = f"{primary_key} = %s"
            params = [primary_key_values]

        query = f"DELETE FROM {table} WHERE {where_clause};"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting record from {table}: {e}")
            return False
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
            return results  # Return results instead of printing
        except Error as e:
            print(f"Error executing set operations query: {e}")
            return []
        finally:
            cursor.close()
            
    def set_membership_query(self, vehicle_id):
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
            return result[0] if result else "No"  # Return 'Yes' or 'No' for the web app
        except Error as e:
            print(f"Error executing set membership query: {e}")
            return "Error"
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
            return [{"ViolationType": row[0], "AvgFine": row[1]} for row in results]
        except Error as e:
            print(f"Error executing set comparison query: {e}")
            return []
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
            return [{"VehicleID": row[0], "TotalFine": row[1]} for row in results]
        except Error as e:
            print(f"Error executing CTE query: {e}")
            return []
        finally:
            cursor.close()
            
    def top_3_roads_with_most_accidents(self):
        """
        Find the top 3 roads with the most accidents using a WITH clause.
        """
        query = """
        WITH RoadAccidentCounts AS (
            SELECT r.RoadID, r.RoadName, COUNT(a.AccidentID) AS AccidentCount
            FROM road r
            JOIN accident a ON r.RoadID = a.RoadID
            GROUP BY r.RoadID, r.RoadName
        )
        SELECT RoadID, RoadName, AccidentCount
        FROM RoadAccidentCounts
        ORDER BY AccidentCount DESC
        LIMIT 3;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"RoadID": row[0], "RoadName": row[1], "AccidentCount": row[2]} for row in results]
        except Error as e:
            print(f"Error fetching top 3 roads with most accidents: {e}")
            return []
        finally:
            cursor.close()
            
    def users_and_vehicle_violations(self, min_fine=0):
        """
        Fetch users and their vehicle violations with filtering based on minimum fine amount.
        """
        query = f"""
        WITH UserViolations AS (
            SELECT 
                u.UserID, u.UserName, v.VehicleID, vi.ViolationType, vi.FineAmount
            FROM user u
            JOIN vehicle v ON u.UserID = v.VehicleID
            JOIN vehicleviolation vv ON v.VehicleID = vv.VehicleID
            JOIN violation vi ON vv.ViolationID = vi.ViolationID
            WHERE vi.FineAmount >= %s
        )
        SELECT UserID, UserName, VehicleID, ViolationType, FineAmount
        FROM UserViolations
        ORDER BY FineAmount DESC;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (min_fine,))
            results = cursor.fetchall()
            return [
                {
                    "UserID": row[0],
                    "UserName": row[1],
                    "VehicleID": row[2],
                    "ViolationType": row[3],
                    "FineAmount": row[4],
                }
                for row in results
            ]
        except Error as e:
            print(f"Error fetching users and their vehicle violations: {e}")
            return []
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
            return [{"Severity": row[0], "AccidentCount": row[1]} for row in results]
        except Error as e:
            print(f"Error executing advanced aggregate query: {e}")
            return []
        finally:
            cursor.close()
            
    def average_fine_per_violation_type(self):
        """
        Calculate the average fine amount per violation type.
        """
        query = """
        SELECT ViolationType, AVG(FineAmount) AS AverageFine
        FROM violation
        GROUP BY ViolationType
        ORDER BY AverageFine DESC;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"ViolationType": row[0], "AverageFine": row[1]} for row in results]
        except Error as e:
            print(f"Error calculating average fine per violation type: {e}")
            return []
        finally:
            cursor.close()
            
    def running_total_accidents_per_road(self):
        """
        Calculate the running total of accidents per road.
        """
        query = """
        SELECT 
            r.RoadName, 
            a.Date, 
            COUNT(a.AccidentID) AS DailyAccidents,
            SUM(COUNT(a.AccidentID)) OVER (PARTITION BY r.RoadID ORDER BY a.Date) AS RunningTotal
        FROM road r
        JOIN accident a ON r.RoadID = a.RoadID
        GROUP BY r.RoadID, r.RoadName, a.Date
        ORDER BY r.RoadName, a.Date;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [
                {
                    "RoadName": row[0],
                    "Date": row[1],
                    "DailyAccidents": row[2],
                    "RunningTotal": row[3]
                }
                for row in results
            ]
        except Error as e:
            print(f"Error calculating running total of accidents per road: {e}")
            return []
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
            return [{"VehicleID": row[0], "ViolationID": row[1], "FineAmount": row[2], "FineRank": row[3]} for row in results]
        except Error as e:
            print(f"Error executing OLAP query: {e}")
            return []
        finally:
            cursor.close()
            
    def percentage_contribution_of_accidents(self):
        """
        Fetch the percentage contribution of accidents per road.
        """
        query = """
        SELECT r.RoadName, COUNT(a.AccidentID) AS TotalAccidents,
               ROUND(100.0 * COUNT(a.AccidentID) / SUM(COUNT(a.AccidentID)) OVER (), 2) AS PercentageContribution
        FROM road r
        JOIN accident a ON r.RoadID = a.RoadID
        GROUP BY r.RoadID, r.RoadName;
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"RoadName": row["RoadName"], "TotalAccidents": row["TotalAccidents"],
                     "PercentageContribution": row["PercentageContribution"]} for row in results]
        except Error as e:
            print(f"Error executing percentage contribution query: {e}")
            return []
        finally:
            cursor.close()

    def partitioned_sum_of_fines(self):
        """
        Fetch the partitioned sum of fines for each violation type.
        """
        query = """
        SELECT ViolationType, FineAmount,
               SUM(FineAmount) OVER (PARTITION BY ViolationType) AS TotalFineByType
        FROM violation;
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"ViolationType": row["ViolationType"], "FineAmount": row["FineAmount"],
                     "TotalFineByType": row["TotalFineByType"]} for row in results]
        except Error as e:
            print(f"Error executing partitioned sum of fines query: {e}")
            return []
        finally:
            cursor.close()
            
    def get_total_accidents(self):
        """Fetch total accidents count."""
        query = "SELECT COUNT(*) FROM accident;"
        return self.fetch_single_value(query)

    def get_active_violations(self):
        query = "SELECT COUNT(*) FROM violation;"  # Remove 'status' condition if unnecessary
        return self.fetch_single_value(query)

    def get_operational_cameras(self):
        query = "SELECT COUNT(*) FROM camera;"  # Remove 'status' condition if unnecessary
        return self.fetch_single_value(query)

    # Helper methods for executing queries
    def fetch_single_value(self, query, params=None):
        """Fetch a single scalar value from the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """Fetch all rows for a query."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
            return []
        finally:
            cursor.close()
            
    def get_total_violations(self):
        query = "SELECT COUNT(*) FROM vehicleviolation;"
        return self.fetch_single_value(query)
    
    def get_total_vehicle_violations(self):
        query = "SELECT COUNT(*) AS count FROM vehicleviolation"
        return self.fetch_single_value(query)

    def get_monthly_accidents(self):
        query = """
        SELECT MONTHNAME(Date) AS month, COUNT(*) AS count 
        FROM accident 
        GROUP BY MONTHNAME(Date), MONTH(Date)
        ORDER BY MONTH(Date);
        """
        result = self.fetch_all(query)
        return result

    def get_violation_distribution(self):
        query = """
        SELECT ViolationType, COUNT(*) AS count 
        FROM violation 
        JOIN vehicleviolation ON violation.ViolationID = vehicleviolation.ViolationID 
        GROUP BY ViolationType
        """
        return self.fetch_all(query)
    
    def get_bubble_chart_data(self):
        query = """
        SELECT 
        road.RoadName AS road_name,
        accident.Severity AS severity,
        COUNT(*) AS accident_count
        FROM accident
        JOIN road ON accident.RoadID = road.RoadID
        GROUP BY road_name, severity
        ORDER BY road_name, severity;
        """
        
        # Mapping severity levels to numeric values
        severity_mapping = {
            "Low": 1,
            "Minor": 2,
            "Medium": 3,
            "High": 4,
            "Major": 5,
            "Fatal": 6
        }

        result = self.fetch_all(query)

        # Transform the result to match Chart.js expectations
        return [
            {
                "road_name": row["road_name"],  # Road name for the label
                "x": severity_mapping.get(row["severity"], 0),  # Map severity to numeric (default 0 if unknown)
                "y": row["accident_count"],  # Accident count on the y-axis
                "r": row["accident_count"] * 6  # Bubble size (scaled)
            }
            for row in result
        ]
    
    def union_query(self):
        """
        Fetch all VehicleIDs that are either involved in accidents or have violations.
        """
        query = """
        SELECT VehicleID FROM accident
        UNION
        SELECT VehicleID FROM vehicleviolation;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error executing UNION query: {e}")
            return []
        finally:
            cursor.close()

    def intersect_query(self):
        """
        Fetch all VehicleIDs that are involved in both accidents and violations.
        """
        query = """
        SELECT a.VehicleID
        FROM accident a
        INNER JOIN vehicleviolation vv ON a.VehicleID = vv.VehicleID;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error executing INTERSECT query: {e}")
            return []
        finally:
            cursor.close()

    def except_query(self):
        """
        Fetch all VehicleIDs that are involved in accidents but do not have violations.
        """
        query = """
        SELECT a.VehicleID
        FROM accident a
        LEFT JOIN vehicleviolation vv ON a.VehicleID = vv.VehicleID
        WHERE vv.VehicleID IS NULL;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error executing EXCEPT query: {e}")
            return []
        finally:
            cursor.close()

    def difference_query(self):
        """
        Fetch all VehicleIDs that are in violations but not in accidents.
        """
        query = """
        SELECT vv.VehicleID
        FROM vehicleviolation vv
        LEFT JOIN accident a ON vv.VehicleID = a.VehicleID
        WHERE a.VehicleID IS NULL;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error executing difference query: {e}")
            return []
        finally:
            cursor.close()
            
    def check_record_exists(self, table, record_id):
        """
        Check if a record exists in the specified table with the given primary key(s).
        """
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

        # Handle composite keys
        if isinstance(primary_key, tuple):
            where_clause = " AND ".join([f"{key} = %s" for key in primary_key])
            query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause};"
            params = record_id
        else:
            where_clause = f"{primary_key} = %s"
            query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause};"
            params = [record_id]

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result[0] > 0  # Returns True if count > 0
        except Error as e:
            print(f"Error checking record existence in {table}: {e}")
            return False
        finally:
            cursor.close()

    def symmetric_difference_query(self):
        """
        Fetch all VehicleIDs that are in either accidents or violations, but not both.
        """
        query = """
        (SELECT VehicleID FROM accident
        WHERE VehicleID NOT IN (SELECT VehicleID FROM vehicleviolation))
        UNION
        (SELECT VehicleID FROM vehicleviolation
        WHERE VehicleID NOT IN (SELECT VehicleID FROM accident));
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error executing symmetric difference query: {e}")
            return []
        finally:
            cursor.close()
            
    def vehicles_with_multiple_violations(self):
        """
        Fetch all VehicleIDs that have been involved in multiple violations.
        """
        query = """
        SELECT VehicleID, COUNT(ViolationID) AS ViolationCount
        FROM vehicleviolation
        GROUP BY VehicleID
        HAVING COUNT(ViolationID) > 1;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0], "ViolationCount": row[1]} for row in results]
        except Error as e:
            print(f"Error fetching vehicles with multiple violations: {e}")
            return []
        finally:
            cursor.close()
            
    def vehicles_with_no_violations(self):
        """
        Fetch all VehicleIDs that are registered but have no violations.
        """
        query = """
        SELECT v.VehicleID, v.LicensePlate
        FROM vehicle v
        LEFT JOIN vehicleviolation vv ON v.VehicleID = vv.VehicleID
        WHERE vv.VehicleID IS NULL;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0], "LicensePlate": row[1]} for row in results]
        except Error as e:
            print(f"Error fetching vehicles with no violations: {e}")
            return []
        finally:
            cursor.close()
            
    def most_common_violation_types(self):
        """
        Fetch the most common violation types.
        """
        query = """
        SELECT ViolationType, COUNT(vv.ViolationID) AS ViolationCount
        FROM violation v
        JOIN vehicleviolation vv ON v.ViolationID = vv.ViolationID
        GROUP BY ViolationType
        ORDER BY ViolationCount DESC;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"ViolationType": row[0], "ViolationCount": row[1]} for row in results]
        except Error as e:
            print(f"Error fetching most common violation types: {e}")
            return []
        finally:
            cursor.close()
            
    def vehicles_in_both_accidents_and_violations(self):
        """
        Fetch all VehicleIDs that are involved in both accidents and violations.
        """
        query = """
        SELECT DISTINCT a.VehicleID
        FROM accident a
        JOIN vehicleviolation vv ON a.VehicleID = vv.VehicleID;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error fetching vehicles involved in both accidents and violations: {e}")
            return []
        finally:
            cursor.close()
            
    def vehicles_in_only_accidents(self):
        """
        Fetch all VehicleIDs that are involved only in accidents.
        """
        query = """
        SELECT a.VehicleID
        FROM accident a
        LEFT JOIN vehicleviolation vv ON a.VehicleID = vv.VehicleID
        WHERE vv.VehicleID IS NULL;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"VehicleID": row[0]} for row in results]
        except Error as e:
            print(f"Error fetching vehicles involved only in accidents: {e}")
            return []
        finally:
            cursor.close()

    def close_connection(self):
        """Close the database connection if open."""
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")