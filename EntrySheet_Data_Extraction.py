import pdfplumber
import json
import os
import re
import logging

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# PDF input path
pdf_file = r"D:\Python\Amount_Validation\59therror\EKH-1007198-6-7501 (1)[0].PDF"
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

def extract_invoice_items(text_lines, source_file):
    """Extract multiple invoice entries from HTS lines."""
    extracted = []
    current_item = {}
    total_mpf = ""
    total_hmf = ""
    total_duty = ""
    for i, line in enumerate(text_lines):
        line = line.strip()

        if re.match(r'^\d{3}\s+\d{4}\.\d{2,4}\.\d{2,4}', line):
            if current_item:
                extracted.append(current_item)

            current_item = {
                "Line": line.split()[0],
                "Extracted Value": "",
                "Duty2": "",
                "MPF": "",
                "HMF": "",
                "Invoice Number": "",
                "Invoice Value": "",
                "Entered Value": "",
                "Source File": source_file
            }

            dollar_values = re.findall(r"\$\d[\d,]*", line)
            if len(dollar_values) >= 1:
                current_item["Extracted Value"] = dollar_values[0]

        if "%" in line and "$" in line and "499" not in line and "501" not in line:
            matches = re.findall(r"\$\d[\d,]*\.\d{2}", line)
            if matches:
                current_item["Duty2"] = matches[-1]

        if line.startswith("499 - Merchandise"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                current_item["MPF"] = match.group()

        if line.startswith("501 - Harbor"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                current_item["HMF"] = match.group()
        # Invoice total-level values (do NOT attach to current_item)
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

        if "Ascertained Duty" in line or re.search(r"\bDuty\b", line):
            # Check if the next line exists and extract it
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                
                # Try to find the dollar value in the next line
                match = re.search(r"\$\d[\d,]*\.\d{2}", next_line)
                
                if match:
                    total_duty= match.group()  # Store the extracted duty value
                    print("Total Duty:",total_duty )
                    total_duty= next_line  # Optionally store the next line for context

        if "Totals for Invoice" in line:
            next_line = text_lines[i + 1].strip() if i + 1 < len(text_lines) else ""
            invoice_info = re.findall(r"\d{10}", next_line)
            values = re.findall(r"\d[\d,]*\.\d{2}\sUSD", next_line)
            if invoice_info:
                current_item["Invoice Number"] = invoice_info[0]
            if len(values) >= 2:
                current_item["Invoice Value"] = values[0]
                current_item["Entered Value"] = values[1]

    if current_item:
        extracted.append(current_item)

    return extracted

# --- Main execution ---
try:
    print(f"Processing: {pdf_file}")
    lines = extract_text_lines(pdf_file)
    results = extract_invoice_items(lines, os.path.basename(pdf_file))  # For multiple line items

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






