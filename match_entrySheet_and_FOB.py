import pdfplumber
import json
import os
import re
import logging
import math

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# PDF input path
pdf_file = r"D:\latest_Error\57therror\EKH-1005896-7-7501[0] (1).pdf"
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
                    for line in page_lines:
                        print(line)
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
    global total_mpf, total_hmf, total_duty
    extracted = []
    current_item = {}
    # total_mpf = ""
    # total_hmf = ""
    # total_duty = ""

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

        # if re.search(r'\d{4}\.\d{2}\.\d{4}', line) and '%' in line:
        #     dollar_values = re.findall(r"\$\d[\d,]*(?:\.\d{2})?", line)
        #     print("Dollar_Values:",dollar_values)
        #     if dollar_values and len(dollar_values) >= 2:
        #         current_item["Extracted Value"] = dollar_values[0]
        #         current_item["Duty2"] = dollar_values[1]
        #     elif dollar_values:
        #         current_item["Duty2"] = dollar_values[0]



        # Normalize line
        clean_line = re.sub(r"[^\x00-\x7F]+", " ", line)  # Remove non-ASCII characters

        # Unified condition
        if (
            (re.search(r'\d{4}\.\d{2}\.\d{4}', line) and '%' in line)
            or ("KG" in line and "$" in line)
        ):
            # dollar_matches = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b", clean_line)
            dollar_matches = re.findall(r"\$\d[\d,]*(?:\.\d{2})?\b", clean_line)

            
            # print("Dollar_Values:", dollar_matches)

            if len(dollar_matches) >= 2:
                current_item["Extracted Value"] = dollar_matches[0]
                current_item["Duty2"] = dollar_matches[1]
            elif len(dollar_matches) == 1:
                # Fallback logic depends on which case it is
                if "KG" in line:
                    current_item["Extracted Value"] = dollar_matches[0]
                else:
                    current_item["Duty2"] = dollar_matches[0]



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


    # Calculate totals
    total_added_duty = 0.0
    total_added_mpf = 0.0
    total_added_hmf = 0.0

    for item in results:
         # Clean and add Duty1
        duty1_val = clean(item.get("Duty1", "0"))
        if isinstance(duty1_val, float):
            total_added_duty += duty1_val
        # Clean and add Duty2
        duty_val = clean(item.get("Duty2", "0"))
        if isinstance(duty_val, float):
            total_added_duty += duty_val

        # Clean and add MPF
        mpf_val = clean(item.get("MPF", "0"))
        if isinstance(mpf_val, float):
            total_added_mpf += mpf_val

        # Clean and add HMF
        hmf_val = clean(item.get("HMF", "0"))
        if isinstance(hmf_val, float):
            total_added_hmf += hmf_val

    print("\n--- Totals ---")
    print(f"Total Duty: ${total_added_duty:.2f}")
    print(f"Total MPF: ${total_added_mpf:.2f}")
    print(f"Total_Added_HMF: ${total_added_hmf:.2f}")

    # Convert totals to float if needed
    total_duty_val = float(clean(total_duty))
    total_mpf_val = float(clean(total_mpf))
    total_hmf_val = float(clean(total_hmf))
    # print("total_hmf_val",total_hmf_val)

    tolerance = 1e-6

    # Compare and report with tolerance
    if math.isclose(total_added_duty, total_duty_val, abs_tol=tolerance):
        print("✅ Total Duty matches.")
    else:
        print(f"❌ Total Duty mismatch! Expected: {total_duty_val}, Found: {total_added_duty:.2f}")

    if math.isclose(total_added_mpf, total_mpf_val, abs_tol=tolerance):
        print("✅ Total MPF matches.")
    else:
        print(f"❌ Total MPF mismatch! Expected: {total_mpf_val}, Found: {total_added_mpf:.2f}")

    if math.isclose(total_added_hmf, total_hmf_val, abs_tol=tolerance):
        print("✅ Total HMF matches.")
    else:
        print(f"❌ Total HMF mismatch! Expected: {total_hmf_val}, Found: {total_added_hmf:.2f}")



except Exception as e:
    print(f"Error processing {pdf_file}: {str(e)}")
    logging.error(f"Error processing {pdf_file}: {str(e)}")
    exit(1)
#=============================================================================================================




from pdfminer.high_level import extract_text
import json
import os
import re

# Path to the folder containing PDF files
pdf_folder = r"D:\Python\Amount_Validation\59therror\New folder"

# Path to the output .txt file
# output_file = os.path.join(pdf_folder, "output_json.txt")

# Ensure the folder exists
if not os.path.exists(pdf_folder):
    # print(f"Folder not found: {pdf_folder}")
    exit(1)

# List to store JSON data for all PDFs
all_json_data = []

