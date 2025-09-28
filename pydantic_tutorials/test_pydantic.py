from pydantic import BaseModel, EmailStr, AnyUrl, constr, Field
from typing import List,Dict, Optional, Annotated
# Step-1: create class with basemodel to validate


class Contact(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{10,15}$') # optional +, then 10–15 digits
    website: Optional[AnyUrl] = None

class Patient(BaseModel):
    name: Annotated[str, Field(max_length= 50, title='full Name of the patient', description='name should not be more than 50 chracters', examples='jhon doe')]
    age: int
    weight: Annotated[float, Field(gt=0, strict = True)] # with strict pydantic will follow float strictly '78.0' = not allowed 
    married: Optional[bool] = None
    allergies: List[str]
    contact: Contact



def insert_Patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.weight)
    print(patient.married)
    print(patient.allergies)
    print(patient.contact)
    print('Inserted')

#step-2: the data
patient_info = {'name':'john doe', 'age':30, 'weight': 78.0,  'allergies':['pollen', 'dust'], 'contact':{'email': 'aj.sh@cp.com', 'phone':'00000000000',  "website": "https://example.com" }}


patient1 = Patient(**patient_info)         # ** to unpack dictionary

insert_Patient_data(patient1) 