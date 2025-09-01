# from pdfminer.high_level import extract_text
# import json
# import os
# import re

# # Path to the single PDF file
# pdf_file = r"D:\latest_Error\19therror\FOB INV. DETAILS USA  COLUMBUS  CONT. NO. 12\COMM 13200075.pdf"

# # List to store JSON data
# json_data = []

# def clean_exporter_details(text):
#     """Extract exporter details after the marker, stopping before IEC Code, Rex No, or Invoice No."""
#     # Regex to capture all text until the end markers
#     pattern = r'^(.*?)(?=\n(?:IEC Code:|Rex No:|Invoice No:|$))'
#     match = re.match(pattern, text, re.DOTALL | re.MULTILINE)
#     if match:
#         result = match.group(1).strip()
#         print(f"Regex matched for exporter details: {result}")
#         return result
#     print(f"Regex failed for text: {text}")
#     return "Exporter details not found."

# # Check if the file exists and is a PDF
# if not os.path.exists(pdf_file) or not pdf_file.lower().endswith(".pdf"):
#     print(f"Invalid or missing PDF file: {pdf_file}")
#     exit(1)

# # Extract all text
# try:
#     text = extract_text(pdf_file)
#     # print(text[:1000])  # Uncomment to inspect extracted text
# except Exception as e:
#     print(f"Error extracting text from {pdf_file}: {e}")
#     exit(1)

# # 1. Extract Manufacture & Exporter Details
# start_marker_exporter1 = "Manufacture & Exporter :"
# start_marker_exporter2 = "Exporter:"
# end_marker_exporter1 = "\nIEC Code:"
# end_marker_exporter2 = "\nRex No:"
# end_marker_exporter3 = "\nInvoice No:"

# start_index_exporter = text.find(start_marker_exporter1)
# if start_index_exporter != -1:
#     start_index_exporter += len(start_marker_exporter1)
# else:
#     start_index_exporter = text.find(start_marker_exporter2)
#     if start_index_exporter != -1:
#         start_index_exporter += len(start_marker_exporter2)

# end_index_exporter = text.find(end_marker_exporter1)
# if end_index_exporter == -1:
#     end_index_exporter = text.find(end_marker_exporter2)
# if end_index_exporter == -1:
#     end_index_exporter = text.find(end_marker_exporter3)

# if start_index_exporter == -1 or end_index_exporter == -1:
#     exporter_details = "Manufacture & Exporter details not found."
# else:
#     extracted_text = text[start_index_exporter:end_index_exporter]
#     print(f"Extracted text for exporter: {extracted_text}")
#     exporter_details = clean_exporter_details(extracted_text)

# # 2. Extract Invoice No.
# start_marker_invoice = "Invoice No: "
# end_marker_invoice = "\n"
# start_index_invoice = text.find(start_marker_invoice) + len(start_marker_invoice)
# end_index_invoice = text.find(end_marker_invoice, start_index_invoice)

# if start_index_invoice == -1 or end_index_invoice == -1:
#     invoice_no = "Invoice No. not found."
# else:
#     invoice_no = text[start_index_invoice:end_index_invoice].strip()

# # 3. Extract FOB Value IN USD
# start_marker_fob = "FOB Value IN USD - "
# end_marker_fob = "\n"
# start_index_fob = text.find(start_marker_fob) + len(start_marker_fob)
# end_index_fob = text.find(end_marker_fob, start_index_fob)

# if start_index_fob == -1 or end_index_fob == -1:
#     fob_value = "FOB Value not found."
# else:
#     fob_value = text[start_index_fob:end_index_fob].strip()

# # Structure the data for JSON, including the PDF filename
# data = {
#     "pdf_file": os.path.basename(pdf_file),
#     "Manufacture & Exporter": exporter_details,
#     "Invoice No.": invoice_no,
#     "FOB Value IN USD": fob_value
# }

# # Check if we should skip this record
# if "not found" not in exporter_details:
#     try:
#         # Attempt to convert FOB value to float
#         fob_numeric = float(fob_value.replace(',', '').strip())
#         data["FOB Value IN USD"] = fob_numeric  # Store the parsed float
#         json_data.append(data)
#         print(f"Processed {os.path.basename(pdf_file)}")
#     except ValueError:
#         print(f"Skipped {os.path.basename(pdf_file)} due to invalid FOB value: {fob_value}")
# else:
#     print(f"Skipped {os.path.basename(pdf_file)} due to missing exporter details.")

