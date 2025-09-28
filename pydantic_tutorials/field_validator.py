from pydantic import BaseModel, EmailStr, AnyUrl, constr, Field, field_validator
from typing import List,Dict, Optional, Annotated
# Step-1: create class with basemodel to validate


class Contact(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{10,15}$') # optional +, then 10–15 digits
    website: Optional[AnyUrl] = None

        # Validate that email domain is allowed
    @field_validator('email')
    @classmethod
    def check_domain(cls, v: EmailStr) -> EmailStr:
        allowed = {'hsbc.co.uk', 'gfm.co.uk'}
        domain = v.split('@', 1)[-1].lower()
        if domain not in allowed:
            raise ValueError('Email must be from hsbc.co.uk or gfm.co.uk')
        return v

class Patient(BaseModel):
    name: str
    age: int
    weight: float
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