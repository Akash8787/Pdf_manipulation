from invoice2data import extract_data  
from invoice2data.extract.loader import read_templates

temp1 = read_templates('Template/')
browse_file_var=r"D:\Python\Pdf_Manipulation\input_folder\EKH-1007199-6-7501.pdf"
try:
    ## result2 variable where   Invoices details data extracted
    result2 = extract_data(browse_file_var,templates=temp1)
    print("Result2:",result2)
    # print("--------------------------------")
except Exception as e:
    print('Error while fetching all invoices details '+str(e))


# from pdfminer.high_level import extract_text

# # Path to your PDF file
# pdf_path = r"D:\Python\Pdf_Manipulation\invoices\COMM 8599.pdf"

# # Extract all text
# text = extract_text(pdf_path)

# print(text)


# from pdfminer.high_level import extract_text
# import json

# # Path to your PDF file
# pdf_path = r"D:\Python\Pdf_Manipulation\invoices\COMM 8517.pdf"

# # Extract all text
# text = extract_text(pdf_path)

# # 1. Extract Manufacture & Exporter Details
# start_marker_exporter = "Manufacture & Exporter :\n"
# end_marker_exporter = "\nIEC Code:"
# start_index_exporter = text.find(start_marker_exporter) + len(start_marker_exporter)
# end_index_exporter = text.find(end_marker_exporter)

# if start_index_exporter == -1 or end_index_exporter == -1:
#     exporter_details = "Manufacture & Exporter details not found."
# else:
#     exporter_details = text[start_index_exporter:end_index_exporter].strip()

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

# # Print the extracted information (for verification)
# print("Manufacture & Exporter Details:")
# print(exporter_details)
# print("\nInvoice No.:")
# print(invoice_no)
# print("\nFOB Value IN USD:")
# print(fob_value)

# # Structure the data for JSON
# data = {
#     "Manufacture & Exporter": exporter_details,
#     "Invoice No.": invoice_no,
#     "FOB Value IN USD": fob_value
# }

# # Convert to JSON and print
# json_output = json.dumps(data, indent=4, ensure_ascii=False)
# print("\nJSON Output:")
# print(json_output)




# from pdfminer.high_level import extract_text
# import json
# import os

# # Path to the folder containing PDF files
# pdf_folder = r"D:\Python\Pdf_Manipulation\FOB   INV. DETAILS  USA TRIM STAR  CONT. NO. 42"

# # Path to the output .txt file
# output_file = os.path.join(pdf_folder, "output_json.txt")

# # Ensure the folder exists
# if not os.path.exists(pdf_folder):
#     print(f"Folder not found: {pdf_folder}")
#     exit(1)

# # List to store JSON data for all PDFs
# all_json_data = []

# # Iterate through all files in the folder
# for filename in os.listdir(pdf_folder):
#     if filename.lower().endswith(".pdf"):
#         # Full path to the PDF file
#         pdf_path = os.path.join(pdf_folder, filename)

#         # Extract all text
#         try:
#             text = extract_text(pdf_path)
#         except Exception as e:
#             print(f"Error extracting text from {filename}: {e}")
#             continue

#         # 1. Extract Manufacture & Exporter Details
#         start_marker_exporter = "Manufacture & Exporter :\n"
#         end_marker_exporter = "\nIEC Code:"
#         start_index_exporter = text.find(start_marker_exporter) + len(start_marker_exporter)
#         end_index_exporter = text.find(end_marker_exporter)

#         if start_index_exporter == -1 or end_index_exporter == -1:
#             exporter_details = "Manufacture & Exporter details not found."
#         else:
#             exporter_details = text[start_index_exporter:end_index_exporter].strip()

#         # 2. Extract Invoice No.
#         start_marker_invoice = "Invoice No: "
#         end_marker_invoice = "\n"
#         start_index_invoice = text.find(start_marker_invoice) + len(start_marker_invoice)
#         end_index_invoice = text.find(end_marker_invoice, start_index_invoice)

#         if start_index_invoice == -1 or end_index_invoice == -1:
#             invoice_no = "Invoice No. not found."
#         else:
#             invoice_no = text[start_index_invoice:end_index_invoice].strip()

#         # 3. Extract FOB Value IN USD
#         start_marker_fob = "FOB Value IN USD - "
#         end_marker_fob = "\n"
#         start_index_fob = text.find(start_marker_fob) + len(start_marker_fob)
#         end_index_fob = text.find(end_marker_fob, start_index_fob)

#         if start_index_fob == -1 or end_index_fob == -1:
#             fob_value = "FOB Value not found."
#         else:
#             fob_value = text[start_index_fob:end_index_fob].strip()

