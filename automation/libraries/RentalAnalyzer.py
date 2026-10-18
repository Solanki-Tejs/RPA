import os
import re
import csv
from datetime import datetime

class RentalAnalyzer:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def calculate_suitability_score(self, employment_status, monthly_income, rent_amount):
        """
        Calculates a basic suitability score (1-10) for a rental applicant.
        Args:
            employment_status: str (e.g. 'Employed', 'Student', 'Unemployed')
            monthly_income: str or float (e.g. '50000')
            rent_amount: str or float (e.g. '15000' or '₹15,000')
        Returns:
            str: "Score: X/10 (Amount is Y% of income)"
        """
        try:
            # Clean currency symbols, commas, and whitespace
            rent_str = str(rent_amount).replace('₹', '').replace(',', '').strip()
            income_str = str(monthly_income).replace('₹', '').replace(',', '').strip()
            
            income = float(income_str)
            rent = float(rent_str)
        except (ValueError, TypeError):
            return "Score: 1/10 (Manual Review: Invalid Income or Rent)"

        if income <= 0:
            return "Score: 1/10 (No income reported)"

        ratio = rent / income
        score = 10

        # Rent to income ratio deductions
        if ratio > 0.3:
            score -= 2
        if ratio > 0.4:
            score -= 3
        if ratio > 0.5:
            score -= 3 # cumulative deductions

        # Employment status deductions
        emp = str(employment_status).strip()
        if emp == 'Student':
            score -= 2
        elif emp == 'Unemployed':
            score -= 4
        elif emp == 'Self-Employed':
            score -= 1

        score = max(1, min(10, score))
        return f"Score: {score}/10 (Amount is {int(ratio * 100)}% of income)"

    def initialize_export_csv(self, filename="approved_applications_report.csv"):
        """
        Initializes or resets the CSV file with proper headers.
        """
        headers = [
            "Timestamp",
            "Applicant Name",
            "Email",
            "Phone",
            "Property Title",
            "Amount",
            "Employment Status",
            "Monthly Income",
            "Status",
            "Score"
        ]
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def append_scraped_application(self, applicant_name, applicant_cell, property_title, rent_amount, emp_status, monthly_income, status_cell, task_param="Approved Only", filename="approved_applications_report.csv"):
        """
        Appends a scraped application row to the CSV file based on filter parameters.
        """
        # Parse status from status cell (e.g. "Approved\nScore: 8/10...")
        status_text = str(status_cell).strip()
        status_match = re.search(r'(Approved|Rejected|Pending)', status_text, re.IGNORECASE)
        status = status_match.group(1).capitalize() if status_match else status_text.split('\n')[0].strip()

        # Check filter
        filter_str = str(task_param).strip().lower()
        if "approved" in filter_str and status != "Approved":
            return

        # Parse score
        score_match = re.search(r'(Score:\s*\d+/\d+.*)', status_text, re.IGNORECASE)
        score = score_match.group(1).strip() if score_match else "N/A"

        # Parse email and phone from applicant cell
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(applicant_cell))
        email = email_match.group(0) if email_match else ""

        phone_match = re.search(r'(\+?\d[\d\s-]{8,15})', str(applicant_cell))
        phone = phone_match.group(0).strip() if phone_match else ""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        clean_rent = str(rent_amount).replace('₹', '').replace(',', '').strip()
        clean_income = str(monthly_income).strip()

        row = [
            timestamp,
            str(applicant_name).strip(),
            email,
            phone,
            str(property_title).strip(),
            clean_rent,
            str(emp_status).strip(),
            clean_income,
            status,
            score
        ]

        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def initialize_buyer_export_csv(self, filename="buyer_approved_properties.csv"):
        """
        Initializes or resets the Buyer CSV export file with headers.
        """
        headers = [
            "Applied On",
            "Property Title",
            "Location",
            "Amount",
            "Owner Name",
            "Owner Phone",
            "Owner Email",
            "Status",
            "Score"
        ]
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def append_buyer_application(self, property_cell, landlord_cell, applied_on, status, score, filename="buyer_approved_properties.csv"):
        """
        Appends an approved property record for the buyer.
        """
        if str(status).strip() != "Approved":
            return

        p_text = str(property_cell)
        lines = [l.strip() for l in p_text.split('\n') if l.strip()]
        title = lines[0] if len(lines) > 0 else ""
        location = ""
        rent = ""
        loc_match = re.search(r'📍\s*(.*)', p_text)
        if loc_match:
            location = loc_match.group(1).strip()
        rent_match = re.search(r'₹\s*([\d,]+)', p_text)
        if rent_match:
            rent = rent_match.group(1).replace(',', '').strip()

        l_text = str(landlord_cell)
        l_lines = [l.strip() for l in l_text.split('\n') if l.strip()]
        owner_name = l_lines[0] if len(l_lines) > 0 else "Seller"
        phone_match = re.search(r'📞\s*([\d\+\s-]+)', l_text)
        owner_phone = phone_match.group(1).strip() if phone_match else ""
        email_match = re.search(r'✉️\s*([\w\.-]+@[\w\.-]+\.\w+)', l_text)
        owner_email = email_match.group(1).strip() if email_match else ""

        row = [
            str(applied_on).strip(),
            title,
            location,
            rent,
            owner_name,
            owner_phone,
            owner_email,
            str(status).strip(),
            str(score).strip()
        ]

        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

