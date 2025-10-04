import json
from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import date
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, List, Optional

app = FastAPI()  # Create an app instance


# ---- Model for patient notes ----
class Note(BaseModel):
    note_id: Annotated[int, Field(..., ge=1, description="Note ID")]
    doctor: Annotated[str, Field(..., min_length=1, description="Doctor name")]
    date: Annotated[date, Field(..., description="Date in YYYY-MM-DD format")]
    content: Annotated[str, Field(..., min_length=1, description="Doctor's note")]

class Patient(BaseModel):
    id: Annotated[int, Field(..., ge=1, description="Unique patient ID")]
    name: Annotated[str, Field(..., min_length=1, description="Full Name of the patient")]
    age: Annotated[int, Field(..., ge=0, le=120, description="Age of the patient")]
    height: Annotated[float, Field(..., gt=0, le=2.5, description="Height in metres")]
    weight: Annotated[float, Field(..., gt=0, le=300, description="Weight in kg")]
    gender: Annotated[Literal['Male', 'Female'], Field(..., description="Gender of the patient")]
    notes: List[Note] = Field(default_factory=list)


    # ---- Auto-calculated BMI ----
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    # ---- Auto-calculated Verdict ----
    @computed_field
    @property
    def verdict(self) -> Literal['Underweight', 'Normal', 'Overweight', 'Obese']:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        return "Obese"

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    height: Optional[float] = Field(None, gt=0, le=2.5)
    weight: Optional[float] = Field(None, gt=0, le=300)
    gender: Optional[Literal["Male", "Female"]] = None
    notes: Optional[List[Note]] = None  # optional full replacement of notes list


 #helper function that loads the data from json.file
def load_data():                           
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

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.post("/add")
def add_patient(patient: Patient):
    data = load_data()

    # check if patient with same ID already exists
    for p in data["patients"]:
        if p["id"] == patient.id:
            raise HTTPException(status_code=400, detail="Patient with this ID already exists")

    # add new patient
    data["patients"].append(patient.model_dump(mode="json"))  # model_dump() is Pydantic v2

    #save the inro database
    save_data(data)

    return JSONResponse(status_code=201, content={
    "message": "Patient added successfully",
    "patient": patient.model_dump(mode="json")
    })

# Update/ Add new note 
@app.post("/patient/{patient_id}/note")
def add_note(
    patient_id: int = Path(..., ge=1, description="ID of the patient to add a note for"),
    new_note: Note = ...
):
    data = load_data()
    patients = data.get("patients", [])

    # find the patient by ID
    for p in patients:
        if p["id"] == patient_id:
            # make sure note_id is unique for that patient
            existing_ids = [n["note_id"] for n in p["notes"]]
            if new_note.note_id in existing_ids:
                raise HTTPException(status_code=400, detail=f"Note ID {new_note.note_id} already exists for this patient.")

            # append note (convert to JSON-safe dict)
            p["notes"].append(jsonable_encoder(new_note))

            save_data(data)
            return {
                "message": f"Note {new_note.note_id} added successfully for patient {p['name']}.",
                "patient_id": patient_id,
                "total_notes": len(p["notes"])
            }

    raise HTTPException(status_code=404, detail="Patient not found")


@app.put("/edit/{patient_id}")
def update_patient(
    patient_id: int = Path(..., ge=1, description="ID of the patient to update"),
    patient_update: PatientUpdate = ...
):
    data = load_data()
    patients = data.get("patients", [])

    # find the patient index
    idx = -1
    for i, p in enumerate(patients):
        if p["id"] == patient_id:
            idx = i
            break

    if idx == -1:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = patients[idx]                       # current dict
    updates = patient_update.model_dump(exclude_unset=True, exclude_none=True)


    # merge (incoming fields overwrite existing)
    merged = {**existing, **updates}

    # validate with full model (recomputes computed fields)
    try:
        updated = Patient(**merged)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # persist back (JSON-safe, dates → strings)
    patients[idx] = updated.model_dump(mode="json")
    data["patients"] = patients
    save_data(data)

    return {
        "message": f"Patient {patient_id} updated successfully.",
        "patient": updated
    }


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: int ):

    #load data
    data = load_data()
    patients = data.get("patients", [])

    # find the patient index
    idx = -1
    for i, p in enumerate(patients):
        if p["id"] == patient_id:
            idx = i
            break

    if idx == -1:
        raise HTTPException(status_code=404, detail="Patient not found")
    

    # Save patient's name before deletion for message
    deleted_name = patients[idx]["name"]


    # remove the patient from the list
    del patients[idx]

    # save the inro database
    save_data(data)

    return JSONResponse(status_code=200, content={"message": f"Patient {patient_id}- {deleted_name} deleted successfully."})