def clean_exporter_details(text):
    """Remove unwanted prefixes (like 'rter:') and their trailing newlines."""
    # Remove any word characters + ":" at the start, along with the following newline
    cleaned = re.sub(r'^\w+:\n', '', text.strip())
    # Also handle cases where there's extra whitespace or variations
    cleaned = re.sub(r'^\s*\w+[: ]*\n', '', cleaned)
    # Remove trailing invoice info if present
    cleaned = re.sub(r'\n\nInvoice No:.*', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

# Iterate through all files in the folder
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        # Full path to the PDF file
        pdf_path = os.path.join(pdf_folder, filename)

        # Extract all text
        try:
            text = extract_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text from {filename}: {e}")
            continue

        # 1. Extract Manufacture & Exporter Details
        start_marker_exporter = "Manufacture & Exporter :\n"
        end_marker_exporter = "\nIEC Code:"
        start_index_exporter = text.find(start_marker_exporter) + len(start_marker_exporter)
        end_index_exporter = text.find(end_marker_exporter)

        if start_index_exporter == -1 or end_index_exporter == -1:
            exporter_details = "Manufacture & Exporter details not found."
        else:
            exporter_details = clean_exporter_details(text[start_index_exporter:end_index_exporter])

        # 2. Extract Invoice No.
        start_marker_invoice = "Invoice No: "
        end_marker_invoice = "\n"
        start_index_invoice = text.find(start_marker_invoice) + len(start_marker_invoice)
        end_index_invoice = text.find(end_marker_invoice, start_index_invoice)

        if start_index_invoice == -1 or end_index_invoice == -1:
            invoice_no = "Invoice No. not found."
        else:
            invoice_no = text[start_index_invoice:end_index_invoice].strip()

        # 3. Extract FOB Value IN USD
        start_marker_fob = "FOB Value IN USD - "
        end_marker_fob = "\n"
        start_index_fob = text.find(start_marker_fob) + len(start_marker_fob)
        end_index_fob = text.find(end_marker_fob, start_index_fob)

        if start_index_fob == -1 or end_index_fob == -1:
            fob_value = "FOB Value not found."
        else:
            fob_value = text[start_index_fob:end_index_fob].strip()

        # Structure the data for JSON, including the PDF filename
                # Structure the data for JSON, including the PDF filename
        data = {
            "pdf_file": filename,
            "Manufacture & Exporter": exporter_details,
            "Invoice No.": invoice_no,
            "FOB Value IN USD": fob_value
        }

        # Check if we should skip this record
        if "not found" in exporter_details:
            # print(f"Skipped {filename} due to missing exporter details.")
            continue

        try:
            # Attempt to convert FOB value to float
            fob_numeric = float(fob_value.replace(',', '').strip())
            data["FOB Value IN USD"] = fob_numeric  # Store the parsed float
        except ValueError:
            print(f"Skipped {filename} due to invalid FOB value: {fob_value}")
            continue

        # Append to the list of all JSON data
        all_json_data.append(data)
        print(f"Processed {filename}")

# Step 1: Track matched invoice numbers from `results`
matched_invoices = set()
# Print all JSON data
# print(json.dumps(all_json_data, indent=4, ensure_ascii=False))
invoice_fob_list = [(item["Invoice No."], item["FOB Value IN USD"]) for item in all_json_data]
# Print the extracted invoice numbers and FOB values
def clean_value(val):
    """Removes commas and currency text, returns float."""
    try:
        return float(val.replace(',', '').replace('USD', '').strip())
    except:
        return 0.0

for invoice, fob in invoice_fob_list:
    found = False  # Flag to track if invoice matched

    for item in results:
        # print(item["Duty2"])
        if str(item["Invoice Number"]).strip() == str(invoice).strip():
            found = True
            print(f"Matched Invoice: {item['Invoice Number']}")
            entered_value = clean_value(item.get("Entered Value", "0"))
            invoice_value = clean_value(item.get("Invoice Value", "0"))

            if (math.isclose(fob, entered_value, rel_tol=1e-3) and
                math.isclose(fob, invoice_value, rel_tol=1e-3)):
                print(f"✅ OK for Invoice No. {invoice}")
            else:
                print(f"❌ Value mismatch for Invoice No. {invoice}")
            break  # Stop checking once matched

    if not found:
        print(f"⚠️ Invoice No. {invoice} not found in EntrySheet.")

# Step 2: Check if any invoice in `results` was never matched
invoice_folder_invoices = {inv for inv, _ in invoice_fob_list}

for item in results:
    invoice_no = str(item.get("Invoice Number", "")).strip()
    if invoice_no and invoice_no not in invoice_folder_invoices:
        print(f"📂 Invoice {invoice_no} from EntrySheet has no matching file in invoice folder.")




