from flask import Flask,Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import re
import mysql.connector
import os  # Add this line to import the 'os' module
from werkzeug.utils import secure_filename  # Add this line to import the 'secure_filename' function
# routes/doctors.py

from config.database import get_database_connection, close_database_connection

from flask import Flask
from flask_bcrypt import Bcrypt

from routes.doctors import doctors_bp
from routes.medicines import medicines_bp
from routes.labtests import labtests_bp
from routes.departments import departments_bp
from routes.patients import patients_bp
from routes.billing import billing_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
bcrypt = Bcrypt(app)

app.register_blueprint(doctors_bp)
app.register_blueprint(medicines_bp)
app.register_blueprint(labtests_bp)
app.register_blueprint(departments_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(billing_bp)

# # Database connection parameters
# db_config = {
#     "host": "localhost",
#     "user": "sinch",
#     "password": "Sinchu@333",
#     "database": "_14796a9152410a05",
# }

# def get_database_connection():
#     connection = mysql.connector.connect(**db_config)
#     return connection

# def close_database_connection(connection):
#     connection.close()


# # Add this line to set up the upload folder
# app.config['UPLOAD_FOLDER'] = 'static/images'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Add this line to define allowed file extensions


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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



if __name__ == '__main__':
    app.run(debug=True)

        
    
#Note: Remember to create doctype for ADMINS