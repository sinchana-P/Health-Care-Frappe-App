# routes/billing.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from config.database import get_database_connection, close_database_connection
from mysql.connector import Error 
from decimal import Decimal
from werkzeug.datastructures import ImmutableMultiDict


billing_bp = Blueprint('billing', __name__)


# Route to display the list of billings
@billing_bp.route("/billings", methods=['GET'])
def billings():
    patients = get_patients()
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch billing data from the database
        cursor.execute("SELECT * FROM tabBilling")
        billings = cursor.fetchall()

        return render_template("billing.html", billings=billings, patients=patients)

    except Exception as e:
        print(f"Error in billings route: {e}")
        # You can redirect to an error page or return an error response
        return render_template("error.html", error_message="An error occurred. Please try again later.")

    finally:
        cursor.close()
        close_database_connection(connection)



@billing_bp.route('/save_billing', methods=['POST'])
def save_billing():
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.form['patient']
            services_provided = request.form['services_provided']
            item_name = request.form['item_name']
            quantity = int(request.form['quantity'])
            unit_price = float(request.form['unit_price'])
            tax = float(request.form['tax'])
            total_amount = quantity * unit_price + quantity * tax
            payment_method = request.form['payment_method']
            payment_status = request.form['payment_status']
            payment_date = request.form['payment_date']
            paid = request.form.get('paid', 'No')  # Default to 'No' if not provided

            print(patient_id)
            # Validate form data (add your validation logic here)

            # Handle the form submission to add a new billing
            connection = get_database_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO tabBilling
                (name, patient, services_provided, item_name, quantity, unit_price, tax, total_amount, payment_method, payment_status, payment_date, paid)
                VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, services_provided, item_name, quantity, unit_price, tax, total_amount, payment_method, payment_status, payment_date, paid))

            connection.commit()

        except Error as e:
            # Handle the database error
            print(f"Database error: {e}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('billing.billings'))  # Redirect to the list of billings after adding



# Route to edit billing information
@billing_bp.route('/edit_billing/<string:billing_id>', methods=['GET', 'POST'])
def edit_billing(billing_id):
    billing = get_billing_by_id(billing_id)

    if request.method == 'POST':
        # Update billing information in the database
        update_billing(billing_id, request.form)

        return redirect(url_for('billing.billings'))

    patients = get_patients()  # Fetch patient data for dynamic dropdown

    return render_template('edit_billing.html', billing=billing, patients=patients)

# Function to get billing details by ID
def get_billing_by_id(billing_id):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM tabBilling WHERE name = %s", (billing_id,))
        billing = cursor.fetchone()

        return billing

    except Exception as e:
        print(f"Error in get_billing_by_id: {e}")
        return None

    finally:
        cursor.close()
        close_database_connection(connection)


def update_billing(billing_id, form_data):
    connection = get_database_connection()
    cursor = connection.cursor()
    print("form data:", form_data)

    try:
        # Convert ImmutableMultiDict to a regular Python dictionary
        form_data_dict = form_data.to_dict(flat=False)

        # Retrieve the original billing information
        original_billing = get_billing_by_id(billing_id)

        if original_billing:
            # Use the original values for calculation
            total_amount = (
                int(form_data_dict['quantity'][0]) * float(form_data_dict['unit_price'][0])
                + int(form_data_dict['quantity'][0]) * float(form_data_dict['tax'][0])
            )

            cursor.execute("""
                UPDATE tabBilling
                SET patient = %s, services_provided = %s, item_name = %s,
                    quantity = %s, unit_price = %s, tax = %s, total_amount = %s,
                    payment_method = %s, payment_status = %s, payment_date = %s, paid = %s
                WHERE name = %s
            """, (
                form_data_dict['patient'][0],
                form_data_dict['services_provided'][0],
                form_data_dict['item_name'][0],
                form_data_dict['quantity'][0],
                form_data_dict['unit_price'][0],
                form_data_dict['tax'][0],
                total_amount,  # Use the calculated total_amount
                form_data_dict['payment_method'][0],
                form_data_dict['payment_status'][0],
                form_data_dict['payment_date'][0],
                form_data_dict.get('paid', ['No'])[0],  # Default to 'No' if not provided
                billing_id
            ))

            print(form_data)
            connection.commit()
        else:
            print(f"Error: Billing record with ID {billing_id} not found.")

    except Exception as e:
        print(f"Error in update_billing: {e}")

    finally:
        cursor.close()
        close_database_connection(connection)


@billing_bp.route("/delete_billing/<string:billing_id>", methods=['GET'])
def delete_billing(billing_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        # Perform delete operation
        query = "DELETE FROM tabBilling WHERE name = %s"
        cursor.execute(query, (billing_id,))
        connection.commit()

        flash('Billing record deleted successfully', 'success')
        return redirect(url_for('billing.billings'))

    except Exception as e:
        print(f"Error in delete_billing: {e}")
        flash('Error deleting billing record', 'error')
        return redirect(url_for('billing.billings'))

    finally:
        cursor.close()
        close_database_connection(connection)

# Function to fetch patients for the dynamic dropdown
def get_patients():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT name, patient_name FROM tabPatient")
        patients = cursor.fetchall()

        return patients

    except Exception as e:
        print(f"Error in get_patients: {e}")
        return None

    finally:
        cursor.close()
        close_database_connection(connection)
