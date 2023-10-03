from flask import Flask,Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import re
import mysql.connector
import os  # Add this line to import the 'os' module
from werkzeug.utils import secure_filename  # Add this line to import the 'secure_filename' function
# routes/doctors.py

from config.database import get_database_connection, close_database_connection

app = Flask(__name__)

# app.config['SECRET_KEY'] = 'cairocoders-ednalan'
bcrypt = Bcrypt(app)

doctors_bp = Blueprint('doctors', __name__)


# Route to save a new doctor
@doctors_bp.route('/save_doctor', methods=['POST'])
def save_doctor():
    if request.method == 'POST':
        # Get form data
        doctor_name = request.form['doctor_name']
        department = request.form['department']
        contact = request.form['contact']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        doc_license = request.form['license']
        availability = request.form['availability']

        # Handle the form submission to add a new doctor
        connection = get_database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO tabDoctor (name, doctor_name, department, contact, specialization, qualification, license, availability) "
                           "VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s)",
                           (doctor_name, department, contact, specialization, qualification, doc_license, availability))

            connection.commit()

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('doctors.doctors'))  # Redirect to the list of doctors after adding


# Function to get doctor details by ID
def get_doctor_by_id(doctor_id):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM tabDoctor WHERE name = %s"
        cursor.execute(query, (doctor_id,))
        doctor = cursor.fetchone()

        return doctor

    except Exception as e:
        print(f"Error in get_doctor_by_id: {e}")
        return None

    finally:
        close_database_connection(connection)

# Route to fetch doctor details by ID
@doctors_bp.route('/get_doctor_details/<string:doctor_id>', methods=['GET'])
def get_doctor_details(doctor_id):
    doctor = get_doctor_by_id(doctor_id)
    return jsonify({'doctor': doctor})

# Route to update doctor information
@doctors_bp.route('/update_doctor', methods=['POST'])
def update_doctor():
    cursor = None
    connection = None
    try:
        doctor_id = request.form['doctor_id']
        form_data = request.form.to_dict(flat=True)

        connection = get_database_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tabDoctor
            SET doctor_name = %s, department = %s, contact = %s,
                specialization = %s, qualification = %s, license = %s,
                availability = %s
            WHERE name = %s
        """
        cursor.execute(query, (
            form_data['doctor_name'],
            form_data['department'],
            form_data['contact'],
            form_data['specialization'],
            form_data['qualification'],
            form_data['license'],
            form_data['availability'],
            doctor_id
        ))

        connection.commit()
        return {'success': True, 'message': 'Doctor updated successfully'}

    except Exception as e:
        print(f"Error in update_doctor: {e}")
        return jsonify({'success': False, 'message': 'Error updating doctor'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to edit doctor information
@doctors_bp.route('/edit_doctor/<string:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = get_doctor_by_id(doctor_id)

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict(flat=True)

            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
                UPDATE tabDoctor
                SET doctor_name = %s, department = %s, contact = %s,
                    specialization = %s, qualification = %s, license = %s,
                    availability = %s
                WHERE name = %s
            """
            cursor.execute(query, (
                form_data['doctor_name'],
                form_data['department'],
                form_data['contact'],
                form_data['specialization'],
                form_data['qualification'],
                form_data['license'],
                form_data['availability'],
                doctor_id
            ))

            connection.commit()

            print("Doctor updated successfully!")

            return redirect(url_for('doctors.doctors'))

        except Exception as e:
            print(f"Error in edit_doctor POST: {e}")
            return jsonify({'success': False, 'message': 'Error updating doctor'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                close_database_connection(connection)

    return render_template('edit_doctor.html', doctor=doctor)


# Route to delete doctor
@doctors_bp.route('/delete_doctor/<string:doctor_id>', methods=['GET'])
def delete_doctor(doctor_id):
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Perform delete operation
        query = "DELETE FROM tabDoctor WHERE name = %s"
        cursor.execute(query, (doctor_id,))
        connection.commit()

        return redirect(url_for('doctors.doctors'))

    except Exception as e:
        print(f"Error in delete_doctor: {e}")
        return jsonify({'success': False, 'message': 'Error deleting doctor'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)



# Route to display the list of doctors
@doctors_bp.route("/doctors", methods=['GET', 'POST'])
def doctors():
    if 'loggedin' in session:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM tabDoctor")
            doctors = cursor.fetchall()

            return render_template("doctors.html", doctors=doctors)

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('doctors.doctors'))




