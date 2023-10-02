from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import re
import mysql.connector
import os  # Add this line to import the 'os' module
from werkzeug.utils import secure_filename  # Add this line to import the 'secure_filename' function


app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
bcrypt = Bcrypt(app)

# Database connection parameters
db_config = {
    "host": "localhost",
    "user": "sinch",
    "password": "Sinchu@333",
    "database": "_14796a9152410a05",
}

def get_database_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def close_database_connection(connection):
    connection.close()


# Add this line to set up the upload folder
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Add this line to define allowed file extensions


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/')
def home():
    return redirect(url_for('login')) 

# FOr Layout
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'name' in session and session['name']:
        # return f"Hello {session['name']}"
        return render_template('dashboard.html', name=session['name'])
    else:
        return redirect(url_for('login'))
    

# For hello
@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if 'name' in session and session['name']:
        return f"Hello {session['name']}"
        # return render_template('dashboard.html', name=session['name'])
    else:
        return redirect(url_for('login'))
    
# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     return "Welcome to explore our app!"


# For Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

def register_user(fullname, email, password):
    try:
        print(fullname, email, password)
        connection = get_database_connection()
        cursor = connection.cursor()

        # Check if the email already exists
        cursor.execute("SELECT user_name FROM tabHealth_Care_Users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return 'Email already exists!'

        # Insert the new user into the 'tabHealth_Care_Users' table
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO tabHealth_Care_Users (name, user_name, email, password) VALUES (uuid(), %s, %s, %s)",
                       (fullname, email, hashed_password))
        connection.commit()

        print(fullname, email, password)
        return 'You have successfully registered!'

    except mysql.connector.Error as err:
        return f"Database error: {err}"

    finally:
        cursor.close()
        close_database_connection(connection)

