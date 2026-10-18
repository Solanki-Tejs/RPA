from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=16)
pdf.cell(200, 10, text="Plotify Bulk Property Submission - Rules & Format", new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(10)

pdf.set_font("Helvetica", size=12)

content = [
    "To use the Seller Bulk List feature, your CSV file MUST follow these strict rules:",
    "",
    "1. Exact Column Headers Required:",
    "Your CSV file must have exactly these column headers in the first row:",
    "Title, Price, Category, Location, Description, Bedrooms, Bathrooms, Area, Type, Floor,",
    "TotalFloors, Furnishing, Facing, Amenities, MapLink, ImagePath, OwnershipProof",
    "",
    "2. Allowed Values for Specific Columns:",
    "To avoid robot errors, you must use exact matches for dropdown fields:",
    "",
    "- Category: Sell, Rent, Commercial",
    "- Type: House, Apartment, Villa, Commercial, Farm House, Beach House",
    "- Furnishing: Unfurnished, Semi Furnished, Fully Furnished (Do NOT use hyphens)",
    "- Facing: North, South, East, West",
    "",
    "3. Amenities Formatting:",
    "- Amenities must be a single string separated by commas (e.g. \"Lift, Parking, Security\").",
    "- If using Excel, ensure the cell is quoted if it contains commas.",
    "- Only these exact amenities are supported: Lift, Parking, Power Backup, Security,",
    "  Water Supply, Play Area.",
    "",
    "4. File Upload Columns:",
    "- ImagePath and OwnershipProof must be EXACT absolute file paths on your computer.",
    "- Example: C:\\Users\\Name\\Documents\\house.png",
    "",
    "5. General Rules:",
    "- Do not include extra spaces at the beginning or end of values.",
    "- Numeric fields (Price, Bedrooms, Bathrooms, Area, Floor, TotalFloors) must be numbers.",
]

for line in content:
    if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or "- Category:" in line or "- Type:" in line or "- Furnishing:" in line or "- Facing:" in line:
        pdf.set_font("Helvetica", style="B", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 8, text=line, new_x="LMARGIN", new_y="NEXT")

output_path = r"d:\Projects\RPA\automation\frontend\public\bulk_property_rules.pdf"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
pdf.output(output_path)
