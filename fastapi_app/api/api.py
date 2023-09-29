from fastapi import APIRouter, HTTPException, status, Depends, FastAPI
from pydantic import BaseModel
import mysql.connector
import logging

# Create an instance of the APIRouter
user_router = APIRouter()
# app = FastAPI()

# Database connection parameters
db_config = {
    "host": "localhost",
    "user": "sinch",
    "password": "Sinchu@333",
    "database": "_14796a9152410a05",
}

# # Create a FastAPI app
# app = FastAPI()

# Define a function to establish a database connection
def get_database_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        yield connection
    finally:
        connection.close()

# Define a data model for user registration
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str

# 1. API to egister User
@user_router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        # Check if the username already exists in the database
        query_check_username = "SELECT user_name FROM tabHealth_Care_Users WHERE user_name = %s"
        values_check_username = (user.username,)

        cursor = db.cursor()
        cursor.execute(query_check_username, values_check_username)
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists. Choose a different username.",
            )

        # Insert the new user into the 'tabHealth_Care_Users' table
        query_insert_user = "INSERT INTO tabHealth_Care_Users (name, user_name, email, password) VALUES (uuid(), %s, %s, %s)"
        values_insert_user = (user.username, user.email, user.password)

        cursor.execute(query_insert_user, values_insert_user)
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

    return {"message": "User registered successfully"}


#2. Define a data model for user login
class UserLogin(BaseModel):
    username: str
    email: str
    password: str

#2. API to Login User
@user_router.post("/api/login")
async def login_user(user: UserLogin, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        # Check if the username and password match a record in the database
        query_check_user = "SELECT user_name,email, password FROM tabHealth_Care_Users WHERE user_name = %s AND email = %s AND password = %s"
        values_check_user = (user.username, user.email, user.password)

        cursor = db.cursor()
        cursor.execute(query_check_user, values_check_user)
        result = cursor.fetchone()

        if result:
            return {"message": "Login successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed. Please check your username and password.",
            )
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()


#3. app.include_router(user_router)

#3. API to fetch all Users
@user_router.get("/api/getUsers")
async def get_users(db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        query_get_users = "SELECT user_name, email FROM tabHealth_Care_Users"
        
        cursor = db.cursor()
        cursor.execute(query_get_users)
        
        # Fetch all users as a list of dictionaries
        users = []
        for user_data in cursor.fetchall():
            user = {
                "user_name": user_data[0],
                "email": user_data[1]
            }
            users.append(user)
            print(users)
        
        return users
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()



# # -------------------- DOCTOR'S API'S ------------------
# # -------------------- PATIENT'S API  ------------------