def login_user(email, password):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Check if the email and password match a record in the database
        cursor.execute("SELECT name, user_name, password FROM tabHealth_Care_Users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            if not bcrypt.check_password_hash(result[2], password):
                return 'Please enter correct email and password!'
            else:
                session['loggedin'] = True
                session['userid'] = result[0]
                session['name'] = result[1]
                session['email'] = email
                print(session['name'], session['email'])

                return 'Logged in successfully!'
        else:
            return 'Please enter correct email / password!'

    except mysql.connector.Error as err:
        return f"Database error: {err}"

    finally:
        cursor.close()
        close_database_connection(connection)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("register")
    message = ''
    if request.method == 'POST' and 'user_name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['user_name']
        password = request.form['password']
        email = request.form['email']

        print("inside register")
        print(fullname, email, password)

        
        message = register_user(fullname, email, password)
        return redirect(url_for('register'))
    
    elif request.method == 'POST':
        message = 'Please fill out the form!'

    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        message = login_user(email, password)

        if 'Logged in successfully!' in message:
            return redirect(url_for('dashboard'))

    return render_template('login.html', message=message)


# Manage Books
# @app.route("/books", methods=['GET', 'POST'])
# def books():
#     if 'loggedin' in session:
#         return render_template('books.html')
#     return redirect(url_for('login'))



# Route to save a new doctor
@app.route('/save_doctor', methods=['POST'])
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

    return redirect(url_for('doctors'))  # Redirect to the list of doctors after adding


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
@app.route('/get_doctor_details/<string:doctor_id>', methods=['GET'])
def get_doctor_details(doctor_id):
    doctor = get_doctor_by_id(doctor_id)
    return jsonify({'doctor': doctor})

# Route to update doctor information
@app.route('/update_doctor', methods=['POST'])
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
@app.route('/edit_doctor/<string:doctor_id>', methods=['GET', 'POST'])
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

            return redirect(url_for('doctors'))

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
@app.route('/delete_doctor/<string:doctor_id>', methods=['GET'])
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

        return redirect(url_for('doctors'))

    except Exception as e:
        print(f"Error in delete_doctor: {e}")
        return jsonify({'success': False, 'message': 'Error deleting doctor'})

    finally:
        if cursor:
            cursor.close()
        if connection:
            close_database_connection(connection)























# Route to delete a doctor
# @app.route('/delete_doctor/<doctorid>', methods=['GET', 'POST'])
# def delete_doctor(doctorid):
#     if request.method == 'POST':
#         # Handle the form submission to delete the doctor
#         connection = get_database_connection()
#         cursor = connection.cursor()

#         try:
#             cursor.execute("DELETE FROM tabDoctor WHERE name = %s", (doctorid,))
#             connection.commit()

#         except mysql.connector.Error as err:
#             # Handle the database error
#             print(f"Database error: {err}")

#         finally:
#             cursor.close()
#             close_database_connection(connection)

#         return redirect(url_for('doctors'))  # Redirect to the list of doctors after deletion

#     # # Fetch the details of the doctor for confirmation
#     # connection = get_database_connection()
#     # cursor = connection.cursor(dictionary=True)

#     # try:
#     #     cursor.execute("SELECT * FROM tabDoctors WHERE name = %s", (doctorid,))
#     #     doctor = cursor.fetchone()

#     #     return render_template('delete_doctor.html', doctor=doctor)

#     # except mysql.connector.Error as err:
#     #     # Handle the database error
#     #     print(f"Database error: {err}")
#     #     # You might want to redirect to an error page or handle it in a way suitable for your application.

#     # finally:
#     #     cursor.close()
#     #     close_database_connection(connection)

# Route to display the list of doctors
@app.route("/doctors", methods=['GET', 'POST'])
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

    return redirect(url_for('doctors'))







# @app.route('/doctors', methods=['GET', 'POST'])
# def doctors():
#     if 'loggedin' in session:
#         return render_template('doctors.html')
#     return redirect(url_for('login'))


# # Manage Doctors
# @app.route("/doctors", methods=['GET', 'POST'])
# def doctors():
#     if 'loggedin' in session:
#         # Assuming you have a Doctor model defined
#         doctors = Doctor.query.all()
 
#         return render_template("doctors.html", doctors=doctors)
#     return redirect(url_for('login'))


# Manage Doctors
# @app.route("/doctors", methods=['GET', 'POST'])
# def doctors():
#     if 'loggedin' in session:
#         connection = get_database_connection()
#         cursor = connection.cursor(dictionary=True)

#         try:
#             # Execute a SELECT query to fetch all doctors from the tabDoctor table
#             cursor.execute("SELECT * FROM tabDoctor")
#             doctors = cursor.fetchall()

#             return render_template("doctors.html", doctors=doctors)

#         except mysql.connector.Error as err:
#             # Handle the database error
#             print(f"Database error: {err}")
#             # You might want to redirect to an error page or handle it in a way suitable for your application.

#         finally:
#             # Close the cursor and connection
#             cursor.close()
#             close_database_connection(connection)

#     return redirect(url_for('login'))


# @app.route('/save_doctor', methods=['POST'])
# def save_doctor():
#     msg = ''
#     if 'loggedin' in session:
#         if request.method == 'POST':
#             doctor_name = request.form['doctor_name']
#             department = request.form['department']
#             contact = request.form['contact']
#             specialization = request.form['specialization']
#             qualification = request.form['qualification']
#             doc_license = request.form['license']
#             availability = request.form['availability']
#             action = request.form['action']

#             connection = get_database_connection()
#             cursor = connection.cursor()

#             try:
#                 if action == 'addDoctor':
#                     cursor.execute("INSERT INTO tabDoctor (name, doctor_name, department, contact, specialization, qualification, license, availability) VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s)",
#                                    (doctor_name, department, contact, specialization, qualification, doc_license, availability))
#                     connection.commit()
#                     msg = 'Doctor added successfully!'

#                 elif action == 'updateDoctor':
#                     doctor_id = request.form['name']
#                     cursor.execute("UPDATE tabDoctor SET doctor_name=%s, department=%s, contact=%s, specialization=%s, qualification=%s, license=%s, availability=%s WHERE name=%s",
#                                    (doctor_name, department, contact, specialization, qualification, doc_license, availability, doctor_id))
#                     connection.commit()
#                     msg = 'Doctor updated successfully!'

#                 elif action == 'deleteDoctor':
#                     doctor_id = request.form['name']
#                     cursor.execute("DELETE FROM tabDoctor WHERE name=%s", (doctor_id,))
#                     connection.commit()
#                     msg = 'Doctor deleted successfully!'

#                 else:
#                     msg = 'Invalid action!'

#             except mysql.connector.Error as err:
#                 msg = f"Database error: {err}"

#             finally:
#                 cursor.close()
#                 close_database_connection(connection)

#         return redirect(url_for('doctors'))

#     return redirect(url_for('login'))













# @app.route('/save_book',methods=['POST'])
# def save_book():
#     msg = ''    
#     if 'loggedin' in session:
#         if request.method == 'POST':
#             name = request.form['name'] 
#             isbn = request.form['isbn']  
#             action = request.form['action']
 
#             # if action == 'updateBook':
#             #     bookid = request.form['bookid']
#             #     book = Books.query.get(bookid)
             
#             #     book.name = name
#             #     book.isbn = isbn
 
#             #     db.session.commit()
#             #     print("UPDATE book") 
#             # else:
#             #     file = request.files['uploadFile']
#             #     filename = secure_filename(file.filename)
#             #     print(filename)
#             #     if file and allowed_file(file.filename):
#             #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             #         filenameimage = file.filename
 
#             #         book = Books(name=name, picture=filenameimage, isbn=isbn)
#             #         db.session.add(book)
#             #         db.session.commit()
#             #         print("INSERT INTO book")  
#             #     else:
#             #         msg  = 'Invalid Uplaod only png, jpg, jpeg, gif'
#             # return redirect(url_for('books'))        
#         elif request.method == 'POST':
#             msg = 'Please fill out the form !'       
#         return render_template("books.html", msg = msg)
#     return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)



#Note: Remember to create doctype for ADMINS