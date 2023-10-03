# routes/departments.py

from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import mysql.connector
from config.database import get_database_connection, close_database_connection

app = Flask(__name__)
bcrypt = Bcrypt(app)

departments_bp = Blueprint('departments', __name__)

# Route to save a new department
@departments_bp.route('/save_department', methods=['POST'])
def save_department():
    if request.method == 'POST':
        # Get form data
        dep_name = request.form['dep_name']
        description = request.form['description']
        hod = request.form['hod']
        contact = request.form['contact']
        opening_hours_from = request.form['opening_hours_from']
        opening_hours_to = request.form['opening_hours_to']
        beds = request.form['beds']

        # Handle the form submission to add a new department
        connection = get_database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO tabDepartment (name, dep_name, description, hod, contact, opening_hours_from, opening_hours_to, beds) "
                           "VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s)",
                           (dep_name, description, hod, contact, opening_hours_from, opening_hours_to, beds))

            connection.commit()

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('departments.departments'))  # Redirect to the list of departments after adding

# Function to get department details by ID
def get_department_by_id(dep_id):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM tabDepartment WHERE name = %s"
        cursor.execute(query, (dep_id,))
        department = cursor.fetchone()

        return department

    except Exception as e:
        print(f"Error in get_department_by_id: {e}")
        return None

    finally:
        close_database_connection(connection)

# Route to fetch department details by ID
@departments_bp.route('/get_department_details/<string:dep_id>', methods=['GET'])
def get_department_details(dep_id):
    department = get_department_by_id(dep_id)
    return jsonify({'department': department})

# Route to update department information
@departments_bp.route('/update_department', methods=['POST'])
def update_department():
    cursor = None
    connection = None
    try:
        dep_id = request.form['dep_id']
        form_data = request.form.to_dict(flat=True)

        connection = get_database_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tabDepartment
            SET dep_name = %s, description = %s, hod = %s, contact = %s,
                opening_hours_from = %s, opening_hours_to = %s, beds = %s
            WHERE name = %s
        """
        cursor.execute(query, (
            form_data['dep_name'],
            form_data['description'],
            form_data['hod'],
            form_data['contact'],
            form_data['opening_hours_from'],
            form_data['opening_hours_to'],
            form_data['beds'],
            dep_id
        ))

        connection.commit()
        return {'success': True, 'message': 'Department updated successfully'}

    except Exception as e:
        print(f"Error in update_department: {e}")
        return jsonify({'success': False, 'message': 'Error updating department'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to edit department information
@departments_bp.route('/edit_department/<string:dep_id>', methods=['GET', 'POST'])
def edit_department(dep_id):
    department = get_department_by_id(dep_id)

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict(flat=True)

            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
                UPDATE tabDepartment
                SET dep_name = %s, description = %s, hod = %s, contact = %s,
                    opening_hours_from = %s, opening_hours_to = %s, beds = %s
                WHERE name = %s
            """
            cursor.execute(query, (
                form_data['dep_name'],
                form_data['description'],
                form_data['hod'],
                form_data['contact'],
                form_data['opening_hours_from'],
                form_data['opening_hours_to'],
                form_data['beds'],
                dep_id
            ))

            connection.commit()

            print("Department updated successfully!")

            return redirect(url_for('departments.departments'))

        except Exception as e:
            print(f"Error in edit_department POST: {e}")
            return jsonify({'success': False, 'message': 'Error updating department'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                close_database_connection(connection)

    return render_template('edit_department.html', department=department)

# Route to delete department
@departments_bp.route('/delete_department/<string:dep_id>', methods=['GET'])
def delete_department(dep_id):
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Perform delete operation
        query = "DELETE FROM tabDepartment WHERE name = %s"
        cursor.execute(query, (dep_id,))
        connection.commit()

        return redirect(url_for('departments.departments'))

    except Exception as e:
        print(f"Error in delete_department: {e}")
        return jsonify({'success': False, 'message': 'Error deleting department'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to display the list of departments
@departments_bp.route("/departments", methods=['GET', 'POST'])
def departments():
    if 'loggedin' in session:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM tabDepartment")
            departments = cursor.fetchall()

            return render_template("departments.html", departments=departments)

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('departments.departments'))