#         # Structure the data for JSON, including the PDF filename
#         data = {
#             "pdf_file": filename,
#             "Manufacture & Exporter": exporter_details,
#             "Invoice No.": invoice_no,
#             "FOB Value IN USD": fob_value
#         }

#         # Append to the list of all JSON data
#         all_json_data.append(data)
#         print(f"Processed {filename}")

# # Save all JSON data to a single .txt file
# try:
#     with open(output_file, "w", encoding="utf-8") as f:
#         # Write as a JSON array for clarity
#         json.dump(all_json_data, f, indent=4, ensure_ascii=False)
#     print(f"Saved all JSON data to {output_file}")
# except Exception as e:
#     print(f"Error saving JSON to {output_file}: {e}")
#=============================================================================================================

#Sagar

# from pdfminer.high_level import extract_text
# import json
# import os
# import re

# # Path to the folder containing PDF files
# pdf_folder = r"D:\Python\Pdf_Manipulation\invoices"

# # Path to the output .txt file
# output_file = os.path.join(pdf_folder, "output_json.txt")

# # Ensure the folder exists
# if not os.path.exists(pdf_folder):
#     print(f"Folder not found: {pdf_folder}")
#     exit(1)

# # List to store JSON data for all PDFs
# all_json_data = []

# def clean_exporter_details(text):
#     """Remove unwanted prefixes (like 'rter:') and their trailing newlines."""
#     # Remove any word characters + ":" at the start, along with the following newline
#     cleaned = re.sub(r'^\w+:\n', '', text.strip())
#     # Also handle cases where there's extra whitespace or variations
#     cleaned = re.sub(r'^\s*\w+[: ]*\n', '', cleaned)
#     # Remove trailing invoice info if present
#     cleaned = re.sub(r'\n\nInvoice No:.*', '', cleaned, flags=re.DOTALL)
#     return cleaned.strip()

# # Iterate through all files in the folder
# for filename in os.listdir(pdf_folder):
#     if filename.lower().endswith(".pdf"):
#         # Full path to the PDF file
#         pdf_path = os.path.join(pdf_folder, filename)

#         # Extract all text
#         try:
#             text = extract_text(pdf_path)
#         except Exception as e:
#             print(f"Error extracting text from {filename}: {e}")
#             continue

#         # 1. Extract Manufacture & Exporter Details
#         start_marker_exporter = "Manufacture & Exporter :\n"
#         end_marker_exporter = "\nIEC Code:"
#         start_index_exporter = text.find(start_marker_exporter) + len(start_marker_exporter)
#         end_index_exporter = text.find(end_marker_exporter)

#         if start_index_exporter == -1 or end_index_exporter == -1:
#             exporter_details = "Manufacture & Exporter details not found."
#         else:
#             exporter_details = clean_exporter_details(text[start_index_exporter:end_index_exporter])

#         # 2. Extract Invoice No.
#         start_marker_invoice = "Invoice No: "
#         end_marker_invoice = "\n"
#         start_index_invoice = text.find(start_marker_invoice) + len(start_marker_invoice)
#         end_index_invoice = text.find(end_marker_invoice, start_index_invoice)

#         if start_index_invoice == -1 or end_index_invoice == -1:
#             invoice_no = "Invoice No. not found."
#         else:
#             invoice_no = text[start_index_invoice:end_index_invoice].strip()

#         # 3. Extract FOB Value IN USD
#         start_marker_fob = "FOB Value IN USD - "
#         end_marker_fob = "\n"
#         start_index_fob = text.find(start_marker_fob) + len(start_marker_fob)
#         end_index_fob = text.find(end_marker_fob, start_index_fob)

#         if start_index_fob == -1 or end_index_fob == -1:
#             fob_value = "FOB Value not found."
#         else:
#             fob_value = text[start_index_fob:end_index_fob].strip()

#         # Structure the data for JSON, including the PDF filename
#         data = {
#             "pdf_file": filename,
#             "Manufacture & Exporter": exporter_details,
#             "Invoice No.": invoice_no,
#             "FOB Value IN USD": fob_value
#         }

#         # Append to the list of all JSON data
#         all_json_data.append(data)
#         print(f"Processed {filename}")

# # Save all JSON data to a single .txt file
# try:
#     with open(output_file, "w", encoding="utf-8") as f:
#         # Write as a JSON array for clarity
#         json.dump(all_json_data, f, indent=4, ensure_ascii=False)
#     print(f"Saved all JSON data to {output_file}")
# except Exception as e:
#     print(f"Error saving JSON to {output_file}: {e}")