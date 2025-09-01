# import pdfplumber
# import json
# import os
# import re
# import logging

# # Set up logging
# logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# # Path to the PDF file
# pdf_file = r"D:\Python\Amount_Validation\EKH-1007198-6-7501 (1)[0].PDF"

# # Derive the directory from the PDF file path
# pdf_dir = os.path.dirname(pdf_file)

# # Path to the output .txt file (in the same directory as the PDF)
# output_file = os.path.join(pdf_dir, "output_json.txt")

# # Ensure the PDF file exists
# if not os.path.exists(pdf_file):
#     print(f"PDF file not found: {pdf_file}")
#     exit(1)
# if not os.path.isfile(pdf_file):
#     print(f"Path is not a file: {pdf_file}")
#     exit(1)

# def clean(var):
#     """Clean a string by removing currency symbols, commas, and percentages, and converting to float."""
#     if not isinstance(var, str):
#         return var
#     var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '').strip()
#     if var.lower() in ('no', 'n', 'free'):
#         return 0.0
#     try:
#         return float(var)
#     except ValueError:
#         return var

# def extract_invoices(pdf_text):
#     """Extract data from one or more invoices in the text."""
#     try:
#         # Split text into lines (row-wise)
#         text_lines = pdf_text.strip().split('\n')
        
#         # Print each row to confirm row-wise extraction
#         print("Extracted Text (Row-wise):")
#         for i, row in enumerate(text_lines, 1):
#             print(f"Row {i}: {row}")

#         # Find the start of the invoice data (after header)
#         start_idx = 0
#         for i, line in enumerate(text_lines):
#             if re.match(r'\d+\s+PKG', line.strip()):
#                 start_idx = i
#                 break
        
#         # Process the invoice block (from start_idx to the end)
#         invoice_lines = text_lines[start_idx:]
#         # invoice_data = process_invoice_block(invoice_lines)

#         # return [invoice_lines]  # Return as a list for consistency
#         return [{
#     'lines': invoice_lines
# }]


#     except Exception as e:
#         error_msg = f"Error processing invoice: {str(e)}"
#         print(error_msg)
#         logging.error(error_msg)
#         return []

# # Process the PDF file using pdfplumber
# all_invoices = []
# print(f"Processing: {pdf_file}")

# try:
#     # Extract text from the PDF using pdfplumber
#     pdf_text = ""
#     with pdfplumber.open(pdf_file) as pdf:
#         for page in pdf.pages:
#             # Extract text from the page
#             text = page.extract_text()
#             if text:
#                 pdf_text += text + "\n"

#     if not pdf_text.strip():
#         raise ValueError("Extracted text is empty. The PDF might be scanned or corrupted.")
    
#     # Extract invoice data row-wise
#     invoices = extract_invoices(pdf_text)
#     for invoice in invoices:
#         invoice['source_file'] = os.path.basename(pdf_file)  # Add source file info
#         all_invoices.append(invoice)
    
#     # Calculate totals for validation
#     mpf_total = sum(invoice['fees']['mpf']['amount'] for invoice in invoices if 'mpf' in invoice['fees'])
#     hmf_total = sum(invoice['fees']['hmf']['amount'] for invoice in invoices if 'hmf' in invoice['fees'])
#     print(f"\nMPF Total for {os.path.basename(pdf_file)}: {mpf_total}")
#     print(f"HMF Total for {os.path.basename(pdf_file)}: {hmf_total}")

# except Exception as e:
#     error_msg = f"Error processing {pdf_file}: {str(e)}"
#     print(error_msg)
#     logging.error(error_msg)
#     exit(1)

# # Save the extracted data to the output file
# try:
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(all_invoices, f, indent=4)
#     print(f"Data saved to: {output_file}")
# except Exception as e:
#     error_msg = f"Error saving to {output_file}: {str(e)}"
#     print(error_msg)
#     logging.error(error_msg)
#     exit(1)



# rows= extract_invoices()


# line_number = duty = mpf = hmf = invoice_number = invoice_value = entered_value = ""

