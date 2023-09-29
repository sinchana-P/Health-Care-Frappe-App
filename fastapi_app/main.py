from fastapi import APIRouter,FastAPI
from api import api,doctors,patients
# from apps.fastapi_app.api import patients
# from db_config import db_config 

app = FastAPI()

app.include_router(api.user_router)
app.include_router(doctors.doctor_router)
app.include_router(patients.patient_router)


# Include the doctor_router in the main app
# app.include_router(doctor_router)
# app.include_router(patient_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="192.168.1.99", port=8000)







# from fastapi import FastAPI

# app = FastAPI()


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="192.168.1.99", port=8000)

#   http://192.168.1.99:8000/docs
#  uvicorn main:app --host='192.168.1.99' --port=8000 --reload