import pdfplumber
import json
import os
import re
import logging

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# PDF input path
pdf_file = r"D:\Python\Amount_Validation\52therror\EKH-0872208-7-7501.PDF"
pdf_dir = os.path.dirname(pdf_file)
output_file = os.path.join(pdf_dir, "output_json.txt")

# Check file existence
if not os.path.exists(pdf_file) or not os.path.isfile(pdf_file):
    print(f"PDF file not found or invalid: {pdf_file}")
    exit(1)


def clean(var, add_currency=False, add_usd=False):
    """Remove currency symbols, commas, percentages, and convert to float."""
    if not isinstance(var, str):
        return var
    var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '').strip()
    if var.lower() in ('no', 'n', 'free'):
        return 0.0
    try:
        cleaned_value = float(var)
        if add_currency:
            return f"${cleaned_value:.2f}"
        if add_usd:
            return f"{cleaned_value:.2f} USD"
        return cleaned_value
    except ValueError:
        return var

def extract_text_lines(pdf_file):
    """Extract text line by line from all pages, returning a list of lines per page."""
    all_lines = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    page_lines = text.strip().split('\n')
                    print(f"\n--- Page {i} ---\n")
                    # for line in page_lines:
                    #     print(line)
                    all_lines.extend(page_lines)
                else:
                    print(f"\n--- Page {i} ---\n[Empty Page]")
        if not all_lines:
            raise ValueError("Extracted text is empty. The PDF might be scanned or corrupted.")
        return all_lines
    except Exception as e:
        logging.error(f"Error reading PDF: {str(e)}")
        raise

def extract_invoice_fields(text_lines, source_file):
    extracted = []
    current_item = {}
    total_mpf = ""
    total_hmf = ""
    total_duty = ""

    for i, line in enumerate(text_lines):
        line = line.strip()

        # Extract Line number (e.g., "001") from any line starting with 3 digits (but NOT 499 or 501)
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

        # Extract Duty1 from line with tariff code, weight, and FREE (e.g., "9903.01.28 2,094 KG FREE $0.00")
        if re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,]+\s+KG\b', line):

            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                current_item["Duty1"] = match.group()
                # print(current_item["Duty1"])

        if re.search(r'\d{4}\.\d{2}\.\d{4}', line) and '%' in line:
            dollar_values = re.findall(r"\$\d[\d,]*(?:\.\d{2})?", line)
            # print(dollar_values)
            if dollar_values and len(dollar_values) >= 2:
                current_item["Extracted Value"] = dollar_values[0]
                current_item["Duty2"] = dollar_values[1]
            elif dollar_values:
                current_item["Duty2"] = dollar_values[0]



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


        if line.startswith("499 - MPF"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                total_mpf = match.group()
                print("Total MPF:", total_mpf)

        if line.startswith("501 - HMF"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                total_hmf = match.group()
                print("Total HMF:", total_hmf)

        # Total Duty: look for keyword and get dollar value in the **next** line
        # Look for total duty amount that comes AFTER the line containing "Ascertained Duty"
        if "Ascertained Duty" in line:
            # Look ahead up to 3 lines after current line to find a standalone dollar value
            for j in range(1, 4):
                if i + j < len(text_lines):
                    next_line = text_lines[i + j].strip()
                    match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                    if match:
                        total_duty = match.group()
                        print("Total Duty:", total_duty)
                        break



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


try:
    print(f"Processing: {pdf_file}")
    lines = extract_text_lines(pdf_file)
    results = extract_invoice_fields(lines, os.path.basename(pdf_file))  # For multiple line items

    # Save result
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"\nData saved to: {output_file}")

    # Print summary
    print("\nExtracted Values:")
    print(json.dumps(results, indent=4))

except Exception as e:
    print(f"Error processing {pdf_file}: {str(e)}")
    logging.error(f"Error processing {pdf_file}: {str(e)}")
    exit(1)