# # Extract from duty line
# duty_line = next((r for r in rows if re.match(r'^\d{3}\s', r)), "")
# if duty_line:
#     parts = duty_line.split()
#     line_number = parts[0]
#     entered_value = re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', duty_line).group(0)
#     duty_match = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', duty_line)
#     if len(duty_match) > 1:
#         duty = duty_match[1]

# # Extract MPF and HMF
# for r in rows:
#     if 'Merchandise Processing Fee' in r:
#         mpf = re.search(r'\$\d+\.\d{2}', r).group(0)
#     elif 'Harbor Maintenance Fee' in r:
#         hmf = re.search(r'\$\d+\.\d{2}', r).group(0)

# # Extract Invoice number and value
# invoice_row = next((r for r in rows if re.match(r'^\d{10}', r)), "")
# if invoice_row:
#     parts = invoice_row.split()
#     invoice_number = parts[0]
#     invoice_value = f"{parts[1]} {parts[2]}"

# # Final result
# result = {
#     "Line": line_number,
#     "Entered Value": entered_value,
#     "Duty": duty,
#     "MPF": mpf,
#     "HMF": hmf,
#     "Invoice Number": invoice_number,
#     "Invoice Value": invoice_value
# }

# # Output in desired format
# formatted_result = f'{{{line_number},{entered_value},{duty},{mpf},{hmf}, {invoice_number}, {invoice_value}}}'
# print(formatted_result)



# import pdfplumber
# import json
# import os
# import re
# import logging

# # Setup logging
# logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# # PDF input path
# pdf_file = r"D:\Python\Amount_Validation\EKH-1007199-6-7501.pdf"
# pdf_dir = os.path.dirname(pdf_file)
# output_file = os.path.join(pdf_dir, "output_json.txt")

# # Check file existence
# if not os.path.exists(pdf_file) or not os.path.isfile(pdf_file):
#     print(f"PDF file not found or invalid: {pdf_file}")
#     exit(1)

# def clean(var):
#     """Remove currency symbols, commas, percentages, and convert to float."""
#     if not isinstance(var, str):
#         return var
#     var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '').strip()
#     if var.lower() in ('no', 'n', 'free'):
#         return 0.0
#     try:
#         return float(var)
#     except ValueError:
#         return var

# def extract_text_lines(pdf_file):
#     """Extract text line by line from all pages."""
#     try:
#         pdf_text = ""
#         with pdfplumber.open(pdf_file) as pdf:
#             # for page in pdf.pages:
#             for i, page in enumerate(pdf.pages, start=1):

#                 text = page.extract_text()
#                 # print(f"\n--- Page {i} ---\n{text}\n")

#                 if text:
#                     pdf_text += text + "\n"
#                     print(pdf_text)
                    
#         if not pdf_text.strip():
#             raise ValueError("Extracted text is empty. The PDF might be scanned or corrupted.")
#         return pdf_text.strip().split('\n')
#     except Exception as e:
#         logging.error(f"Error reading PDF: {str(e)}")
#         raise

# def extract_invoice_fields(text_lines):
#     """Extract fields like Duty, MPF, HMF, Invoice number/value from lines."""
#     line_number = duty = mpf = hmf = invoice_number = invoice_value = entered_value = ""

#     # Extract from duty line (starts with 3 digits)
#     duty_line = next((r for r in text_lines if re.match(r'^\d{3}\s', r)), "")
#     if duty_line:
#         parts = duty_line.split()
#         line_number = parts[0]
#         dollar_values = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', duty_line)
#         if dollar_values:
#             entered_value = dollar_values[0]
#         if len(dollar_values) > 1:
#             duty = dollar_values[1]

#     # Extract MPF and HMF
#     for r in text_lines:
#         if 'Merchandise Processing Fee' in r:
#             match = re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', r)
#             if match:
#                 mpf = match.group(0)
#         elif 'Harbor Maintenance Fee' in r:
#             match = re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', r)
#             if match:
#                 hmf = match.group(0)

