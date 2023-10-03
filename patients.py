from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import mysql.connector
from config.database import get_database_connection, close_database_connection

patients_bp = Blueprint('patients', __name__)

# Route to display the list of patients
@patients_bp.route("/patients", methods=['GET', 'POST'])
def patients():
    if 'loggedin' in session:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM tabPatient")
            patients = cursor.fetchall()

            return render_template("patients.html", patients=patients)

        except mysql.connector.Error as err:
            # Handle the database error
            print(f"Database error: {err}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('patients.patients'))
