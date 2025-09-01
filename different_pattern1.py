import pdfplumber
import json
import os
import re
import logging

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# # PDF input path
# pdf_file = r"D:\Python\Amount_Validation\59therror\EKH-1007198-6-7501 (1)[0].PDF"
# pdf_dir = os.path.dirname(pdf_file)
# output_file = os.path.join(pdf_dir, "output_json.txt")

# # Check file existence
# if not os.path.exists(pdf_file) or not os.path.isfile(pdf_file):
#     print(f"PDF file not found or invalid: {pdf_file}")
#     exit(1)


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
        # if re.match(r'^\d{3}(?!\.\d)', line) and not line.startswith(("499", "501")):
        # if re.match(r'^00[1-9]\b', line.strip()):
        # if re.match(r'^\d{3}\b', line.strip()) and not line.startswith(("499", "501")):
        # if re.match(r'^\d{3}\b', line.strip()) and not re.match(r'^\d{3}\.\d', line.strip()):
        # if re.match(r'^(0[0-9]{2})\b(?!\.\d)', line.strip()):
        # if re.match(r'^(0(0[1-9]|[1-9][0-9]))\b', line.strip()):
        # if re.match(r'^(0{0,2}[1-9]|0?[1-9][0-9])\b', line.strip()):
        if re.match(r'^(00[1-9]|0[0-9]{3})\b', line.strip()):



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

        # if re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,]+\s+KG\b', line):
        #     # Try to find $amount on the same line
        #     match = re.search(r"\$\d[\d,]*\.\d{2}", line)

        #     # If not found, check the next line (could be "FREE $0.00")
        #     if not match and i + 1 < len(text_lines):
        #         next_line = text_lines[i + 1].strip()
        #         match = re.search(r"\$\d[\d,]*\.\d{2}", next_line)

        #     if match:
        #         current_item["Duty1"] = match.group()
        #         print("Duty1:", current_item["Duty1"])
        #     else:
        #         print("No Duty1 match found.")

        # # Normalize line
        # clean_line = re.sub(r"[^\x00-\x7F]+", " ", line)  # Remove non-ASCII characters

        # # Unified condition
        # if (
        #     (re.search(r'\d{4}\.\d{2}\.\d{4}', line) and '%' in line)
        #     or ("KG" in line and "$" in line)
        # ):
        #     # dollar_matches = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b", clean_line)
        #     dollar_matches = re.findall(r"\$\d[\d,]*(?:\.\d{2})?\b", clean_line)

            
        #     # print("Dollar_Values:", dollar_matches)

        #     if len(dollar_matches) >= 2:
        #         current_item["Extracted Value"] = dollar_matches[0]
        #         current_item["Duty2"] = dollar_matches[1]
            # elif len(dollar_matches) == 1:
            #     # Fallback logic depends on which case it is
            #     if "KG" in line:
            #         current_item["Extracted Value"] = dollar_matches[0]
            #     else:
            #         current_item["Duty2"] = dollar_matches[0]

        # if re.search(r'^\d{3}\s+\d{4}\.\d{2}\.\d{4}\s+[\d,]+\s+KG\b', line):
        #     # Find all dollar amounts on the line
        #     dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)

        #     if dollar_matches:
        #         current_item["Extracted Value"] = dollar_matches[0]  # $2,898
        #         print("Extracted Value:", current_item["Extracted Value"])

        #     # Extract Duty1 from line (typically last dollar on the line)
        #     if len(dollar_matches) > 1:
        #         current_item["Duty1"] = dollar_matches[-1]  # $289.80
        #         print("Duty1:", current_item["Duty1"])

        #     # Look ahead to find Duty2 in following lines
        #     for offset in range(1, 3):  # check next 2 lines
        #         if i + offset < len(text_lines):
        #             next_line = text_lines[i + offset].strip()
        #             duty2_match = re.search(r"\d+(\.\d+)?\s*%\s*\$(\d[\d,]*\.\d{2})", next_line)
        #             if duty2_match:
        #                 current_item["Duty2"] = f"${duty2_match.group(2)}"
        #                 print("Duty2:", current_item["Duty2"])
        #                 break
        #         # New block: Fallback match if no "001 xxx KG" line but tariff and dollar values exist
        # elif re.search(r'\d{4}\.\d{2}\.\d{4}.*?\$\d[\d,]*\.\d{2}', line):
        #     dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)

        #     if dollar_matches:
        #         current_item["Extracted Value"] = dollar_matches[0]  # $10,293
        #         print("Extracted Value (fallback):", current_item["Extracted Value"])

        #     if len(dollar_matches) > 1:
        #         current_item["Duty2"] = dollar_matches[-1]  # $257.33
        #         print("Duty2 (from tariff line):", current_item["Duty2"])

        #     # Look back 1-2 lines for Duty1
        #     for offset in range(1, 3):
        #         if i - offset >= 0:
        #             prev_line = text_lines[i - offset].strip()
        #             duty1_match = re.search(r"\$\d[\d,]*\.\d{2}", prev_line)
        #             if duty1_match:
        #                 current_item["Duty1"] = duty1_match.group()
        #                 print("Duty1 (from line above):", current_item["Duty1"])
        #                 break
        #     # Look ahead to find Duty2 in following lines

        # elif re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,\.]+\s+KG\b', line):
        #     # Example match: "9903.01.25 1,443.00 KG $9,175 2.50 % $229.38"
        #     dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)

        #     if dollar_matches:
        #         current_item["Extracted Value"] = dollar_matches[0]  # $9,175
        #         print("Extracted Value (tariff line):", current_item["Extracted Value"])

        #         if len(dollar_matches) > 1:
        #             current_item["Duty2"] = dollar_matches[-1]  # $229.38
        #             print("Duty2 (tariff line):", current_item["Duty2"])

        #     # Look back one line for Duty1 (if e.g., $917.50 is on previous line)
        #     if i > 0:
        #         prev_line = text_lines[i - 1].strip()
        #         prev_duty1_match = re.search(r"\$\d[\d,]*\.\d{2}", prev_line)
        #         if prev_duty1_match:
        #             current_item["Duty1"] = prev_duty1_match.group()
        #             print("Duty1 (from previous line):", current_item["Duty1"])


        if re.search(r'^\d{3}\s+\d{4}\.\d{2}\.\d{4}\s+[\d,]+\s+KG\b', line):
            # Find all dollar amounts on the line
            dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
            # print("Dollor_Matches1:",dollar_matches)

            if dollar_matches:
                current_item["Extracted Value"] = dollar_matches[0]  # $2,898
                # print("Extracted Value:", current_item["Extracted Value"])

            # Extract Duty1 from line (typically last dollar on the line)
            if len(dollar_matches) > 1:
                current_item["Duty1"] = dollar_matches[-1]  # $289.80
                # print("Duty1:", current_item["Duty1"])

            # Look ahead to find Duty2 (percent on one line, $ on same or next few lines)
            percent_line = None
            for offset in range(1, 4):
                if i + offset < len(text_lines):
                    next_line = text_lines[i + offset].strip()
                    if re.search(r"\d+(\.\d+)?\s*%", next_line):
                        percent_line = i + offset
                        break

            if percent_line:
                for offset in range(0, 3):
                    if percent_line + offset < len(text_lines):
                        dollar_line = text_lines[percent_line + offset].strip()
                        dollar_match = re.search(r"\$(\d[\d,]*\.\d{2})", dollar_line)
                        if dollar_match:
                            current_item["Duty2"] = f"${dollar_match.group(1)}"
                            print("Duty2 (split):", current_item["Duty2"])
                            break

        elif re.search(r'\d{4}\.\d{2}\.\d{4}.*?\$\d[\d,]*\.\d{2}', line):
            dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
            # print("Dollar_Matches2:",dollar_matches)

            if dollar_matches:
                current_item["Extracted Value"] = dollar_matches[0]
                # print("Extracted Value (fallback):", current_item["Extracted Value"])

            if len(dollar_matches) > 1:
                current_item["Duty2"] = dollar_matches[-1]
                # print("Duty2 (from tariff line):", current_item["Duty2"])

            # Look ahead to find Duty2 (if not already set)
            if "Duty2" not in current_item:
                percent_line = None
                for offset in range(1, 4):
                    if i + offset < len(text_lines):
                        next_line = text_lines[i + offset].strip()
                        if re.search(r"\d+(\.\d+)?\s*%", next_line):
                            percent_line = i + offset
                            break

                if percent_line:
                    for offset in range(0, 3):
                        if percent_line + offset < len(text_lines):
                            dollar_line = text_lines[percent_line + offset].strip()
                            dollar_match = re.search(r"\$(\d[\d,]*\.\d{2})", dollar_line)
                            if dollar_match:
                                current_item["Duty2"] = f"${dollar_match.group(1)}"
                                print("Duty2 (split fallback):", current_item["Duty2"])
                                break

        # elif re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,\.]+\s+KG\b', line):
        #     # Match e.g. "9903.01.25 1,443.00 KG $9,175 2.50 % $229.38"
        #     dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
        #     print("Dollor_Matches3:",dollar_matches)

        #     if dollar_matches:
        #         current_item["Extracted Value"] = dollar_matches[0]
        #         print("Extracted Value (tariff line):", current_item["Extracted Value"])

        #         if len(dollar_matches) > 1:
        #             current_item["Duty2"] = dollar_matches[-1]
        #             print("Duty2 (tariff line):", current_item["Duty2"])

        #     # Look back one line for Duty1 (e.g., $917.50)
        #     if i > 0:
        #         prev_line = text_lines[i - 1].strip()
        #         prev_duty1_match = re.search(r"\$\d[\d,]*\.\d{2}", prev_line)
        #         if prev_duty1_match:
        #             current_item["Duty1"] = prev_duty1_match.group()
        #             print("Duty1 (from previous line):", current_item["Duty1"])
        elif re.search(r'^\d{4}\.\d{2}\.\d{2}\s+[\d,\.]+\s+KG\b', line):
            dollar_matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
            # print("Dollor_Matches3:", dollar_matches)

            if dollar_matches:
                current_item["Extracted Value"] = dollar_matches[0]
                # print("Extracted Value (tariff line):", current_item["Extracted Value"])

            # Look for % on current line
            percent_match = re.search(r"\d+(\.\d+)?\s*%", line)
            if percent_match:
                # Try to get Duty2 on same line
                if len(dollar_matches) > 1:
                    current_item["Duty2"] = dollar_matches[-1]
                    # print("Duty2 (tariff line same line):", current_item["Duty2"])
                else:
                    # If not present on the same line, check next few lines
                    for offset in range(1, 3):  # check next 2 lines max
                        if i + offset < len(text_lines):
                            next_line = text_lines[i + offset].strip()
                            next_dollar = re.search(r"\$\d[\d,]*\.\d{2}", next_line)
                            if next_dollar:
                                current_item["Duty2"] = next_dollar.group()
                                # print("Duty2 (from next line):", current_item["Duty2"])
                                break

            # Look for Duty1 on previous line
            if i > 0:
                prev_line = text_lines[i - 1].strip()
                prev_duty1_match = re.search(r"\$\d[\d,]*\.\d{2}", prev_line)
                if prev_duty1_match:
                    current_item["Duty1"] = prev_duty1_match.group()
                    # print("Duty1 (from previous line):", current_item["Duty1"])







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
        # Extract MPF (Merchandise Processing Fee)
        elif "499 - Merchandise Processing Fee" in line:
            # Try next line for the value
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                match = re.search(r"\$\d[\d,]*[.,]\d{2}", next_line)
                if match:
                    current_item["MPF"] = match.group().replace(",", "").replace("$", "")
                    print("MPF:", current_item["MPF"])

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
        # Extract HMF (Harbor Maintenance Fee)
        elif "501 - Harbor Maintenance Fee" in line:
            # Try next line for the value
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                match = re.search(r"\$\d[\d,]*[.,]\d{2}", next_line)
                if match:
                    current_item["HMF"] = match.group().replace(",", "").replace("$", "")
                    print("HMF:", current_item["HMF"])

                
        if line.startswith("499 - MPF"):
            match = re.search(r"\$\d[\d,]*\.\d{2}", line)
            if match:
                total_mpf = match.group()
                print("Total MPF:", total_mpf)
        if line.startswith("499 - MPF"):
            # Try to match dollar values in this line
            matches = re.findall(r"\$\d[\d,]*\.\d{2}", line)
            # if matches:
            #     if len(matches) >= 2:
            #         total_duty = matches[1]  # Second dollar value
            #         print("Total Duty:", total_duty)

            # Check the next line for entered value if available
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                entered_value_match = re.search(r"\$\d[\d,]*\.\d{2}", next_line)
                if entered_value_match:
                    total_entered_value = entered_value_match.group()
                    print("Total Entered Value1:", total_entered_value)

        

        # if line.startswith("501 - HMF"):
        #     # matches = re.findall(r"\$\d[\d,]*\.\d{2}|\$\d[\d,]*", line)
        #     matches = re.findall(r"\$\s?\d[\d,]*\.?\d{0,2}", line)

        #     # print("Match:",matches)
        #     if matches:
        #         if len(matches) > 1:
        #             total_hmf = matches[0]
        #             total_entered_value = matches[1]
        #         else:
        #             total_hmf = matches[0]
        #             total_entered_value = None  # or handle as needed

        #         print("Total HMF:", total_hmf)
        #         print("Total Entered Value2:", total_entered_value)



        if line.startswith("501 - HMF"):
            matches = re.findall(r"\$\s?\d[\d,]*\.?\d{0,2}", line)
            if matches:
                total_hmf = matches[0]
                if len(matches) > 1:
                    total_entered_value = matches[1]  # only overwrite if it exists

                print("Total HMF:", total_hmf)
                print("Total Entered Value2:", total_entered_value)


        # Total Duty: look for keyword and get dollar value in the **next** line
        # Look for total duty amount that comes AFTER the line containing "Ascertained Duty"
        # if "Ascertained Duty" in line:
        #     # Look ahead up to 3 lines after current line to find a standalone dollar value
        #     for j in range(1, 4):
        #         if i + j < len(text_lines):
        #             next_line = text_lines[i + j].strip()
        #             match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
        #             if match:
        #                 total_duty = match.group()
        #                 print("Total Duty:", total_duty)
        #                 break



            total_duty = None
            for i, line in enumerate(text_lines):
                if "Ascertained Duty" in line:
                    found = False
                    # Check next 3 lines
                    for j in range(1, 4):
                        if i + j < len(text_lines):
                            next_line = text_lines[i + j].strip()
                            # print("j:", j)
                            # print("Next_Line:", next_line)

                            # First try: standalone dollar amount line
                            match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                            # print("Standalone Match:", match)

                            if match:
                                total_duty = match.group()
                                # print("Total Duty:", total_duty)
                                found = True
                                break

                            # Fallback: check if line contains multiple dollar values
                            fallback_matches = re.findall(r"\$\d[\d,]*\.\d{2}", next_line)
                            if fallback_matches:
                                total_duty = fallback_matches[-1]  # Pick the last value
                                print("Total Duty:", total_duty)
                                found = True
                                break

                    # If still not found, check if duty is embedded in the same line
                    if not found:
                        match = re.search(r"\$\d[\d,]*\.\d{2}\s+\$\d[\d,]*\.\d{2}", line)
                        if match:
                            amounts = re.findall(r"\$\d[\d,]*\.\d{2}", line)
                            if len(amounts) >= 2:
                                total_duty = amounts[1]  # Assuming second amount is duty
                                print("Total Duty:",total_duty)




        # Separate loop to extract Total Other Fees AFTER Total Duty has been found
            for i, line in enumerate(text_lines):
                if "Total Other Fees" in line:
                    for j in range(1, 4):  # Look ahead 3 lines
                        if i + j < len(text_lines):
                            next_line = text_lines[i + j].strip()
                            fee_match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                            if fee_match:
                                other_fees = fee_match.group()
                                print("Total Other Fees:", other_fees)
                                break
                    break  # stop after finding the first "Total Other Fees"
            for i, line in enumerate(text_lines):
                line = line.strip()
                if "Ascertained Other" in line:
                    for j in range(1, 4):
                        if i + j < len(text_lines):
                            next_line = text_lines[i + j].strip()
                            match = re.match(r"^\$\d[\d,]*\.\d{2}$", next_line)
                            # print(match)
                            if match:
                                total_other_fee2 = match.group()
                                print("Total Other Fee 2:", total_other_fee2)
                                break


            for i, line in enumerate(text_lines):
                line_lower = line.strip().lower()
                
                if "purchaser" in line_lower and "consignee" in line_lower:
                    # Try to find amount on the same line
                    match = re.search(r"\$\d[\d,]*\.\d{2}", text_lines[i])
                    if match:
                        total_duty_other_fee = match.group()
                        print("Total Duty Other Fee:", total_duty_other_fee)
                        break

                    # Try to look up to 3 lines BEFORE and AFTER
                    found = False
                    for j in range(1, 4):
                        # Look ahead
                        if i + j < len(text_lines):
                            match = re.search(r"\$\d[\d,]*\.\d{2}", text_lines[i + j])
                            if match:
                                total_duty_other_fee = match.group()
                                print("Total Duty Other Fee:", total_duty_other_fee)
                                found = True
                                break
                        # Look behind
                        if i - j >= 0:
                            match = re.search(r"\$\d[\d,]*\.\d{2}", text_lines[i - j])
                            if match:
                                total_duty_other_fee = match.group()
                                print("Total Duty Other Fee:", total_duty_other_fee)
                                found = True
                                break
                    if not found:
                        print("Total Duty Other Fee: Not Found")
                    break



        if "Totals for Invoice" in line:
            next_line = text_lines[i + 1].strip() if i + 1 < len(text_lines) else ""
            # print("Next Line if:", next_line)

            # Extract invoice number (10 digits)
            invoice_match = re.search(r"\b\d{10}\b", next_line)
            if invoice_match:
                current_item["Invoice Number"] = invoice_match.group()

            # Match both $9,175.00USD and $9,175.00 USD
            # value_matches = re.findall(r"\$\d[\d,]*\.\d{2}(?:\s*USD)", next_line)
            value_matches = re.findall(r"\$?\d[\d,]*\.\d{2}\s*USD", next_line)

            if len(value_matches) >= 2:
                current_item["Invoice Value"] = value_matches[0].replace(" ", "")
                current_item["Entered Value"] = value_matches[1].replace(" ", "")



    # Append the last item
    if current_item:
        extracted.append(current_item)


    return extracted