#     # Extract Invoice number and value
#     invoice_row = next((r for r in text_lines if re.match(r'^\d{10}', r)), "")
#     if invoice_row:
#         parts = invoice_row.split()
#         if len(parts) >= 3:
#             invoice_number = parts[0]
#             invoice_value = f"{parts[1]} {parts[2]}"

#     return {
#         "Line": line_number,
#         "Extracted Value": entered_value,
#         "Duty": duty,
#         "MPF": mpf,
#         "HMF": hmf,
#         "Invoice Number": invoice_number,
#         "Invoice Value": invoice_value,
#         "Source File": os.path.basename(pdf_file)
#     }

# # --- Main execution ---
# try:
#     print(f"Processing: {pdf_file}")
#     lines = extract_text_lines(pdf_file)
#     result = extract_invoice_fields(lines)

#     # Save result
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(result, f, indent=4)
#     print(f"Data saved to: {output_file}")

#     # Print summary
#     print("\nExtracted Values:")
#     print(json.dumps(result, indent=4))

# except Exception as e:
#     print(f"Error processing {pdf_file}: {str(e)}")
#     logging.error(f"Error processing {pdf_file}: {str(e)}")
#     exit(1)






# import pdfplumber
# import json
# import os
# import re
# import logging

# # Setup logging
# logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# # PDF input path
# pdf_file = r"D:\Python\Amount_Validation\EKH-1007199-6-7501.pdf"
# pdf_dir = os.path.dirname(pdf_file)
# output_file = os.path.join(pdf_dir, "output_json.txt")

# # Check file existence
# if not os.path.exists(pdf_file) or not os.path.isfile(pdf_file):
#     print(f"PDF file not found or invalid: {pdf_file}")
#     exit(1)

# def clean(var):
#     """Remove currency symbols, commas, percentages, and convert to float."""
#     if not isinstance(var, str):
#         return var
#     var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '').strip()
#     if var.lower() in ('no', 'n', 'free'):
#         return 0.0
#     try:
#         return float(var)
#     except ValueError:
#         return var

# def extract_text_lines(pdf_file):
#     """Extract text line by line from all pages."""
#     try:
#         pdf_text = ""
#         with pdfplumber.open(pdf_file) as pdf:
#             for i, page in enumerate(pdf.pages, start=1):
#                 text = page.extract_text()
#                 if text:
#                     pdf_text += text + "\n"
#         if not pdf_text.strip():
#             raise ValueError("Extracted text is empty. The PDF might be scanned or corrupted.")
#         return pdf_text.strip().split('\n')
#     except Exception as e:
#         logging.error(f"Error reading PDF: {str(e)}")
#         raise

# def extract_invoice_fields(text_lines):
#     """Extract fields like Duty, MPF, HMF, Invoice number/value from lines."""
#     line_number = duty = mpf = hmf = invoice_number = invoice_value = entered_value = ""

#     # Extract from duty line (starts with 3 digits)
#     duty_line = next((r for r in text_lines if re.match(r'^\d{3}\s', r)), "")
#     if duty_line:
#         parts = duty_line.split()
#         line_number = parts[0]
#         dollar_values = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', duty_line)
#         if dollar_values:
#             duty = dollar_values[1] if len(dollar_values) > 1 else ""
#         if dollar_values:
#             extracted_value = dollar_values[0]
#         else:
#             extracted_value = ""

#     # Extract MPF and HMF
#     for r in text_lines:
#         if 'Merchandise Processing Fee' in r:
#             match = re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', r)
#             if match:
#                 mpf = match.group(0)
#         elif 'Harbor Maintenance Fee' in r:
#             match = re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', r)
#             if match:
#                 hmf = match.group(0)

#     # Extract Invoice Number and both values from line with pattern: 2423201238 7,264.00 USD 1.00000 7,264.00 USD
#     invoice_line = next((r for r in text_lines if re.match(r'^\d{10}\s', r) and 'USD' in r), "")
#     if invoice_line:
#         parts = invoice_line.split()
#         if len(parts) >= 5:
#             invoice_number = parts[0]
#             invoice_value = parts[1] + " " + parts[2]  # First "7,264.00 USD"
#             entered_value = parts[4] + " " + parts[5]  # Second "7,264.00 USD"

