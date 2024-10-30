from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.encounter import Encounter

settings = {
    "app_id": "7050fb07-90d0-4b0b-8cf1-9a1a88c9f6d9",
    "api_base": "https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
}

cerner = client.FHIRClient(settings=settings)
cerner.prepare()

app = FastAPI()

@app.get("/")
def documentation():
    # redirect to /docs
    return RedirectResponse(url="/docs")

@app.get("/cerner/patient/{patient_id}")
def get_patient(patient_id: str):
    patient = Patient.read(patient_id, cerner.server)
    return patient.as_json()

@app.get("/cerner/encounter/search")
def search_encounter():
    search = Encounter.where(struct={'subject': '12724066', 'status': 'finished'})
    encounters = search.perform_resources(cerner.server)
    return {"encounters": [encounter.as_json() for encounter in encounters]}

@app.get("/cerner/patient/search")
def search_patient():
    search = Patient.where(struct={'family': 'smart', 'given': 'joe', 'birthdate': '1990-09-15'})
    patients = search.perform_resources(cerner.server)
    return {"patients": [patient.as_json() for patient in patients]}