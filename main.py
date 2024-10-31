from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.encounter import Encounter
from starlette.middleware.sessions import SessionMiddleware
import requests

settings = {
    "app_id": "d08c0a04-367c-4ece-9498-8b6057eee8d4",
    "api_base": "https://gw.interop.community/TestSandboxManzi/data",
    "redirect_uri": "http://127.0.0.1:8000/cerner/token",
    "scope": "launch/patient patient/*.read patient/*.write openid profile",
    "client_secret": "J6ZKzNgy2DkiE3cTrqjXGYgHKdY0l1ztFzJKTIgy4KfyqERsfT4uaRAtqq5UQkVGHbnAtq46FpzA0PDjuf33Aw"
}

cerner = client.FHIRClient(settings=settings)
cerner.prepare()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

@app.get("/")
def documentation():
    return RedirectResponse(url="/docs")

@app.get("/cerner/patient/all")
def get_all_patients():
    print(cerner.authorize())
    search = Patient.where(struct={})
    patients = search.perform_resources(cerner.server)
    return {"patients": [patient.as_json() for patient in patients]}

@app.get("/cerner/patient")
def get_patient(request: Request):
    bearer_token = request.headers.get("Authorization").split(" ")[1]
    response = requests.get(f"{settings['api_base']}/Patient", headers={"Authorization": f"Bearer {bearer_token}"})
    patients = response.json()["entry"]
    return {"patients": patients}

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

@app.get("/cerner/practitioner")
def get_practitioner(request: Request):
    bearer_token = request.headers.get("Authorization").split(" ")[1]
    response = requests.get(f"{settings['api_base']}/Practitioner", headers={"Authorization": f"Bearer {bearer_token}"})
    practitioners = response.json()["entry"]
    return {"practitioners": practitioners}

@app.get("/cerner/authorize")
def get_authorize():
    return RedirectResponse(url=cerner.server.authorize_uri)

@app.get("/cerner/token")
def get_token(request: Request):
    code = request.query_params.get("code")

    response = requests.post(
        "https://iol2auth.interop.community/token", 
        data = {
                "grant_type": "authorization_code", 
                "code": code, 
                "redirect_uri": settings["redirect_uri"]
            },
        auth=(settings["app_id"], settings["client_secret"])
    )

    return response.json()