#     return {
#         "Line": line_number,
#         "Extracted Value": extracted_value,
#         "Duty": duty,
#         "MPF": mpf,
#         "HMF": hmf,
#         "Invoice Number": invoice_number,
#         "Invoice Value": invoice_value,
#         "Entered Value": entered_value,
#         "Source File": os.path.basename(pdf_file)
#     }

# # --- Main execution ---
# try:
#     print(f"Processing: {pdf_file}")
#     lines = extract_text_lines(pdf_file)
#     result = extract_invoice_fields(lines)

#     # Save result
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(result, f, indent=4)
#     print(f"Data saved to: {output_file}")

#     # Print summary
#     print("\nExtracted Values:")
#     print(json.dumps(result, indent=4))

# except Exception as e:
#     print(f"Error processing {pdf_file}: {str(e)}")
#     logging.error(f"Error processing {pdf_file}: {str(e)}")
#     exit(1)











import pdfplumber
import json
import os
import re
import logging

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

# PDF input path
pdf_file = r"D:\Python\Amount_Validation\EKH-1007198-6-7501 (1)[0].PDF"
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
        # Add currency symbol if required (for MPF, HMF)
        if add_currency:
            return f"${cleaned_value:.2f}"
        # Add USD if required (for Invoice Value and Entered Value)
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

def extract_invoice_fields(text_lines):
    """Extract fields like Duty, MPF, HMF, Invoice number/value from lines."""
    line_number = duty = mpf = hmf = invoice_number = invoice_value = entered_value = extracted_value = ""

    # Extract from duty line (starts with 3 digits)
    duty_line = next((r for r in text_lines if re.match(r'^\d{3}\s', r)), "")
    if duty_line:
        parts = duty_line.split()
        line_number = parts[0]
        dollar_values = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', duty_line)
        if dollar_values:
            duty = clean(dollar_values[1] if len(dollar_values) > 1 else "")
        extracted_value = clean(dollar_values[0], add_currency=True) if dollar_values else ""

    # Extract MPF and HMF based on specific keywords, ensuring we get the correct amounts
    mpf_line = next((r for r in text_lines if 'Merchandise Processing Fee' in r), "")
    if mpf_line:
        mpf_values = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', mpf_line)
        if mpf_values:
            mpf = clean(mpf_values[-1], add_currency=True)  # Last value in the list is the actual MPF amount
            print("Mpf:",mpf)

    hmf_line = next((r for r in text_lines if 'Harbor Maintenance Fee' in r), "")
    if hmf_line:
        hmf_values = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', hmf_line)
        if hmf_values:
            hmf = clean(hmf_values[-1], add_currency=True)  # Last value in the list is the actual HMF amount

    # Extract Invoice Number and both values from line with pattern: 2423201238 7,264.00 USD 1.00000 7,264.00 USD
    invoice_line = next((r for r in text_lines if re.match(r'^\d{10}\s', r) and 'USD' in r), "")
    if invoice_line:
        parts = invoice_line.split()
        if len(parts) >= 5:
            invoice_number = parts[0]
            invoice_value = clean(parts[1] + " " + parts[2], add_usd=True)  # First "7,264.00 USD"
            entered_value = clean(parts[4] + " " + parts[5], add_usd=True)  # Second "7,264.00 USD"

    return {
        "Line": line_number,
        "Extracted Value": extracted_value,
        "Duty1": duty,
        "MPF": mpf,
        "HMF": hmf,
        "Invoice Number": invoice_number,
        "Invoice Value": invoice_value,
        "Entered Value": entered_value,
        "Source File": os.path.basename(pdf_file)
    }


# --- Main execution ---
try:
    print(f"Processing: {pdf_file}")
    lines = extract_text_lines(pdf_file)
    results = extract_invoice_fields(lines)

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





