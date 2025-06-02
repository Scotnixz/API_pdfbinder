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
        archive_pdf = base_dir / "templates_binder" / f"binder-{state.upper()}.pdf"   
        if not archive_pdf.exists():
            raise FileNotFoundError(f"Template for state {state} not found in templates_binder directory.")  
             
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
            "date_exp": self.eff_date,
            "date_end": self.exp_date,
            "vehicle_year": vehicle_year,
            "vehicle_make": vehicle_make.upper(),
            "vehicle_model": vehicle_model.upper(),
            "vehicle_vin": vehicle_vin.upper(),
            "lienholder_name": lien_name.upper(),
            "lienholder_street": lien_address.upper(),
            "lienholder_city_state_zip": lien_city_state_zip.upper(),
            "lienholder_bool": self.lienholder,
            "issued_date": self.eff_date,
        }

    def insert_info(self):
        coords = CORDS_BINDER[self.state]
        for campo, valor in self.data.items():
            if campo in coords:
                coord = coords[campo]
                self.page.insert_text(coord["pos"], valor, fontsize=coord["fontsize"],
                                      fontname="helv", color=(0, 0, 0))

class GaragingProof(Pdfs):
    def __init__(self, state, full_name, address, city_state_zip, new_policy_start_date):
        
        self.cords1 = []
        self.cords2 = []
        self.data1 = {}
        self.data2 = {}
        self.bill_1 = ""
        self.bill_2 = ""

        base_dir = Path(__file__).resolve().parent
        
        archive_1 = base_dir / "address_template" / f"1-{state.upper()}.pdf"
        archive_2 = base_dir / "address_template" / f"2-{state.upper()}.pdf"

        self.doc1 = fitz.open(archive_1)
        self.doc2 = fitz.open(archive_2)

        if not archive_1.exists() or not archive_2.exists():
            raise FileNotFoundError(f"Missing template(s) for state {state}.")

        for page in [*self.doc1, *self.doc2]:
            for name in fonts.keys():
                page.insert_font(name, fontfile=fonts[name])

        self.policy_date = datetime.strptime(new_policy_start_date, "%m/%d/%y")
        self.full_name_split = full_name.lower().split()
        full_name_format = [palavra.capitalize() for palavra in self.full_name_split]
        full_name_capitalized = " ".join(full_name_format)
        bill_start = (self.policy_date - relativedelta(months=2)).replace(day=15)
        bill_end = (self.policy_date - relativedelta(months=1)).replace(day=15)
        last_year_date = bill_end - relativedelta(years=1)
        last_year = last_year_date.strftime("%y")
        bill_payment = (bill_end + relativedelta(months=1)).replace(day=13)
        abr_month_payment = bill_payment.strftime("%b")
        abr_month_start = bill_start.strftime("%b")
        month_start = bill_start.strftime("%B")
        abr_month_end = bill_end.strftime("%b")
        month_end = bill_end.strftime("%B")
        year_payment = bill_payment.strftime("%Y")
        year_start = bill_start.strftime("%Y")
        year_start_2 = bill_start.strftime("%y")
        year_end = bill_end.strftime("%Y")
        year_end_2 = bill_end.strftime("%y")
        next_year = bill_end + relativedelta(years=1)
        next_year = next_year.strftime("%Y")
        start_date_month_num = bill_start.strftime("%m")
        last_payment_date = bill_start - relativedelta(month=1)
        last_payment_month = last_payment_date.strftime("%m")
        next_meter_date = (self.policy_date).replace(day=20)
        next_meter_month = next_meter_date.strftime("%B")
        next_meter_month2 = next_meter_date.strftime("%b")
        year_next_meter = next_meter_date.strftime("%Y")
        year_next_meter2 = next_meter_date.strftime("%y")



        
        self.state = state.upper()

        if self.state == "MA":
            account_number_xfinity = f"8773 10 291 {random.randint(1000000, 9999999)}"
            self.cords1 = NATIONAL_GRID_MA
            self.cords2 = XFINITY_MA
            self.bill_1 = "NATIONAL_GRID_"
            self.bill_2 = "XFINITY_"
            
            self.data1 = {
            "full_name": full_name.upper(),
            "address": address.upper(),
            "city_state_zip": city_state_zip.upper(),
            "billing_period": f"{abr_month_start} 15, {year_start} to {abr_month_end} 15, {year_end}",
            "account_number": f"37{random.randint(100, 999)}-{random.randint(10000, 99999)}",
            "payment_date": f"{abr_month_payment} 13, {year_payment}",
            "date_bill_issued": f"{abr_month_end} 20, {year_end}", #Esse eu tenho que colocar as cordenadas ainda
            "service_period": f"{abr_month_start} 15 - {abr_month_end} 15",
            "previous_reading_dt": f"{abr_month_start} 1",
            "month_history": f"{abr_month_end} {last_year}"


            }
            self.data2 = {
            "account_number": account_number_xfinity,
            "billing_date": f"{abr_month_end} 11, {year_end}",
            "services_from": f"{abr_month_start} 18, {year_start} to {abr_month_end} 17, {year_end}",
            "title_name": f"Hello {full_name_capitalized},",
            "full_address": f"For {address.upper()}, {city_state_zip.upper()}",
            "last_payment_dt": f"{abr_month_start} 26",
            "description": f"Your automatic payment on {abr_month_end} 25, {year_end}, will include your",
            "automatic_payment": f"{abr_month_end} 25, {year_end}",
            "bold_description": f"Credit card payment will be applied {abr_month_end} 25, {year_end}",
            "full_name": full_name.upper(),
            "address": address.upper(),
            "city_state_zip": city_state_zip.upper(),
            "account_number_lower": f"{account_number_xfinity}000{random.randint(10000, 99999)}",
            "promotional_discount": f"end on Dec 17, {year_end}. The remainder of your discount will expire when your promotion",
            "promotional_discount2": f"ends on Dec 17, {next_year}.",
            }

        elif self.state == "NJ":
            account_number_var = random.randint(100000, 999999)
            account_number_var2 = random.randint(10, 99)
            account_number_var3 = random.randint(1, 9)
            account_number_var4 = random.randint(1, 9)
            account_number_var5 = random.randint(1000, 9999)
            account_number_var6 = random.randint(100, 999)
            
            due_date_solution = f"{month_start} 30, {year_start}"
            while len(due_date_solution) < 18:
                void_str = " "
                due_date_solution = void_str + due_date_solution

            self.cords1 = OPTIMUM_NJ
            self.cords2 = PSEG_NJ
            self.bill_1 = "OPTIMUM_"
            self.bill_2 = "PSEG_"
            
            self.data1 = {
                "account_number": f"07844-{account_number_var}-{account_number_var2}-{account_number_var3}",
                "full_name": full_name.upper(),
                "address": address.upper(),
                "city_state_zip": city_state_zip.upper(),
                "billing_period": f"{abr_month_start}/16 - {abr_month_end}/15",
                "due_date": f"{month_start} 30, {year_start}",	
                "includes_payment": f"{start_date_month_num}/13/{year_start_2}",
                "total_amount": f"{month_start} 30, {year_start}",
                "account_different": f"07844  {account_number_var}  {account_number_var2}  {account_number_var3}     {account_number_var4}  00{account_number_var5}",
                "due_date_solution": due_date_solution,
                "last_payments": f"{last_payment_month}/27",
                "one_time_activity": f"{last_payment_month}/18",
                "one_time_activity2": f"{last_payment_month}/20",
                }
        
            self.data2 = {
                "pay_by": f"{abr_month_end}\u00A028,\u00A0{year_end}",
                "bill_date": f"{month_end} 20, {year_end}",
                "period": f"{month_start} 27, {year_start} to {month_end} 26, {year_end}",
                "total_amount": f"{month_end}\u00A028,\u00A0{year_end}",
                "name": f"{full_name.upper()}",
                "account_number1": f"77 051 {account_number_var6} {account_number_var2}",
                "address": address.upper(),
                "city_state_zip": city_state_zip.upper(),
                "next_meter": f"{next_meter_month}\u00A020,\u00A0{year_next_meter}",
                "account_number2": f"77051{account_number_var6}{account_number_var2}",
                "account_number_ocr": f"77051{account_number_var6}{account_number_var2} 0000246875 000015021{account_number_var2}",
            }
            
            full_name_width_font = fitz.Font(fontfile= FONT_DIR / "helv_bold.ttf")
            full_name_width = full_name_width_font.text_length(full_name.upper(), fontsize=9 )
            x_right = 560
            correct_xy = ((x_right - full_name_width), 32)
            self.cords2[15]["pos"] = correct_xy
        else:
            raise FileNotFoundError(f"No template found for {self.state}")

    def insert_info(self):
        for k in self.cords1:
            field_str = self.data1[k["field"]]
            page = self.doc1[k["page"]]
            page.insert_text(k["pos"], field_str, fontsize=k["fontsize"],
                                fontname=k["fontname"], color=k["color"])
        for k in self.cords2:
            field_str = self.data2[k["field"]]
            page = self.doc2[k["page"]]
            page.insert_text(k["pos"], field_str, fontsize=k["fontsize"],
                                fontname=k["fontname"], color=k["color"])
    def save_garaging(self, path_dir, path_dir2):
        self.doc1.save(path_dir)
        self.doc2.save(path_dir2)
        self.doc1.close()
        self.doc2.close()

    def insert_info_to_dir(self, path_dir, path_dir2):
        self.insert_info()
        self.save_garaging(path_dir, path_dir2)

                