# # Print JSON data
# print(json.dumps(json_data, indent=4, ensure_ascii=False))

# # Create list of invoice and FOB values
# invoice_fob_list = [(item["Invoice No."], item["FOB Value IN USD"]) for item in json_data]

# # Print the extracted invoice numbers and FOB values
# for invoice, fob in invoice_fob_list:
#     print(f"Invoice No.: {invoice}, FOB Value IN USD: {fob}")

#====================================================================================================================
from pdfminer.high_level import extract_text
import json
import os
import re

# Path to the folder containing PDF files
pdf_folder = r"D:\latest_Error\45therror\FOB INV. DETAILS US COLUMBUS CONT.NO. 19"

# List to store JSON data for all PDFs
json_data = []

def clean_exporter_details(text):
    """Extract exporter details, including Rex No if present, stopping before IEC Code or Invoice No."""
    # Regex to capture exporter details and Rex No (if present) in one group
    pattern = r'^(.*?)(?:\nRex No:[^\n]*)?(?=\n(?:IEC Code:|Invoice No:|$))'
    match = re.match(pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        result = match.group(0).strip()  # Use group(0) to include Rex No if matched
        print(f"Regex matched for exporter details: {result}")
        return result
    print(f"Regex failed for text: {text}")
    return "Exporter details not found."

# Ensure the folder exists
if not os.path.exists(pdf_folder):
    print(f"Folder not found: {pdf_folder}")
    exit(1)



# Ensure the folder exists
if not os.path.exists(pdf_folder):
    print(f"Folder not found: {pdf_folder}")
    exit(1)

# List PDF files
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
print(f"Files in folder: {pdf_files}")

# Iterate through all PDF files in the folder
for filename in pdf_files:
    # Full path to the PDF file
    pdf_path = os.path.join(pdf_folder, filename)

    # Extract all text
    try:
        text = extract_text(pdf_path)
        print(f"Extracted text from {filename} (first 200 chars): {text[:200]}")
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        continue

    # 1. Extract Manufacture & Exporter Details
    start_marker_exporter1 = "Manufacture & Exporter :"
    start_marker_exporter2 = "Exporter:"
    end_marker_exporter1 = "\nIEC Code:"
    end_marker_exporter2 = "\nRex No:"
    end_marker_exporter3 = "\nInvoice No:"

    start_index_exporter = text.find(start_marker_exporter1)
    if start_index_exporter != -1:
        start_index_exporter += len(start_marker_exporter1)
    else:
        start_index_exporter = text.find(start_marker_exporter2)
        if start_index_exporter != -1:
            start_index_exporter += len(start_marker_exporter2)

    end_index_exporter = text.find(end_marker_exporter1)
    if end_index_exporter == -1:
        end_index_exporter = text.find(end_marker_exporter2)
    if end_index_exporter == -1:
        end_index_exporter = text.find(end_marker_exporter3)

    if start_index_exporter == -1 or end_index_exporter == -1:
        exporter_details = "Manufacture & Exporter details not found."
    else:
        extracted_text = text[start_index_exporter:end_index_exporter]
        print(f"Extracted text for {filename}: {extracted_text}")
        exporter_details = clean_exporter_details(extracted_text)

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
    data = {
        "pdf_file": filename,
        "Manufacture & Exporter": exporter_details,
        "Invoice No.": invoice_no,
        "FOB Value IN USD": fob_value
    }

    # Check if we should skip this record
    if "not found" not in exporter_details:
        try:
            # Attempt to convert FOB value to float
            fob_numeric = float(fob_value.replace(',', '').strip())
            data["FOB Value IN USD"] = fob_numeric  # Store the parsed float
            json_data.append(data)
            print(f"Processed {filename}")
        except ValueError:
            print(f"Skipped {filename} due to invalid FOB value: {fob_value}")
    else:
        print(f"Skipped {filename} due to missing exporter details.")

# Print JSON data
print(json.dumps(json_data, indent=4, ensure_ascii=False))

# Create list of invoice and FOB values
invoice_fob_list = [(item["Invoice No."], item["FOB Value IN USD"]) for item in json_data]

# Print the extracted invoice numbers and FOB values
for invoice, fob in invoice_fob_list:
    print(f"Invoice No.: {invoice}, FOB Value IN USD: {fob}")