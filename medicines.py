from flask import Flask,Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import re
from datetime import datetime
import mysql.connector
import os  # Add this line to import the 'os' module
from werkzeug.utils import secure_filename  # Add this line to import the 'secure_filename' function
# routes/doctors.py

from config.database import get_database_connection, close_database_connection


medicines_bp = Blueprint('medicines', __name__)


# Route to save a new medicine
@medicines_bp.route('/save_medicine', methods=['POST'])
def save_medicine():
    if request.method == 'POST':
        # Get form data
        medicine_name = request.form['medicine_name']
        generic_name = request.form['generic_name']
        dosage_form = request.form['dosage_form']
        strength = request.form['strength']
        prescription_required = request.form['prescription_required']
        manufacturer = request.form['manufacturer']
        description = request.form['description']
        storage_instructions = request.form['storage_instructions']
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        quantity_available = int(request.form['quantity_available'])
        unit_price = float(request.form['unit_price'])
        medication_category = request.form['medication_category']
        side_effects = request.form['side_effects']
        contraindications = request.form['contraindications']
        dosage_instructions = request.form['dosage_instructions']

        # Handle the form submission to add a new medicine
        connection = get_database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO tabMedicines
                (name, medicine_name, generic_name, dosage_form, strength, prescription_required,
                manufacturer, description, storage_instructions, expiry_date, quantity_available,
                unit_price, medication_category, side_effects, contraindications, dosage_instructions)
                VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (medicine_name, generic_name, dosage_form, strength, prescription_required,
                 manufacturer, description, storage_instructions, expiry_date, quantity_available,
                 unit_price, medication_category, side_effects, contraindications, dosage_instructions))

            connection.commit()

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('medicines.medicines'))  # Redirect to the list of medicines after adding

# Function to get medicine details by ID
def get_medicine_by_id(medicine_id):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM tabMedicines WHERE name = %s"
        cursor.execute(query, (medicine_id,))
        medicine = cursor.fetchone()

        return medicine

    except Exception as e:
        print(f"Error in get_medicine_by_id: {e}")
        return None

    finally:
        close_database_connection(connection)

# Route to fetch medicine details by ID
@medicines_bp.route('/get_medicine_details/<string:medicine_id>', methods=['GET'])
def get_medicine_details(medicine_id):
    medicine = get_medicine_by_id(medicine_id)
    return jsonify({'medicine': medicine})

# Route to update medicine information
@medicines_bp.route('/update_medicine', methods=['POST'])
def update_medicine():
    cursor = None
    connection = None
    try:
        medicine_id = request.form['medicine_id']
        form_data = request.form.to_dict(flat=True)

        connection = get_database_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tabMedicines
            SET medicine_name = %s, generic_name = %s, dosage_form = %s,
                strength = %s, prescription_required = %s, manufacturer = %s,
                description = %s, storage_instructions = %s, expiry_date = %s,
                quantity_available = %s, unit_price = %s, medication_category = %s,
                side_effects = %s, contraindications = %s, dosage_instructions = %s
            WHERE name = %s
        """
        cursor.execute(query, (
            form_data['medicine_name'], form_data['generic_name'], form_data['dosage_form'],
            form_data['strength'], form_data['prescription_required'], form_data['manufacturer'],
            form_data['description'], form_data['storage_instructions'], form_data['expiry_date'],
            form_data['quantity_available'], form_data['unit_price'], form_data['medication_category'],
            form_data['side_effects'], form_data['contraindications'], form_data['dosage_instructions'],
            medicine_id
        ))

        connection.commit()
        return {'success': True, 'message': 'Medicine updated successfully'}

    except Exception as e:
        print(f"Error in update_medicine: {e}")
        return jsonify({'success': False, 'message': 'Error updating medicine'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to edit medicine information
@medicines_bp.route('/edit_medicine/<string:medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    medicine = get_medicine_by_id(medicine_id)

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict(flat=True)

            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
                UPDATE tabMedicines
                SET medicine_name = %s, generic_name = %s, dosage_form = %s,
                    strength = %s, prescription_required = %s, manufacturer = %s,
                    description = %s, storage_instructions = %s, expiry_date = %s,
                    quantity_available = %s, unit_price = %s, medication_category = %s,
                    side_effects = %s, contraindications = %s, dosage_instructions = %s
                WHERE name = %s
            """
            cursor.execute(query, (
                form_data['medicine_name'], form_data['generic_name'], form_data['dosage_form'],
                form_data['strength'], form_data['prescription_required'], form_data['manufacturer'],
                form_data['description'], form_data['storage_instructions'], form_data['expiry_date'],
                form_data['quantity_available'], form_data['unit_price'], form_data['medication_category'],
                form_data['side_effects'], form_data['contraindications'], form_data['dosage_instructions'],
                medicine_id
            ))

            connection.commit()

            print("Medicine updated successfully!")

            return redirect(url_for('medicines.medicines'))

        except Exception as e:
            print(f"Error in edit_medicine POST: {e}")
            return jsonify({'success': False, 'message': 'Error updating medicine'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                close_database_connection(connection)

    return render_template('edit_medicine.html', medicine=medicine)

# Route to delete medicine
@medicines_bp.route('/delete_medicine/<string:medicine_id>', methods=['GET'])
def delete_medicine(medicine_id):
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Perform delete operation
        query = "DELETE FROM tabMedicines WHERE name = %s"
        cursor.execute(query, (medicine_id,))
        connection.commit()

        return redirect(url_for('medicines.medicines'))

    except Exception as e:
        print(f"Error in delete_medicine: {e}")
        return jsonify({'success': False, 'message': 'Error deleting medicine'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to display the list of medicines
@medicines_bp.route("/medicines", methods=['GET', 'POST'])
def medicines():
    if 'loggedin' in session:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM tabMedicines")
            medicines = cursor.fetchall()

            return render_template("medicines.html", medicines=medicines)

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('medicines.medicines'))
