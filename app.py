from flask import Flask, render_template, request, redirect, url_for, flash
from crud_flask import DatabaseManager
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key for flash messages

# Initialize DatabaseManager with database connection details
db = DatabaseManager(host="localhost", user="root", password="password", database="grp4-deliverable5")

# List of available tables
TABLES = ["accident", "address", "camera", "phonenumber", "road", 
          "roadcamera", "user", "vehicle", "vehicleviolation", "violation"]

@app.route('/')
def index():
    try:
        # Fetch data from DatabaseManager methods
        total_accidents = db.get_total_accidents()
        active_violations = db.get_active_violations()
        cameras_operational = db.get_operational_cameras()
        
        # Fetch data for charts
        monthly_accidents_data = db.get_monthly_accidents()
        violation_distribution_data = db.get_violation_distribution()
        bubble_chart_data = db.get_bubble_chart_data()  # Add logic to fetch bubble chart data

        # Extract labels and counts for charts
        monthly_accidents = [row['month'] for row in monthly_accidents_data]
        monthly_accidents_counts = [row['count'] for row in monthly_accidents_data]

        violation_distribution_labels = [row['ViolationType'] for row in violation_distribution_data]
        violation_distribution_counts = [row['count'] for row in violation_distribution_data]
        total_violations = db.get_total_violations()

        # List of available tables
        tables = ["accident", "address", "camera", "phonenumber", "road", 
                  "roadcamera", "user", "vehicle", "vehicleviolation", "violation"]

        # Pass all the data to the template
        return render_template(
            'index.html',
            tables=tables,
            total_accidents=total_accidents,
            total_violations=total_violations,
            cameras_operational=cameras_operational,
            monthly_accidents=monthly_accidents,
            monthly_accidents_counts=monthly_accidents_counts,
            violation_distribution_labels=violation_distribution_labels,
            violation_distribution_counts=violation_distribution_counts,
            bubble_chart_data=bubble_chart_data  # Pass bubble chart data to the template
        )
    except Exception as e:
        # Handle errors gracefully
        flash(f"Error fetching data: {str(e)}", "danger")
        return render_template('index.html', tables=[], total_accidents=0, active_violations=0, cameras_operational=0)

@app.route('/select_table')
def select_table():
    # Page where user selects a table to view records
    return render_template('select_table.html', tables=TABLES)

@app.route('/select_table_for_create')
def select_table_for_create():
    # Page where user selects a table to create a record
    return render_template('select_table_for_create.html', tables=TABLES)

@app.route('/create/<table>', methods=['GET', 'POST'])
def create_record(table):
    if request.method == 'POST':
        try:
            # Collect form data and insert it into the database
            data = request.form.to_dict()
            success = db.create_record(table, data)
            
            if success:
                flash(f"Record successfully created in '{table}' table.", "success")
            else:
                flash(f"Failed to create record in '{table}' table.", "danger")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
    
    # Get columns to display the input form dynamically
    columns = db.get_columns(table)
    return render_template('create_record.html', table=table, columns=columns)

@app.route('/read/<table>')
def read_records(table):
    try:
        # Fetch records and columns from the specified table
        records = db.read_record(table)
        columns = db.get_columns(table)
        print("Records:", records)  # Debugging line
        print("Columns:", columns)  # Debugging line
        return render_template('view_records.html', records=records, columns=columns, table=table)
    except Exception as e:
        flash(f"Error reading records from {table}: {str(e)}", "danger")
        return redirect(url_for('select_table'))

@app.route('/update/<table>', methods=['GET', 'POST'])
def update_record(table):
    try:
        if request.method == 'POST':
            record_id = request.form['record_id']
            column = request.form['column']
            new_value = request.form['new_value']
            update_data = {column: new_value}
            
            # Attempt to update the record
            success = db.update_record(table, record_id, update_data)
            if success:
                flash(f"Record with ID '{record_id}' successfully updated in '{table}' table.", "success")
            else:
                flash(f"Failed to update record with ID '{record_id}' in '{table}' table.", "danger")
            return redirect(url_for('update_record', table=table))

        # If GET request, fetch columns for the selected table
        columns = db.get_columns(table)
        return render_template('update_record.html', table=table, columns=columns)
    except Exception as e:
        flash(f"An error occurred while updating record: {str(e)}", "danger")
        return redirect(url_for('update_record', table=table))


