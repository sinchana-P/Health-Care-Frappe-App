# -------------------- DOCTOR'S API'S------------------

from fastapi import FastAPI, HTTPException, status, APIRouter, Depends
from pydantic import BaseModel
import mysql.connector

# app = FastAPI()
doctor_router = APIRouter()

# Database connection parameters
db_config = {
    "host": "localhost",
    "user": "sinch",
    "password": "Sinchu@333",
    "database": "_14796a9152410a05",
}

# Define a function to establish a database connection
def get_database_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        yield connection
    finally:
        connection.close()

# Create a data model for doctor information
class Doctor(BaseModel):
    contact: str
    specialization: str
    qualification: str
    license: str
    availability: str
    doctor_name: str
    department: str

#1. API to fetch all doctors
@doctor_router.get("/doctors")
async def get_doctors(db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tabDoctor")
        doctors = cursor.fetchall()
        return doctors
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

#2. API to fetch a particular doctor by ID
@doctor_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tabDoctor WHERE name = %s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )
        return doctor
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

#3. API to create a new doctor
@doctor_router.post("/doctors", status_code=status.HTTP_201_CREATED)
async def create_doctor(doctor: Doctor, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor()
        insert_query = "INSERT INTO tabDoctor (name, contact, specialization, qualification, license, availability, doctor_name, department) VALUES (1234, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            doctor.contact,
            doctor.specialization,
            doctor.qualification,
            doctor.license,
            doctor.availability,
            doctor.doctor_name,
            doctor.department,
        )
        cursor.execute(insert_query, values)
        db.commit()
        return {"message": "Doctor created successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

#4. API to update doctor information by ID
@doctor_router.put("/doctors/{doctor_id}")
async def update_doctor(doctor_id: str, doctor: Doctor, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor()
        update_query = "UPDATE tabDoctor SET contact=%s, specialization=%s, qualification=%s, license=%s, availability=%s, doctor_name=%s, department=%s WHERE name=%s"
        values = (
            doctor.contact,
            doctor.specialization,
            doctor.qualification,
            doctor.license,
            doctor.availability,
            doctor.doctor_name,
            doctor.department,
            doctor_id,
        )
        cursor.execute(update_query, values)
        db.commit()
        return {"message": "Doctor updated successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

#5. API to delete a doctor by ID
@doctor_router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor()
        delete_query = "DELETE FROM tabDoctor WHERE name = %s"
        cursor.execute(delete_query, (doctor_id,))
        db.commit()
        return {"message": "Doctor deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

#6.  API to search for doctors by name or specialization
@doctor_router.get("/doctors/search")
async def search_doctors(query: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor(dictionary=True)
        search_query = "SELECT * FROM tabDoctors WHERE doctor_name LIKE %s OR specialization LIKE %s"
        values = (f"%{query}%", f"%{query}%")
        cursor.execute(search_query, values)
        matched_doctors = cursor.fetchall()
        if not matched_doctors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching doctors found",
            )
        return matched_doctors
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

# Include the doctor_router in the main app
# app.include_router(doctor_router)


# Include the doctor_router in the main app
# app.include_router(doctor_router)


# ----------- search doctor --------

# 6.a   API to search for doctors by name or specialization
# @app.get("/doctors/search")
# async def search_doctors(query: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
#     try:
#         cursor = db.cursor(dictionary=True)
#         search_query = "SELECT * FROM tabDoctors WHERE LOWER(doctor_name) LIKE LOWER(%s) OR LOWER(specialization) LIKE LOWER(%s)"
#         search_query = "SELECT * FROM tabDoctors WHERE doctor_name LIKE %s OR specialization LIKE %s"
#         values = (f"%{query}%", f"%{query}%")
#         cursor.execute(search_query, values)
#         matched_doctors = cursor.fetchall()  
            
#         if not matched_doctors:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No matching doctors found",
#             )
        
#         return matched_doctors
#     except mysql.connector.Error as err:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database error: {err}",
#         )
#     finally:
#         cursor.close()


#6.b API to search for doctors by name or specialization (case-insensitive)
# @app.get("/doctors/search")
# async def search_doctors(query: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
#     try:
#         cursor = db.cursor(dictionary=True)
#         search_query = "SELECT * FROM tabDoctors WHERE LOWER(doctor_name) LIKE %s OR LOWER(specialization) LIKE %s"
#         query = f"%{query.lower()}%"  # Convert query to lowercase for comparison
#         values = (query, query)
#         cursor.execute(search_query, values)
#         matched_doctors = cursor.fetchall()
#         return matched_doctors
#     except mysql.connector.Error as err:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database error: {err}",
#         )
#     finally:
#         cursor.close()



#6.c API to search for doctors by name or specialization (case-insensitive)
# @app.get("/doctors/search")
# async def search_doctors(query: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
#     try:
#         cursor = db.cursor(dictionary=True)
#         search_query = "SELECT * FROM tabDoctors WHERE LOWER(doctor_name) LIKE %s OR LOWER(specialization) LIKE %s"
#         query = f"%{query.lower()}%"  # Convert query to lowercase for comparison
#         values = (query,)
#         print("Search Query:", search_query)
#         print("Search Value:", query)
#         cursor.execute(search_query, values)
#         matched_doctors = cursor.fetchall()
#         print("Matched Doctors:", matched_doctors)
#         return matched_doctors
#     except mysql.connector.Error as err:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database error: {err}",
#         )
#     finally:
#         cursor.close()



# app = FastAPI()
# doctor_router = APIRouter()

# Set up logging
# logging.basicConfig(level=logging.DEBUG)


# # Define a function to establish a database connection
# def get_database_connection():
#     try:
#         connection = mysql.connector.connect(**db_config)
#         yield connection
#     finally:
#         connection.close()

# # ... (Other code remains the same)

#6.d API to search for doctors by name or specialization (case-insensitive)
# @app.get("/doctors/search")
# async def search_doctors(query: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
#     try:
#         cursor = db.cursor(dictionary=True)
#         search_query = "SELECT * FROM tabDoctors WHERE LOWER(doctor_name) LIKE %s OR LOWER(specialization) LIKE %s"
#         query = f"%{query.lower()}%"  # Convert query to lowercase for comparison
#         values = (query, query)
#         logging.debug("Search Query: %s", search_query)
#         logging.debug("Search Value: %s", query)
#         cursor.execute(search_query, values)
#         matched_doctors = cursor.fetchall()
#         logging.debug("Matched Doctors: %s", matched_doctors)
#         return matched_doctors
#     except mysql.connector.Error as err:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database error: {err}",
#         )
#     finally:
#         cursor.close()


