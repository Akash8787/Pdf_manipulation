import json
import re

def extract_invoice_fields(text_lines, source_file):
    extracted = []
    current_item = {}
    total_mpf = ""
    total_hmf = ""
    total_duty = ""

    for i, line in enumerate(text_lines):
        line = line.strip()

        # Skip irrelevant lines (e.g., standalone numbers like "110")
        if re.match(r'^\d{3}\s*$', line):
            continue

        # Extract Line number (e.g., "001" to "999"), excluding "499" or "501"
        if re.match(r'^\d{3}\b', line) and not line.startswith(("499", "501")):
            if current_item:
                extracted.append(current_item)

            current_item = {
                "Line": line.strip().split()[0],
                "Extracted Value": "",
                "Duty1": "",
                "Duty2": "",
                "MPF": "",
                "HMF": "",
                "Invoice Number": "",
                "Invoice Value": "",
                "Entered Value": "",
                "Source File": source_file
            }

        # # Extract Extracted Value and Duty2 from tariff line
        # if re.match(r'^\d{3}\s+\d{4}\.\d{2}\.\d{2}\.\d{4}\s+[\d,]+\s+KG\b', line):
        #     dollar_values = re.findall(r"\$\d[\d,]*\.\d{2}", line)
        #     if dollar_values:
        #         if len(dollar_values) >= 1:
        #             current_item["Extracted Value"] = dollar_values[0]  # First dollar value ($1,659)
        #         if len(dollar_values) >= 2:
        #             current_item["Duty2"] = dollar_values[1]  # Second dollar value ($41.48)


                # Extract Extracted Value and Duty2 from line containing dollar values
        # Extract Extracted Value and Duty2 from line containing dollar values
        if '$' in line and "KG" in line:
            # Use re.finditer to capture exact positions
            dollar_matches = list(re.finditer(r"\$\d[\d,]*\.\d{2}", line))
           


            print(dollar_matches)
            if len(dollar_matches) >= 2:
                current_item["Extracted Value"] = dollar_matches[0].group()  # First dollar value
                print()
                current_item["Duty2"] = dollar_matches[1].group()            # Second dollar value
            elif len(dollar_matches) == 1:
                current_item["Extracted Value"] = dollar_matches[0].group()




        # Extract MPF
        if line.startswith("499 -") and "%" in line:
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                current_item["MPF"] = match.group()

        # Extract HMF
        if line.startswith("501 -") and "%" in line:
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                current_item["HMF"] = match.group()

        # Totals for Invoice line
        if "Totals for Invoice" in line:
            next_line = text_lines[i + 1].strip() if i + 1 < len(text_lines) else ""
            invoice_info = re.findall(r"\d{10}", next_line)
            values = re.findall(r"\d[\d,]*\.\d{2}\sUSD", next_line)
            if invoice_info:
                current_item["Invoice Number"] = invoice_info[0]
            if len(values) >= 2:
                current_item["Invoice Value"] = values[0]
                current_item["Entered Value"] = values[1]

    # Append the last item
    if current_item:
        extracted.append(current_item)

    return extracted

# Example input text
raw_text = """
001 8708.99.8180 225 KG 480.00 NO $1,659 2.50 % $41.48
C $131
N
499 - Merchandise Processing Fee 0.3464 % $5.75
501 - Harbor Maintenance Fee 0.1250 % $2.07
Totals for Invoice Invoice Value +/- MMV Exchange Entered Value
2423219308 1,659.00 USD 1.00000 1,659.00 USD
"""

# Split into lines and extract
text_lines = raw_text.strip().splitlines()
pdf_file = "EKH-1007198-6-7501.pdf"

extracted_data = extract_invoice_fields(text_lines, pdf_file)

# Convert to JSON string
json_output = json.dumps(extracted_data, indent=4)
print(json_output)