### 4. Delete Record Route
# @app.route('/delete/<table>', methods=['GET', 'POST'])
# def delete_record(table):
#     if request.method == 'POST':
#         record_id = request.form['record_id']
#         try:
#             # Call the delete_record method from DatabaseManager
#             db.delete_record(table, record_id)
#             flash(f"Record deleted successfully from {table}.", "success")
#         except Exception as e:
#             flash(f"Error deleting record: {str(e)}", "danger")
#         return redirect(url_for('index'))

#     return render_template('delete_record.html', table=table)
@app.route('/delete/<table>', methods=['GET', 'POST'])
def delete_record(table):
    if request.method == 'POST':
        record_id = request.form['record_id']
        try:
            # Call the delete_record method from your DatabaseManager
            db.delete_record(table, record_id)
            flash(f"Record with ID {record_id} successfully deleted from '{table}'.", "success")
        except Exception as e:
            flash(f"Failed to delete record with ID {record_id} from '{table}': {str(e)}", "danger")
        return redirect(url_for('delete_record', table=table))
    return render_template('delete_record.html', table=table)

### 5. Complex Queries Page Route
# Route for the complex queries menu
@app.route('/queries')
def queries():
    # Render the page listing all complex queries
    return render_template('queries.html')

# Route for Set Operations Query
@app.route('/set_operations_query')
def set_operations_query():
    try:
        results = db.set_operations_query()
        return render_template('set_operations_result.html', results=results)
    except Exception as e:
        flash(f"Error executing set operations query: {str(e)}", "danger")
        return redirect(url_for('queries'))

# Route for Set Membership Query
@app.route('/set_membership_query', methods=['GET', 'POST'])
def set_membership_query():
    result = None
    vehicle_id = None
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        try:
            result = db.set_membership_query(int(vehicle_id))
        except Exception as e:
            flash(f"Error executing set membership query: {str(e)}", "danger")
            return redirect(url_for('queries'))
    return render_template('set_membership_result.html', result=result, vehicle_id=vehicle_id)

# Route for Set Comparison Query
@app.route('/set_comparison_query')
def set_comparison_query():
    try:
        results = db.set_comparison_query()
        return render_template('set_comparison_result.html', results=results)
    except Exception as e:
        flash(f"Error executing set comparison query: {str(e)}", "danger")
        return redirect(url_for('queries'))

