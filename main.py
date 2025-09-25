import json
from fastapi import FastAPI, Path, HTTPException, Query

app = FastAPI()  # Create an app instance

def load_data():                            #helper function that loads the data from json.file
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

#Endpoints
@app.get("/")                                                                    #get method to view/retrive CRUD -> R
def hello():
    return {"message": "Hello there, you alright?"}

@app.get("/about")
def about():
    return {'message':'A complete solution to manage your patients records'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_data(
    patient_id: int = Path(                                               # Using Path to get a perticular data 
        ...,   
        description="ID of a particular patient in the database", 
        ge=1,  # must be >= 1
        example=3
    )
):
    data = load_data()  # load all data
    patients = data["patients"]  # extract list of patients
    
    for patient in patients:
        if patient["id"] == patient_id:
            return patient
    
    raise HTTPException(status_code=404, detail="Data/Patient not found")  # raising custom error with HTTPException

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(
        "age",
        description="Field to sort by (currently supports 'age')"
    ),
    order: str = Query(
        "asc",
        description="Sort order: 'asc' or 'desc'"
    ),
    gender: str | None = Query(
        None,
        description="Optional filter: 'Male' or 'Female'"
    )
):
    data = load_data()
    patients = data["patients"]

    # Optional filtering by gender
    if gender:
        gender = gender.capitalize()  # normalize input
        if gender not in ["Male", "Female"]:
            raise HTTPException(status_code=400, detail="Invalid gender filter")
        patients = [p for p in patients if p["gender"] == gender]

    # Sorting
    if sort_by not in ["age", "gender"]:
        raise HTTPException(status_code=400, detail="Can only sort by 'age' or 'gender'")

    reverse = True if order == "desc" else False
    sorted_data = sorted(patients, key=lambda x: x[sort_by], reverse=reverse)

    return sorted_data