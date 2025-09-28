from pydantic import BaseModel, EmailStr, AnyUrl, constr, Field, field_validator, model_validator, computed_field
from typing import List,Dict, Optional, Annotated
# Step-1: create class with basemodel to validate


class Contact(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{10,15}$')  # optional +, then 10–15 digits
    website: Optional[AnyUrl] = None
    emergency_contact: Optional[str] = None  # add this so we can validate for seniors

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
    weight: float #kg
    height: float #metre
    married: Optional[bool] = None
    allergies: List[str]
    contact: Contact

    # Cross-field validation (runs after fields are parsed)
    @model_validator(mode='after')
    def validate_age_and_weight(self):
        if self.age > 60 and not (self.contact and self.contact.emergency_contact):
            raise ValueError('Patients over 60 must have an emergency_contact.')
        if self.weight > 250:
            raise ValueError('Patient weight should not be more than 250 kg')
        return self
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2),2)

def insert_Patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.weight)
    print(patient.married)
    print(patient.allergies)
    print(patient.contact)
    print('BMI : ',patient.bmi)
    print('Inserted')

#step-2: the data
patient_info = {'name':'john doe', 'age':30, 'weight': 85.0, 'height': 1.7145,   'allergies':['pollen', 'dust'], 'contact':{'email': 'aj.sh@gfm.co.uk', 'phone':'00000000000',  "website": "https://example.com" }}


patient1 = Patient(**patient_info)         # ** to unpack dictionary

insert_Patient_data(patient1) 

temp = patient1.model_dump()

print(temp)
print(type(temp))

# Get JSON string instead of dict
print(patient1.model_dump_json())

# Get JSON Schema (for documentation / validation)
print(Patient.model_json_schema())