# Route for Subquery with CTE
# @app.route('/subquery_with_clause')
# def subquery_with_clause():
#     try:
#         results = db.subquery_with_clause()
#         return render_template('subquery_result.html', results=results)
#     except Exception as e:
#         flash(f"Error executing subquery with clause: {str(e)}", "danger")
#         return redirect(url_for('queries'))
@app.route('/subquery_with_total_fines')
def subquery_with_total_fines():
    try:
        results = db.subquery_with_clause()
        return render_template('subquery_result.html', title="Total Fines by Vehicle", results=results, headers=["VehicleID", "TotalFine"])
    except Exception as e:
        flash(f"Error executing subquery with total fines: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/top_3_roads_with_most_accidents')
def top_3_roads_with_most_accidents():
    try:
        results = db.top_3_roads_with_most_accidents()
        return render_template('subquery_result.html', title="Top 3 Roads with Most Accidents", results=results, headers=["RoadID", "RoadName", "AccidentCount"])
    except Exception as e:
        flash(f"Error executing top 3 roads query: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/users_and_vehicle_violations')
def users_and_vehicle_violations():
    try:
        # Default minimum fine is 0; can be parameterized
        min_fine = request.args.get('min_fine', default=0, type=int)
        results = db.users_and_vehicle_violations(min_fine)
        return render_template('subquery_result.html', title="Users and Vehicle Violations", results=results, headers=["UserID", "UserName", "VehicleID", "ViolationType", "FineAmount"])
    except Exception as e:
        flash(f"Error fetching users and their violations: {str(e)}", "danger")
        return redirect(url_for('queries'))

# Route for Advanced Aggregate Query
@app.route('/advanced_aggregate_query')
def advanced_aggregate_query():
    try:
        results = db.advanced_aggregate_query()
        return render_template('advanced_aggregate_result.html', results=results)
    except Exception as e:
        flash(f"Error executing advanced aggregate query: {str(e)}", "danger")
        return redirect(url_for('queries'))
    
@app.route('/average_fine_per_violation_type')
def average_fine_per_violation_type():
    try:
        results = db.average_fine_per_violation_type()
        return render_template('advanced_aggregate_result.html', title="Average Fine Per Violation Type", results=results)
    except Exception as e:
        flash(f"Error fetching average fine per violation type: {e}", "danger")
        return redirect(url_for('queries'))

@app.route('/running_total_accidents_per_road')
def running_total_accidents_per_road():
    try:
        results = db.running_total_accidents_per_road()
        return render_template('advanced_aggregate_result.html', title="Running Total of Accidents Per Road", results=results)
    except Exception as e:
        flash(f"Error fetching running total accidents per road: {e}", "danger")
        return redirect(url_for('queries'))

# Route for OLAP Query
@app.route('/olap_query')
def olap_query():
    try:
        results = db.olap_query()
        return render_template('olap_result.html', title="Fine rank per vehicle", results=results)
    except Exception as e:
        flash(f"Error executing OLAP query: {str(e)}", "danger")
        return redirect(url_for('queries'))
    
@app.route('/percentage_contribution_of_accidents')
def percentage_contribution_of_accidents():
    try:
        results = db.percentage_contribution_of_accidents()
        return render_template('olap_result.html', title="Percentage Contribution of Accidents", results=results)
    except Exception as e:
        flash(f"Error fetching percentage contribution of accidents: {e}", "danger")
        return redirect(url_for('queries'))

@app.route('/partitioned_sum_of_fines')
def partitioned_sum_of_fines():
    try:
        results = db.partitioned_sum_of_fines()
        return render_template('olap_result.html', title="Partitioned Sum of Fines", results=results)
    except Exception as e:
        flash(f"Error fetching partitioned sum of fines: {e}", "danger")
        return redirect(url_for('queries'))

    
@app.route('/detailed_violation')
def detailed_violation():
    violation_type = request.args.get('type')
    records = db.get_records_by_violation_type(violation_type)  # Fetch records by type
    return render_template('detailed_violation.html', violation_type=violation_type, records=records)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/union_query')
def union_query():
    try:
        results = db.union_query()
        return render_template('set_operations_result.html', title="Union Query", results=results)
    except Exception as e:
        flash(f"Error executing union query: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/intersect_query')
def intersect_query():
    try:
        results = db.intersect_query()
        return render_template('set_operations_result.html', title="Intersect Query", results=results)
    except Exception as e:
        flash(f"Error executing intersect query: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/except_query')
def except_query():
    try:
        results = db.except_query()
        return render_template('set_operations_result.html', title="Except Query", results=results)
    except Exception as e:
        flash(f"Error executing except query: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/difference_query')
def difference_query():
    try:
        results = db.difference_query()
        return render_template('set_operations_result.html', title="Difference Query", results=results)
    except Exception as e:
        flash(f"Error executing difference query: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/symmetric_difference_query')
def symmetric_difference_query():
    try:
        results = db.symmetric_difference_query()
        return render_template('set_operations_result.html', title="Symmetric Difference Query", results=results)
    except Exception as e:
        flash(f"Error executing symmetric difference query: {str(e)}", "danger")
        return redirect(url_for('queries'))
    
@app.route('/vehicles_with_multiple_violations')
def vehicles_with_multiple_violations():
    try:
        results = db.vehicles_with_multiple_violations()
        return render_template('set_comparison_result.html', title="Vehicles with Multiple Violations", results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/vehicles_with_no_violations')
def vehicles_with_no_violations():
    try:
        results = db.vehicles_with_no_violations()
        return render_template('set_comparison_result.html', title="Vehicles with No Violations", results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/most_common_violation_types')
def most_common_violation_types():
    try:
        results = db.most_common_violation_types()
        return render_template('set_comparison_result.html', title="Most Common Violation Types", results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/vehicles_in_both_accidents_and_violations')
def vehicles_in_both_accidents_and_violations():
    try:
        results = db.vehicles_in_both_accidents_and_violations()
        return render_template('set_comparison_result.html', title="Vehicles in Both Accidents and Violations", results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('queries'))

@app.route('/vehicles_in_only_accidents')
def vehicles_in_only_accidents():
    try:
        results = db.vehicles_in_only_accidents()
        return render_template('set_comparison_result.html', title="Vehicles in Only Accidents", results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('queries'))

if __name__ == '__main__':
    app.run(debug=True)