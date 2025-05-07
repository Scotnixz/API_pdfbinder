import fitz
import random
from info import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path


class Pdfs:
    def __init__(self, archive):
        self.archive = archive
        self.doc = fitz.open(archive)

    def salvar(self, name_archive):
        self.doc.save(name_archive)
        self.doc.close()

class Binder_Pdf(Pdfs):
    def __init__(self, state, full_name, address, city_state_zip, new_policy_start_date,
                 vehicle_year, vehicle_make, vehicle_model, vehicle_vin,
                 lienholder=False,
                 lien_name="", lien_address="", lien_city_state_zip=""):
        
        base_dir = Path(__file__).resolve().parent
        archive_pdf = base_dir / "templates_certo" / f"binder-{state.upper()}.pdf"   
        if not archive_pdf.exists():
            raise FileNotFoundError(f"Template for state {state} not found in templates_certo directory.")  
             
        super().__init__(archive_pdf)
        self.page = self.doc[0]
        self.state = state.upper()
        self.policy_number = first_numbers_policy[self.state] + str(random.randint(100, 999))
        # Ajusta a data da policy para os estados que precisam de 12 meses e deixar 6 como padrão.
        self.policy_range = relativedelta(months=6)
        if self.state in ["NY", "GA"]:
            self.policy_range = relativedelta(months=12)
        
        self._exp_date = datetime.strptime(new_policy_start_date, "%m/%d/%y") + relativedelta(days=10)
        self.exp_date = self._exp_date.strftime("%m-%d-%y")
        self.eff_date = (self._exp_date - self.policy_range).strftime("%m-%d-%y")
        if lienholder:
            self.lienholder = "X"
        else: 
            self.lienholder = ""

        self.data = {
            "full_name": full_name.upper(),
            "address": address.upper(),
            "city_state_zip": city_state_zip.upper(),
            "num_policy": self.policy_number,
            "date_exp": self.exp_date,
            "date_end": self.eff_date,
            "vehicle_year": vehicle_year,
            "vehicle_make": vehicle_make.upper(),
            "vehicle_model": vehicle_model.upper(),
            "vehicle_vin": vehicle_vin.upper(),
            "lienholder_name": lien_name.upper(),
            "lienholder_street": lien_address.upper(),
            "lienholder_city_state_zip": lien_city_state_zip.upper(),
            "lienholder_bool": self.lienholder,
            "issued_date": self.exp_date,
        }

    def insert_info(self):
        coords = CORDS_BINDER[self.state]
        for campo, valor in self.data.items():
            if campo in coords:
                coord = coords[campo]
                self.page.insert_text(coord["pos"], valor, fontsize=coord["fontsize"],
                                      fontname="helv", color=(0, 0, 0))