# Example input text
raw_text = """
DEPARTMENT OF HOMELAND SECURITY
EST : 2TI OMB APPROVAL NO. 1651-0022
U.S Customs and Border Protection EXPIRATION DATE 03/31/2025
ENTRY SUMMARY
1. Filer Code/Entry Number 2. Entry Type 3. Summary Date 4.Surety Number 5. Bond Type 6. Port Code 7. Entry Date
EKH-1012194-8 01 ABI/A 06/25/25 036 8 4102 06/14/25
8. Importing Carrier 9. Mode of Transport 10. Country Origin 11. Import Date
CMA CGM BIANCA 11 INDIA : IN 06/14/25
12. B/L or AWB No 13. Manufacture ID 14. Exporting Country 15. Export Date
CMDU CAD0810927, TKQV00045125 INVICAUT1219PAL INDIA :IN 05/11/25
16. I.T Number 17. I.T Date 18. Missing Docs 19. Foreign Port of Landin 20. U.S Port of Unlading
06/14/25 53306 1401
21. Location of Goods/ G.O Number 22. Consignee Number 23. Importer Number 24. Reference Number
H897 Voyage: 0INJQ 84-255476800 244701-23092
25.Ultimate Consignee Name (Last, First, M.I.) and Address 26. Importer of Record Name(Last, First, M.I.) and Address
LIGON HELICOPTER CORPORATION DBA TRIM STAR VICTORA AUTO PVT, LTD.
Street:3776 VAN DYKE RD Street:MUSTAKIL NO 54 AND 57 NO.
12,19,22 AND 2, HIND TERMNAL
Destination : USA :US Customer Reference : # TKQV00045125
City : ALMONT State : Mi ZIP : 48003-8047 City : Palwal State : HR ZIP : 121102 IN
32. 33. 34.
28. Description of Merchandise
A, ENTERED VALUE A. HTSUS Rate Duty and IR
27.
29. 30. 31. B. AD/CVD Rate
B. CHGS Tax
Line
A. HTSUS NO A. Gross Weight Net Quantity in C. IRC Rate
C. Relationship
No d. Visa Number Dollars Cents
B. AD/CVD NO. B. Manifest Qty HTSUS Units
001 OTH PRTS,ACCES,MOTOR VEHIC 65.00PKG 10 % $411.90
8708.99.81 527.00 KG $4,119 2.50 % $102.98
PRD ANY CTRY,EXC 99030126-0134 C $342
360NO
9903.01.25 N
499 - Merchandise Processing Fee 0.3464 % $14.27
501 - Harbor Maintenance Fee 0.1250 % $5.15
Totals for Invoice Invoice Value +/- MMV Exchange Entered Value
2523201693 4,119.00USD 1.00000 4,119.00USD
CBP USE ONLY TOTALS
A. LIQ CODE B. Ascertained Duty 37. Duty
Other Fee Summary (for Block 39 ) 35. Total Entered Value
499 - MPF $415.95 $15,009.67
$120,077.00
501 - HMF $150.12
REASON CODE C. Ascertained Tax 38. Tax
Total Other Fees
$566.07
D. Ascertained Other 39. Other
36. Declaration of Importer of Record ( Owner of Purchase )
$566.07
or Authorized Agent
E. Ascertained Total 40. Total
I declare that I am the Importer of record and that the actual owner,
$15,575.74
purchaser, or consignee for CBP purposes is as shown above, OR owner,
or purchaser or agent thereof. I further declare that the merchandise was obtained pursuant to a purchase or agreement to purchase and that the
prices set forth in the invoices are true, OR was not obtained pursuant to a purchase or agreement to purchase and the statements in the invoices as
to value or price are true to the best of my knowledge and belief. I also declare that the statements in the documents herein filed fully disclose to the best
of my knowledge and belief the true prices, values, quantities, rebates, drawbacks, fees, commissions, and royalties and are true and correct, and that all  
goods or services provided to the seller of the merchandise either free or at reduced cost are fully disclosed.
I will immediately furnish to the appropriate CBP officer any information showing a different statement of facts.
41. Declarant Name (Last, First, M.I.) Title Signature Date
NYC Supply Chain Solutions Inc/A-In-Fact 06/06/25
42.Broker/Filer Information Name(Last, First, M.I.) and Phone Number 43. Broker/Importer File Number
NYC Supply Chain Solutions Inc/A-In-Fact 1012194 / TKQV00045125
Hicksville, NY 11801 718-2761688
CBP Form 7501 (5/22) Page 1 of 4
"""

# # Split into lines and extract
text_lines = raw_text.strip().splitlines()
pdf_file = "EKH-1007198-6-7501.pdf"

extracted_data = extract_invoice_fields(text_lines, pdf_file)
print("Total Duty Other Fee:",extracted_data)
# Convert to JSON string
json_output = json.dumps(extracted_data, indent=4)
print(json_output)

# try:
#     print(f"Processing: {pdf_file}")
#     lines = extract_text_lines(pdf_file)
#     results = extract_invoice_fields(lines, os.path.basename(pdf_file))  # For multiple line items

#     # Save result
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(results, f, indent=4)
#     print(f"\nData saved to: {output_file}")

#     # Print summary
#     print("\nExtracted Values:")
#     print(json.dumps(results, indent=4))

# except Exception as e:
#     print(f"Error processing {pdf_file}: {str(e)}")
#     logging.error(f"Error processing {pdf_file}: {str(e)}")
#     exit(1)