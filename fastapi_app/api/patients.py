from fastapi import FastAPI, HTTPException, status, APIRouter, Depends
from pydantic import BaseModel
import mysql.connector

# app = FastAPI()
patient_router = APIRouter()

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

# Create a data model for patient information
class Patient(BaseModel):
    patient_name: str
    email: str = None
    address: str = None
    dob: str = None
    gender: str = None
    medical_history: str = None
    current_medications: str = None

# 1. API to fetch all patients
@patient_router.get("/patients")
async def get_patients(db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tabPatient")
        patients = cursor.fetchall()
        return patients
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

# 2. API to fetch a particular patient by ID
@patient_router.get("/patients/{patient_id}")
async def get_patient(patient_id: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tabPatient WHERE name = %s", (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )
        return patient
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

# 3. API to create a new patient
@patient_router.post("/patients", status_code=status.HTTP_201_CREATED)
async def create_patient(patient: Patient, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor()
        insert_query = "INSERT INTO tabPatient (name, patient_name, email, address, dob, gender, medical_history, current_medications) VALUES (uuid() , %s, %s, %s, %s, %s, %s, %s)"
        values = (
            patient.patient_name,
            patient.email,
            patient.address,
            patient.dob,
            patient.gender,
            patient.medical_history,
            patient.current_medications,
        )
        cursor.execute(insert_query, values)
        db.commit()
        return {"message": "Patient created successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

# 4. API to update patient information by ID
@patient_router.put("/patients/{patient_id}")
async def update_patient(
    patient_id: str,
    patient: Patient,
    db: mysql.connector.MySQLConnection = Depends(get_database_connection)
):
    try:
        cursor = db.cursor()
        update_query = "UPDATE tabPatient SET patient_name=%s, email=%s, address=%s, dob=%s, gender=%s, medical_history=%s, current_medications=%s WHERE name=%s"
        values = (
            patient.patient_name,
            patient.email,
            patient.address,
            patient.dob,
            patient.gender,
            patient.medical_history,
            patient.current_medications,
            patient_id,
        )
        cursor.execute(update_query, values)
        db.commit()
        return {"message": "Patient updated successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()

# 5. API to delete a patient by ID
@patient_router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str, db: mysql.connector.MySQLConnection = Depends(get_database_connection)):
    try:
        cursor = db.cursor()
        delete_query = "DELETE FROM tabPatient WHERE name = %s"
        cursor.execute(delete_query, (patient_id,))
        db.commit()
        return {"message": "Patient deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}",
        )
    finally:
        cursor.close()











