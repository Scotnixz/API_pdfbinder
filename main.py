from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from scripts import Binder_Pdf
from pathlib import Path

app = FastAPI()

@app.post("/generate-pdf/")
def generate_pdf(
    state: str = Form(...),
    city: str = Form(...),
    zip_code: str = Form(...),
    full_name: str = Form(...),
    address: str = Form(...),
    new_policy_start_date: str = Form(...),
    vehicle_year: str = Form(...),
    vehicle_make: str = Form(...),
    vehicle_model: str = Form(...),
    vehicle_vin: str = Form(...),
    lienholder: bool = Form(False),
    lien_name: str = Form(""),
    lien_address: str = Form(""),
    lien_city_state_zip: str = Form(""),
):
    
    city_state_zip = (f"{city} {state} {zip_code}").upper()



    binder = Binder_Pdf(
        state, full_name, address, city_state_zip, new_policy_start_date,
        vehicle_year, vehicle_make, vehicle_model, vehicle_vin,
        lienholder, lien_name, lien_address, lien_city_state_zip
    )

    binder.insert_info()

    output_dir = Path("output_pdfs")
    output_dir.mkdir(exist_ok=True)
    file_name = output_dir / f"binder{full_name[0]}.pdf"
    binder.salvar(file_name)

    return FileResponse(path=file_name, filename="generated_policy.pdf", media_type="application/pdf")
