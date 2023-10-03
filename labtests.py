# routes/labtests.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from config.database import get_database_connection, close_database_connection

labtests_bp = Blueprint('labtests', __name__)

# Route to save a new lab test
@labtests_bp.route('/save_labtest', methods=['POST'])
def save_labtest():
    if request.method == 'POST':
        lab_test_name = request.form['lab_test_name']
        fee = request.form['fee']
        vital_organs = request.form['vital_organs']
        checkups = request.form['checkups']

        connection = get_database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO tabLabTests (name, lab_test_name, fee, vital_organ, checkups) "
                           "VALUES (uuid(), %s, %s, %s, %s)",
                           (lab_test_name, fee, vital_organs, checkups))

            connection.commit()

        except Exception as e:
            print(f"Error in save_labtest: {e}")

        finally:
            cursor.close()
            close_database_connection(connection)

    return redirect(url_for('labtests.labtests'))

# Function to get lab test details by ID
def get_labtest_by_id(labtest_id):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM tabLabTests WHERE name = %s"
        cursor.execute(query, (labtest_id,))
        labtest = cursor.fetchone()

        return labtest

    except Exception as e:
        print(f"Error in get_labtest_by_id: {e}")
        return None

    finally:
        close_database_connection(connection)

# Route to fetch lab test details by ID
@labtests_bp.route('/get_labtest_details/<string:labtest_id>', methods=['GET'])
def get_labtest_details(labtest_id):
    labtest = get_labtest_by_id(labtest_id)
    return jsonify({'labtest': labtest})

# Route to update lab test information
@labtests_bp.route('/update_labtest', methods=['POST'])
def update_labtest():
    cursor = None
    connection = None
    try:
        labtest_id = request.form['labtest_id']
        form_data = request.form.to_dict(flat=True)

        connection = get_database_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tabLabTests
            SET lab_test_name = %s, fee = %s, vital_organ = %s,
                checkups = %s
            WHERE name = %s
        """
        cursor.execute(query, (
            form_data['lab_test_name'],
            form_data['fee'],
            form_data['vital_organs'],
            form_data['checkups'],
            labtest_id
        ))

        connection.commit()
        return {'success': True, 'message': 'Lab test updated successfully'}

    except Exception as e:
        print(f"Error in update_labtest: {e}")
        return jsonify({'success': False, 'message': 'Error updating lab test'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to edit lab test information
@labtests_bp.route('/edit_labtest/<string:labtest_id>', methods=['GET', 'POST'])
def edit_labtest(labtest_id):
    labtest = get_labtest_by_id(labtest_id)

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict(flat=True)

            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
                UPDATE tabLabTests
                SET lab_test_name = %s, fee = %s, vital_organ = %s,
                    checkups = %s
                WHERE name = %s
            """
            cursor.execute(query, (
                form_data['lab_test_name'],
                form_data['fee'],
                form_data['vital_organs'],
                form_data['checkups'],
                labtest_id
            ))

            connection.commit()

            print("Lab test updated successfully!")

            return redirect(url_for('labtests.labtests'))

        except Exception as e:
            print(f"Error in edit_labtest POST: {e}")
            return jsonify({'success': False, 'message': 'Error updating lab test'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                close_database_connection(connection)

    return render_template('edit_labtest.html', labtest=labtest)

# Route to delete lab test
@labtests_bp.route('/delete_labtest/<string:labtest_id>', methods=['GET'])
def delete_labtest(labtest_id):
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Perform delete operation
        query = "DELETE FROM tabLabTests WHERE name = %s"
        cursor.execute(query, (labtest_id,))
        connection.commit()

        return redirect(url_for('labtests.labtests'))

    except Exception as e:
        print(f"Error in delete_labtest: {e}")
        return jsonify({'success': False, 'message': 'Error deleting lab test'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)

# Route to display the list of lab tests
@labtests_bp.route("/labtests", methods=['GET', 'POST'])
def labtests():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM tabLabTests")
        labtests = cursor.fetchall()

        return render_template("labtests.html", labtests=labtests)

    except Exception as e:
        print(f"Error in labtests: {e}")

    finally:
        cursor.close()
        close_database_connection(connection)

    return redirect(url_for('labtests.labtests'))
