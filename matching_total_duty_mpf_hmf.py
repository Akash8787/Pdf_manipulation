import pdfplumber
import json
import os
import re
import logging
import math

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# PDF input path
pdf_file = r"D:\Python\Amount_Validation\69therror\EKH-1012194-8.pdf"
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
    global total_mpf, total_hmf, total_duty, total_entered_value, other_fees, total_other_fee2, total_duty_other_fee
    extracted = []
    current_item = {}
    # total_mpf = ""
    # total_hmf = ""
    # total_duty = ""

    for i, line in enumerate(text_lines):
        line = line.strip()

        # Extract Line number (e.g., "001") from any line starting with 3 digits (but NOT 499 or 501)
        # if re.match(r'^\d{3}\b', line) and not line.startswith(("499", "501")):
        if re.match(r'^\d{3}(?![0-9])', line) and not line.startswith(("499", "501")):

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

        if re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,]+\s+KG\b', line):
            # Try to find $amount on the same line
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)

            # If not found, check the next line (could be "FREE $0.00")
            if not match and i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                match = re.search(r"\$\d[\d,]*\.\d{2}", next_line)

            if match:
                current_item["Duty1"] = match.group()
                # print("Duty1:", current_item["Duty1"])
            else:
                print("No Duty1 match found.")



        # # Extract Duty1 from line with tariff code, weight, and FREE (e.g., "9903.01.28 2,094 KG FREE $0.00")
        # if re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,]+\s+KG\b', line):

        #     match = re.search(r"\$\d[\d,]*\.\d{2}", line)
        #     print("Match:",match)
        #     if match:
        #         current_item["Duty1"] = match.group()
        #         print(current_item["Duty1"])
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

        # # Extract MPF
        # if line.startswith("499 -") and "%" in line:
        #     # match = re.search(r"\$\d[\d,]*\.\d{2}", line)
        #     match = re.search(r"\$\d[\d,]*[.,]\d{2}", line)
        #     # print("Match:",match)
        #     if match:
        #         value_str = match.group().replace(",", ".").replace("$", "")
        #         current_item["MPF"] = value_str

        # Extract MPF
        if line.startswith("499 -") and "Merchandise Processing Fee" in line:
            # Check current and next line for $amount
            combined_line = line
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                combined_line += " " + next_line  # Combine current + next line

            # Search for MPF value
            match = re.search(r"\$\d[\d,]*[.,]\d{2}", combined_line)
            if match:
                value_str = match.group().replace(",", "").replace("$", "")
                current_item["MPF"] = value_str



        # # Extract HMF
        # if line.startswith("501 -") and "%" in line:
        #     match = re.search(r"\$\d[\d,]*\.\d{2}", line)
        #     if match:
        #         current_item["HMF"] = match.group()
        # Extract HMF
        if line.startswith("501 -") and "Harbor Maintenance Fee" in line:
            # Combine current and next line in case value is split
            combined_line = line
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                combined_line += " " + next_line  # Merge lines

            match = re.search(r"\$\d[\d,]*[.,]\d{2}", combined_line)
            if match:
                value_str = match.group().replace(",", "").replace("$", "")
                current_item["HMF"] = value_str
                
        if line.startswith("499 - MPF"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                total_mpf = match.group()
                print("Total MPF:", total_mpf)

        if line.startswith("501 - HMF"):
            # matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
            matches = re.findall(r"\$\s?\d[\d,]*\.?\d{0,2}", line)

            # print("Match:",matches)
            if matches:
                if len(matches) > 1:
                    total_hmf = matches[0]
                    total_entered_value = matches[1]
                else:
                    total_hmf = matches[0]
                    total_entered_value = None  # or handle as needed

                print("Total HMF:", total_hmf)
                print("Total Entered Value:", total_entered_value)


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
        # Separate loop to extract Total Other Fees AFTER Total Duty has been found
            for i, line in enumerate(text_lines):
                if "Total Other Fees" in line:
                    for j in range(1, 4):  # Look ahead 3 lines
                        if i + j < len(text_lines):
                            next_line = text_lines[i + j].strip()
                            # fee_match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                            fee_match = re.match(r"^\$\s?\d[\d,]*\.\d{2}$", next_line)

                            print("fee_match:",fee_match)
                            if fee_match:
                                other_fees = fee_match.group()
                                print("Total Other Fees:", other_fees)
                                break
                    break  # stop after finding the first "Total Other Fees"
            for i, line in enumerate(text_lines):
                line = line.strip()
                if "Authorized Agent" in line:
                    for j in range(1, 4):
                        if i + j < len(text_lines):
                            next_line = text_lines[i + j].strip()
                            match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                            if match:
                                total_other_fee2 = match.group()
                                print("Total Other Fee 2:", total_other_fee2)
                                break
                # 2. Check for "Ascertained Total" or "Total" line, then get next dollar value
            for i, line in enumerate(text_lines):
                line = line.strip()
                if "purchaser" in line and "consignee" in line:
                    match = re.search(r"\$\d[\d,]*\.\d{2}", line)
                    if match:
                        total_duty_other_fee = match.group()
                        print("Total Duty Other Fee:", total_duty_other_fee)
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
    total_added_entered_value = 0.0

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
        print("MPF:",mpf_val)

        if isinstance(mpf_val, float):
            total_added_mpf += mpf_val

        # Clean and add HMF
        hmf_val = clean(item.get("HMF", "0"))
        if isinstance(hmf_val, float):
            total_added_hmf += hmf_val
        
        # Clean and add Entered Value
        entered_value = clean(item.get("Entered Value","0"))
        if isinstance(entered_value, float):
            total_added_entered_value += entered_value


    print("\n--- Totals ---")
    print(f"Total Duty: ${total_added_duty:.2f}")
    print(f"Total MPF: ${total_added_mpf:.2f}")
    print(f"Total_Added_HMF: ${total_added_hmf:.2f}")
    print(f"Total_Added_Entered_Value: ${total_added_entered_value:.2f}")

    # Convert totals to float if needed
    total_duty_val = float(clean(total_duty))
    total_mpf_val = float(clean(total_mpf))
    total_hmf_val = float(clean(total_hmf))
    total_entered_val = float(clean(total_entered_value))
    # print("total_hmf_val",total_hmf_val)

    # tolerance = 0.01

    tolerance = 0.011

    # Function to check match within bounds and other logic
    def check_within_bounds(label, actual, expected, tolerance):
        lower_bound = expected - tolerance
        upper_bound = expected + tolerance
        lower_plus1 = expected - 1
        upper_plus1 = expected + 1

        # print(f"\n🔍 Checking {label}:")
        # print(f"   ➤ Expected: {expected}")
        # print(f"   ➤ Actual: {actual}")
        # print(f"   ➤ Allowed Range (±{tolerance}): {lower_bound:.2f} to {upper_bound:.2f}")

        if lower_bound <= actual <= upper_bound:
            print(f"✅ Total {label} matches.")
        elif int(actual) == int(expected):
            print(f"✅ Total {label} matches.")
        elif lower_plus1 <= actual <= upper_plus1:
            print(f"ℹ️ Total {label} not within tolerance or int match, but within ±1 range: {lower_plus1:.2f} to {upper_plus1:.2f}")
        else:
            print(f"❌ Total {label} mismatch! Expected: {expected}, Found: {actual:.2f}")

    # Compare and report
    check_within_bounds("Duty", total_added_duty, total_duty_val, tolerance)
    check_within_bounds("MPF", total_added_mpf, total_mpf_val, tolerance)
    check_within_bounds("HMF", total_added_hmf, total_hmf_val, tolerance)
    check_within_bounds("Entered Value", total_added_entered_value, total_entered_val, tolerance)

    # # Compare and report with tolerance
    # if math.isclose(total_added_duty, total_duty_val, abs_tol=tolerance):
    #     print("✅ Total Duty matches.")
    # else:
    #     print(f"❌ Total Duty mismatch! Expected: {total_duty_val}, Found: {total_added_duty:.2f}")

    # if math.isclose(total_added_mpf, total_mpf_val, abs_tol=tolerance):
    #     print("✅ Total MPF matches.")
    # else:
    #     print(f"❌ Total MPF mismatch! Expected: {total_mpf_val}, Found: {total_added_mpf:.2f}")

    # if math.isclose(total_added_hmf, total_hmf_val, abs_tol=tolerance):
    #     print("✅ Total HMF matches.")
    # else:
    #     print(f"❌ Total HMF mismatch! Expected: {total_hmf_val}, Found: {total_added_hmf:.2f}")
    # if math.isclose(total_added_entered_value, total_entered_val, abs_tol=tolerance):
    #     print("✅ Total Entered Value matches.")
    # else:
    #     print(f"❌ Total Entered Value mismatch! Expected: {total_entered_val}, Found: {total_added_entered_value:.2f}")


except Exception as e:
    print(f"Error processing {pdf_file}: {str(e)}")
    logging.error(f"Error processing {pdf_file}: {str(e)}")
    exit(1)
