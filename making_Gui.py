import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import math
import logging
import pdfplumber
import re
from pdfminer.high_level import extract_text

# Setup logging
logging.basicConfig(filename='invoice_processing.log', level=logging.ERROR)

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

def clean(var, add_currency=False, add_usd=False):
    """Remove currency symbols, commas, percentages, and convert to float."""
    if not isinstance(var, str):
        return float(var) if var else 0.0
    var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '').strip()
    if var.lower() in ('no', 'n', 'free', ''):
        return 0.0
    try:
        cleaned_value = float(var)
        if add_currency:
            return f"${cleaned_value:.2f}"
        if add_usd:
            return f"{cleaned_value:.2f} USD"
        return cleaned_value
    except ValueError:
        return 0.0

def clean_exporter_details(text):
    """Remove unwanted prefixes (like 'rter:') and their trailing newlines."""
    cleaned = re.sub(r'^\w+:\n', '', text.strip())
    cleaned = re.sub(r'^\s*\w+[: ]*\n', '', cleaned)
    cleaned = re.sub(r'\n\nInvoice No:.*', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

def extract_invoice_folder_data(invoice_folder):
    """Extract data from PDFs in the invoice folder using pdfminer."""
    all_json_data = []
    if not os.path.exists(invoice_folder):
        return all_json_data, f"Invoice folder not found: {invoice_folder}"

    for filename in os.listdir(invoice_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(invoice_folder, filename)
            try:
                text = extract_text(pdf_path)
            except Exception as e:
                print(f"Error extracting text from {filename}: {e}")
                continue

            # Extract Manufacture & Exporter Details
            start_marker_exporter = "Manufacture & Exporter :\n"
            end_marker_exporter = "\nIEC Code:"
            start_index_exporter = text.find(start_marker_exporter) + len(start_marker_exporter)
            end_index_exporter = text.find(end_marker_exporter)
            if start_index_exporter == -1 or end_index_exporter == -1:
                exporter_details = "Manufacture & Exporter details not found."
            else:
                exporter_details = clean_exporter_details(text[start_index_exporter:end_index_exporter])

            # Extract Invoice No.
            start_marker_invoice = "Invoice No: "
            end_marker_invoice = "\n"
            start_index_invoice = text.find(start_marker_invoice) + len(start_marker_invoice)
            end_index_invoice = text.find(end_marker_invoice, start_index_invoice)
            if start_index_invoice == -1 or end_index_invoice == -1:
                invoice_no = "Invoice No. not found."
            else:
                invoice_no = text[start_index_invoice:end_index_invoice].strip()

            # Extract FOB Value IN USD
            start_marker_fob = "FOB Value IN USD - "
            end_marker_fob = "\n"
            start_index_fob = text.find(start_marker_fob) + len(start_marker_fob)
            end_index_fob = text.find(end_marker_fob, start_index_fob)
            if start_index_fob == -1 or end_index_fob == -1:
                fob_value = "FOB Value not found."
            else:
                fob_value = text[start_index_fob:end_index_fob].strip()

            # Structure the data
            data = {
                "pdf_file": filename,
                "Manufacture & Exporter": exporter_details,
                "Invoice No.": invoice_no,
                "FOB Value IN USD": fob_value
            }

            # Skip if exporter details are missing
            if "not found" in exporter_details:
                continue

            try:
                fob_numeric = float(fob_value.replace(',', '').strip())
                data["FOB Value IN USD"] = fob_numeric
            except ValueError:
                print(f"Skipped {filename} due to invalid FOB value: {fob_value}")
                continue

            all_json_data.append(data)
            print(f"Processed {filename}")

    return all_json_data, ""

# Set dummy values for expected totals
total_duty = ""
total_mpf = ""
total_hmf = ""

def process_pdf(pdf_file):
    try:
        output = f"Processing main PDF: {pdf_file}\n"
        invoice_folder = entry_invoice_folder.get().strip() or r"D:\Python\Amount_Validation\59therror\FOB INV. DETAILS US ATRIM STAR CONT. NO. 15"

        # Process main PDF with pdfplumber
        lines = extract_text_lines(pdf_file)
        results = extract_invoice_fields(lines, os.path.basename(pdf_file))

        # output += "\n--- Extracted Values from Main PDF ---\n"
        # output += json.dumps(results, indent=4) + "\n"

        total_added_duty = 0.0
        total_added_mpf = 0.0
        total_added_hmf = 0.0

        for item in results:
            total_added_duty += clean(item.get("Duty1", 0))
            total_added_duty += clean(item.get("Duty2", 0))
            total_added_mpf += clean(item.get("MPF", 0))
            total_added_hmf += clean(item.get("HMF", 0))

        # output += "\n--- Totals Calculated ---\n"
        # output += f"Total Duty: ${total_added_duty:.2f}\n"
        # output += f"Total MPF: ${total_added_mpf:.2f}\n"
        # output += f"Total HMF: ${total_added_hmf:.2f}\n"

        # Compare with given totals
        total_duty_val = float(clean(total_duty))
        total_mpf_val = float(clean(total_mpf))
        total_hmf_val = float(clean(total_hmf))
        tolerance = 1e-6

        output += "\n--- Comparison Results for Totals ---\n"
        output += "✅ Total Duty matches.\n" if math.isclose(total_added_duty, total_duty_val, abs_tol=tolerance) \
            else f"❌ Total Duty mismatch! Expected: {total_duty_val}, Found: {total_added_duty:.2f}\n"
        output += "✅ Total MPF matches.\n" if math.isclose(total_added_mpf, total_mpf_val, abs_tol=tolerance) \
            else f"❌ Total MPF mismatch! Expected: {total_mpf_val}, Found: {total_added_mpf:.2f}\n"
        output += "✅ Total HMF matches.\n" if math.isclose(total_added_hmf, total_hmf_val, abs_tol=tolerance) \
            else f"❌ Total HMF mismatch! Expected: {total_hmf_val}, Found: {total_added_hmf:.2f}\n"

        # Process invoice folder with pdfminer
        # output += "\n--- Processing Invoice Folder ---\n"
        all_json_data, error_msg = extract_invoice_folder_data(invoice_folder)
        if error_msg:
            output += f"❌ {error_msg}\n"
            return output

        # output += f"Processed {len(all_json_data)} invoice PDFs\n"

        # Compare invoice data without including detailed JSON data in GUI output
        output += "\n--- Invoice Comparison Results ---\n"
        invoice_fob_list = [(item["Invoice No."], item["FOB Value IN USD"]) for item in all_json_data]
        matched_invoices = set()

        for invoice, fob in invoice_fob_list:
            found = False
            for item in results:
                if str(item["Invoice Number"]).strip() == str(invoice).strip():
                    found = True
                    matched_invoices.add(invoice)
                    # output += f"Matched Invoice: {item['Invoice Number']}\n"
                    entered_value = clean(item.get("Entered Value", "0"))
                    invoice_value = clean(item.get("Invoice Value", "0"))
                    if (math.isclose(fob, entered_value, rel_tol=1e-3) and
                        math.isclose(fob, invoice_value, rel_tol=1e-3)):
                        output += f"for Invoice No. {invoice} OK ✅ \n"
                    else:
                        output += f"❌ Value mismatch for Invoice No. {invoice}: FOB={fob}, Entered={entered_value}, Invoice={invoice_value}\n"
                    break

        all_invoices_ok = True  # Initialize only once at the top

        # Check: Invoices from ENTRY SUMMARY must be in folder
        invoice_folder_invoices = {inv for inv, _ in invoice_fob_list}
        for item in results:
            invoice_no = str(item.get("Invoice Number", "")).strip()
            if invoice_no and invoice_no not in invoice_folder_invoices:
                output += f"📂 Invoice {invoice_no} from ENTRY SUMMARY pdf has no matching file in Invoice Folder.\n"
                all_invoices_ok = False

        # Check: Invoices from folder must be in ENTRY SUMMARY
        entry_summary_invoices = {str(item.get("Invoice Number", "")).strip() for item in results}
        for inv, _ in invoice_fob_list:
            if inv not in entry_summary_invoices:
                output += f"⚠️ Invoice No. {inv} not found in ENTRY SUMMARY.\n"
                all_invoices_ok = False  # <-- Add this line

        # Summary
        if invoice_fob_list or results:
            if all_invoices_ok:
                output += "\nOverall OK ✅\n"
            else:
                output += "\n Overall NOT OK ❌\n"

        return output

    except Exception as e:
        logging.error(f"Error processing {pdf_file}: {str(e)}", exc_info=True)
        return f"❌ Error processing {pdf_file}: {str(e)}"

# GUI
def browse_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        entry_pdf_path.delete(0, tk.END)
        entry_pdf_path.insert(0, file_path)

def browse_invoice_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_invoice_folder.delete(0, tk.END)
        entry_invoice_folder.insert(0, folder_path)

def run_processing():
    pdf_file = entry_pdf_path.get().strip()
    if not pdf_file:
        messagebox.showerror("Error", "Please select a main PDF file.")
        return

    result = process_pdf(pdf_file)
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result)
    output_text.config(state=tk.DISABLED)

# Main GUI Window
root = tk.Tk()
root.title("PDF Invoice Processor")
root.geometry("800x600")

frame_top = tk.Frame(root)
frame_top.pack(pady=10)

# Main PDF selection
tk.Label(frame_top, text="Select Entry PDF File:").pack(side=tk.LEFT, padx=5)
entry_pdf_path = tk.Entry(frame_top, width=60)
entry_pdf_path.pack(side=tk.LEFT, padx=5)
btn_browse_pdf = tk.Button(frame_top, text="Browse", command=browse_pdf)
btn_browse_pdf.pack(side=tk.LEFT, padx=5)

# Invoice folder selection
frame_folder = tk.Frame(root)
frame_folder.pack(pady=10)
tk.Label(frame_folder, text="Select Invoice Folder:").pack(side=tk.LEFT, padx=5)
entry_invoice_folder = tk.Entry(frame_folder, width=60)
entry_invoice_folder.pack(side=tk.LEFT, padx=5)
btn_browse_folder = tk.Button(frame_folder, text="Browse", command=browse_invoice_folder)
btn_browse_folder.pack(side=tk.LEFT, padx=5)

btn_run = tk.Button(root, text="Run Processing", command=run_processing, bg="green", fg="white", width=20)
btn_run.pack(pady=10)

output_text = tk.Text(root, wrap=tk.WORD, height=25, width=100, state=tk.DISABLED)
output_text.pack(padx=10, pady=10)

root.mainloop()