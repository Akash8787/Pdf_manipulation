import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import pythoncom
import sys
import time
import json
import requests
import locale
import webbrowser
from tkinter.scrolledtext import ScrolledText
import re
import uuid
locale.setlocale(locale.LC_ALL, '')

# License check function
def Licence():
    error = ""
    message = ""
    url = "http://aisagar.com/DeepBluePDFManipulation"
    payload = json.dumps({"token": "JUYHJ-LKJH12-IKJUYH-45OIUJ"})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        obj = json.loads(response.text)
        if "Error" in obj and "Message" in obj:
            error = obj["Error"]
            message = obj["Message"]
        else:
            error = response.text
    except Exception as e:
        error = f"License check failed: {str(e)}"
    return error, message

# Logging function
def writeLog(text_box, message, tag=None):
    tm = time.strftime('%d-%b-%Y %H:%M:%S')
    if tag:
        text_box.insert(tk.END, f"{tm} - {message}\n", tag)
    else:
        text_box.insert(tk.END, f"{tm} - {message}\n")
    text_box.yview(tk.END)
    text_box.update_idletasks()

# Clean data utility
def clean(var):
    var = var.replace('$', '').replace(',', '').replace('%', '').replace('USD', '')
    try:
        if var not in ['NO', 'N']:
            var = float(var)
    except ValueError:
        pass
    return var

# Clean extracted data
def clean_data(result1):
    result = {}
    try:
        if 'A.' in result1['aa']:
            result1['aa'] = result1['aa'][0: result1['aa'].index("A.")]
            result['MPF'] = float(result1['aa'].split("$")[-1].replace(",", ''))
        else:
            result['MPF'] = float(result1['aa'].split("$")[-1].replace(",", ''))
        if 'A.' in result1['bb']:
            result1['bb'] = result1['bb'][0: result1['bb'].index("A.")]
            result1['bb'] = result1['bb'][result1['bb'].index("$") + 1:]
            result['HMF'] = float(result1['bb'].split("$")[0].replace(",", ''))
            result['Total Entered Value'] = float(result1['bb'].split("$")[-1].replace(",", ''))
        else:
            result1['bb'] = result1['bb'][result1['bb'].index("$") + 1:]
            result['HMF'] = float(result1['bb'].split("$")[0].replace(",", ''))
            result['Total Entered Value'] = float(result1['bb'].split("$")[-1].replace(",", ''))
        result['Duty'] = float(result1['cc'].split('$')[-1].replace(",", ''))
        result['Total Other Fees'] = float(result1['dd'].split("\n")[-1].replace("$", '').replace(",", ''))
        if "I" in result1['ee']:
            result1['ee'] = result1['ee'].split("\n")
            result['Other'] = float(result1['ee'][0].split("$")[-1].replace("\r", '').replace("\n", '').replace(",", ''))
        else:
            result1['ee'] = result1['ee'].split("\n")
            result['Other'] = float(result1['ee'][-1].split("$")[-1].replace("\r", '').replace("\n", '').replace(",", ''))
        result['Total'] = float(result1['ff'].split("$")[-1].replace("\r", '').replace("\n", '').replace(",", ''))
    except Exception as e:
        raise Exception(f"Error while cleaning data: {str(e)}")
    return result

# Clean comm_invoice_fob.txt
def clean_comm_txtfile():
    try:
        unique_lines = set()
        with open('comm_invoice_fob.txt', 'r') as file:
            for line in file:
                unique_lines.add(line.strip())
        with open('comm_invoice_fob.txt', 'w') as file:
            for line in unique_lines:
                file.write(line + '\n')
    except Exception as e:
        raise Exception(f"Error cleaning comm_invoice_fob.txt: {str(e)}")

# Add invoice and FOB values
def Adding_invoice_and_FOB(pdf_folder, text_box, root):
    error, _ = Licence()
    if error:
        messagebox.showerror("Error", error)
        return False

    if not pdf_folder:
        messagebox.showerror("Error", "Please select a PDF folder.")
        return False

    text_box.delete('1.0', tk.END)
    writeLog(text_box, "Scanning PDF folder for invoices...", "info")
    templates = read_templates("Template2")
    with open("comm_invoice_fob.txt", "w") as f:
        f.close()

    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    if not pdf_files:
        writeLog(text_box, "No PDF files found in the selected folder.", "warning")
        return False

    progress_frame = ttk.Frame(root)
    progress_frame.pack(fill='x', pady=5)
    progress_label = ttk.Label(progress_frame, text="Processing PDF files:")
    progress_label.pack(side='left')
    progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', maximum=total_files)
    progress.pack(side='left', expand=True, fill='x', padx=5)

    processed = 0
    for i in pdf_files:
        try:
            result = extract_data(os.path.join(pdf_folder, i), templates=templates)
            if isinstance(result, dict):
                with open("comm_invoice_fob.txt", "a") as file:
                    invoice_number = ''.join([n for n in str(result['invoice_number']).strip() if n.isdigit()])
                    fob_value = str(result['FOB Value IN USD -']).split()[-1].strip().replace(',', '')
                    fob_float = float(fob_value)
                    rounded_fob = round(fob_float)
                    formatted_fob = locale.format_string("%d", rounded_fob, grouping=True)
                    file.write(invoice_number + " " + str(rounded_fob) + "\n")
                    writeLog(text_box, f"Added invoice {invoice_number}, FOB {formatted_fob}", "success")
            processed += 1
            progress['value'] = processed
            root.update_idletasks()
        except Exception as e:
            writeLog(text_box, f"Error processing {i}: {str(e)}", "error")

    clean_comm_txtfile()
    progress_frame.destroy()
    writeLog(text_box, f"Processed {processed} of {total_files} PDF files.", "info")
    return True

# Clean check block
def clean_check_block(raw_text):
    lines = raw_text.splitlines()
    line_number = lines[0].split()[0] if lines else ""
    try:
        start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))
        cleaned_lines = [f" {line_number} " + lines[start_idx]] + lines[start_idx + 1:]
        cleaned_text = "\r\n".join(cleaned_lines)
        removed_lines = lines[:start_idx]
        removed_text = "\r\n".join(removed_lines)
        return cleaned_text, removed_text
    except StopIteration:
        return raw_text, ""

# Handle separated boxes
def handle_sep(result2, stored_latest):
    try:
        if isinstance(result2['separatedboxes'], str):
            all_stored = []
            text = result2['separatedboxes'].split("\n")
            key = int(text[0].split()[0])
            second = text[1][text[1].find('N'):].split()
            second = [clean(x) for x in second]
            all_stored.extend(second[1:])
            forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
            forth = [clean(x) for x in forth]
            all_stored.extend(forth)
            fifth = text[5].replace('501 - Harbor Maintenance Fee', '').split()
            fifth = [clean(x) for x in fifth]
            all_stored.extend(fifth)
            sixth = text[-1].replace('USD', '').split()
            sixth = [clean(x) for x in sixth]
            all_stored.extend(sixth)
            all_stored[7] = int(all_stored[7])
            stored_latest[str(key)] = all_stored
        elif isinstance(result2['separatedboxes'], list):
            for var in result2['separatedboxes']:
                all_stored = []
                text = str(var).split("\n")
                key = int(text[0].split()[0])
                second = text[1][text[1].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[5].replace('501 - Harbor Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                sixth = text[-1].replace('USD', '').split()
                sixth = [clean(x) for x in sixth]
                all_stored.extend(sixth)
                all_stored[7] = int(all_stored[7])
                stored_latest[str(key)] = all_stored
    except KeyError:
        try:
            if isinstance(result2['separatedboxes2'], str):
                all_stored = []
                text = result2['separatedboxes2'].split("\n")
                key = int(text[0].split()[0])
                second = text[0][text[0].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                sixth = text[-1].replace('USD', '').split()
                sixth = [clean(x) for x in sixth]
                all_stored.extend(sixth)
                all_stored[7] = int(all_stored[7])
                stored_latest[str(key)] = all_stored
            elif isinstance(result2['separatedboxes2'], list):
                for var in result2['separatedboxes2']:
                    all_stored = []
                    text = str(var).split("\n")
                    key = int(text[0].split()[0])
                    second = text[0][text[0].find('N'):].split()
                    second = [clean(x) for x in second]
                    all_stored.extend(second[1:])
                    forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                    forth = [clean(x) for x in forth]
                    all_stored.extend(forth)
                    fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                    fifth = [clean(x) for x in fifth]
                    all_stored.extend(fifth)
                    sixth = text[-1].replace('USD', '').split()
                    sixth = [clean(x) for x in sixth]
                    all_stored.extend(sixth)
                    all_stored[7] = int(all_stored[7])
                    stored_latest[str(key)] = all_stored
        except:
            pass

# Handle full invoices
def full_invoice(result2, stored_latest):
    try:
        if isinstance(result2['check'], list):
            for var in result2['check']:
                all_stored = []
                text = str(var).split("\n")
                key = int(text[0].split()[0])
                second = text[1][text[1].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[5].replace('501 - Harbor Maintenance Fee on Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                sixth = text[-1].replace('USD', '').split()
                sixth = [clean(x) for x in sixth]
                all_stored.extend(sixth)
                all_stored[7] = int(all_stored[7])
                all = [x for x in all_stored if x != '']
                stored_latest[str(key)] = all
        elif isinstance(result2['check'], str):
            all_stored = []
            text = result2['check'].split("\n")
            key = int(text[0].split()[0])
            second = text[1][text[1].find('N`N'):].split()
            second = [clean(x) for x in second]
            all_stored.extend(second[1:])
            forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
            forth = [clean(x) for x in forth]
            all_stored.extend(forth)
            fifth = text[5].replace('501 - Harbor Maintenance Fee', '').split()
            fifth = [clean(x) for x in fifth]
            all_stored.extend(fifth)
            sixth = text[-1].replace('USD', '').split()
            sixth = [clean(x) for x in sixth]
            all_stored.extend(sixth)
            all_stored[7] = int(all_stored[7])
            all = [x for x in all_stored if x != '']
            stored_latest[str(key)] = all
    except KeyError:
        try:
            if isinstance(result2['check2'], list):
                for var in result2['check2']:
                    all_stored = []
                    text = str(var).split("\n")
                    key = int(text[0].split()[0])
                    second = text[0][text[0].find('N'):].split()
                    second = [clean(x) for x in second]
                    all_stored.extend(second[1:])
                    forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                    forth = [clean(x) for x in forth]
                    all_stored.extend(forth)
                    fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                    fifth = [clean(x) for x in fifth]
                    all_stored.extend(fifth)
                    sixth = text[-1].replace('USD', '').split()
                    sixth = [clean(x) for x in sixth]
                    all_stored.extend(sixth)
                    all_stored_copy = [x for x in all_stored if x != '']
                    all_stored_copy[7] = int(all_stored_copy[7])
                    stored_latest[str(key)] = all_stored_copy
            elif isinstance(result2['check2'], str):
                all_stored = []
                text = result2['check2'].split("\n")
                key = int(text[0].split()[0])
                second = text[0][text[0].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                sixth = text[-1].replace('USD', '').split()
                sixth = [clean(x) for x in sixth]
                all_stored.extend(sixth)
                all_stored_copy = [x for x in all_stored if x != '']
                all_stored_copy[7] = int(all_stored_copy[7])
                stored_latest[str(key)] = all_stored_copy
        except:
            pass

# Handle missing boxes
def missing(result2, checking_stored):
    try:
        if isinstance(result2['missingboxes'], list):
            for var in result2['missingboxes']:
                all_stored = []
                text = str(var).split("\n")
                key = int(text[0].split()[0])
                second = text[1][text[1].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[5].replace('501 - Harbor Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                all = [x for x in all_stored if x != '']
                checking_stored[str(key)] = all
        elif isinstance(result2['missingboxes'], str):
            all_stored = []
            text = result2['missingboxes'].split("\n")
            key = int(text[0].split()[0])
            second = text[1][text[1].find('N'):].split()
            second = [clean(x) for x in second]
            all_stored.extend(second[1:])
            forth = text[4].replace('499 - Merchandise Processing Fee', '').split()
            forth = [clean(x) for x in forth]
            all_stored.extend(forth)
            fifth = text[5].replace('501 - Harbor Maintenance Fee', '').split()
            fifth = [clean(x) for x in fifth]
            all_stored.extend(fifth)
            all = [x for x in all_stored if x != '']
            checking_stored[str(key)] = all
    except KeyError:
        try:
            if isinstance(result2['missingboxes2'], list):
                for var in result2['missingboxes2']:
                    all_stored = []
                    text = str(var).split("\n")
                    key = int(text[0].split()[0])
                    second = text[0][text[1].find('N'):].split()
                    second = [clean(x) for x in second]
                    all_stored.extend(second[1:])
                    forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                    forth = [clean(x) for x in forth]
                    all_stored.extend(forth)
                    fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                    fifth = [clean(x) for x in fifth]
                    all_stored.extend(fifth)
                    all = [x for x in all_stored if x != '']
                    checking_stored[str(key)] = all
            elif isinstance(result2['missingboxes2'], str):
                all_stored = []
                text = str(var).split("\n")
                key = int(text[0].split()[0])
                second = text[0][text[0].find('N'):].split()
                second = [clean(x) for x in second]
                all_stored.extend(second[1:])
                forth = text[3].replace('499 - Merchandise Processing Fee', '').split()
                forth = [clean(x) for x in forth]
                all_stored.extend(forth)
                fifth = text[4].replace('501 - Harbor Maintenance Fee', '').split()
                fifth = [clean(x) for x in fifth]
                all_stored.extend(fifth)
                all = [x for x in all_stored if x != '']
                checking_stored[str(key)] = all
        except:
            pass

# Main validation function
def validate_invoices(console_file, pdf_folder, text_box, root, message):
    error, _ = Licence()
    if error:
        messagebox.showerror("Error", error)
        return

    if not console_file or not pdf_folder:
        messagebox.showerror("Error", "Please select both console file and PDF folder.")
        return

    if os.path.exists("reasons.txt"):
        os.remove("reasons.txt")

    stored_latest = {}
    checking_stored = {}
    paired_stored = {}
    problem_count = 0

    pythoncom.CoInitialize()
    sys.stderr = open("consoleoutput.log", "w")
    templates = read_templates("Template/")
    temp1 = read_templates("Template3/")

    try:
        result1 = extract_data(console_file, templates=templates)
        result = clean_data(result1)
        result2 = extract_data(console_file, templates=temp1)
        
        removed_texts = []
        invoice_dollar_values = {}  # Dictionary to store dollar values by invoice number
        if result2 and 'check2' in result2:
            cleaned_checks = []
            for block in result2['check2']:
                cleaned_block, removed_block = clean_check_block(block)
                cleaned_checks.append(cleaned_block)
                removed_texts.append(removed_block)
                # Extract invoice number from the block
                text = str(block).split("\n")
                key = text[0].split()[0]  # Invoice number
                # Extract dollar values from the removed_block
                dollar_matches = re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', removed_block)
                dollar_values = [float(match.replace(",", "").replace("$", "")) for match in dollar_matches]
                invoice_dollar_values[key] = dollar_values
            result2['check2'] = cleaned_checks
            result2['removed_texts'] = removed_texts
        # Sort dollar values by invoice number
        sorted_invoice_dollar_values = dict(sorted(invoice_dollar_values.items(), key=lambda x: int(x[0])))
        # Flatten dollar values in sorted invoice order
        sequential_dollar_values = []
        for invoice_num in sorted_invoice_dollar_values:
            sequential_dollar_values.extend(sorted_invoice_dollar_values[invoice_num])
        writeLog(text_box, f"Flattened Dollar Values in Sorted Invoice Order: {sequential_dollar_values}", "info")
    except Exception as e:
        writeLog(text_box, f"Error extracting data: {str(e)}", "error")
        return

    try:
        handle_sep(result2, stored_latest)
        full_invoice(result2, stored_latest)
        missing(result2, checking_stored)

        for key, value in checking_stored.items():
            if key not in stored_latest:
                stored_latest[key] = value

        stored_latest = dict(sorted(stored_latest.items(), key=lambda x: int(x[0])))
        stored_latest = {k: [0.0 if x == 'FREE' else x for x in v if x != ''] for k, v in stored_latest.items()}

        list_which_arepaired = []
        pair = 1
        for key, value in stored_latest.items():
            if len(value) == 7:
                dict_value = {key: value, str(int(key) + 1): stored_latest[str(int(key) + 1)]}
                list_which_arepaired.append(str(stored_latest[str(int(key) + 1)][7]))
                paired_stored[str(pair)] = dict_value
                pair += 1

        paired_stored = dict(sorted(paired_stored.items(), key=lambda x: int(x[0])))
    except Exception as e:
        writeLog(text_box, f"Error processing invoices: {str(e)}", "error")
        return

    try:
        stored_info_txt = {}
        if os.path.exists("comm_invoice_fob.txt"):
            with open("comm_invoice_fob.txt", "r") as file:
                for value in file:
                    content = value.split()
                    stored_info_txt[content[0]] = float(content[1].replace("\n", "").replace("\r", "").replace(',', ''))
        else:
            writeLog(text_box, "Invoice numbers and FOB values are null", "warning")
    except Exception as e:
        writeLog(text_box, f"Error reading comm_invoice_fob.txt: {str(e)}", "error")
        return

    stored = {str(value[7]): value for key, value in stored_latest.items() if len(value) > 7}
    list_comm_invoice = list(stored_info_txt.keys())
    available_invoices = [key for key in stored if key in list_comm_invoice]
    not_available_invoices = [key for key in stored if key not in list_comm_invoice]

    # Initialize totals
    MPF_total = 0.0
    HMF_total = 0.0
    Total_Entered_Value = 0.0
    Total_Duty = 0.0
    Total_FOB = 0.0

    # Lists for visible values
    mpf_list = []
    hmf_list = []
    duty_list = []  # Stores numerical duty values for summation
    duty_display = []  # Stores display strings for duty column

    # Create Treeview
    tree_frame = ttk.Frame(root)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
    
    tree = ttk.Treeview(tree_frame, columns=('Status', 'Entered Value', 'FOB Value', 'MPF', 'HMF', 'Duty'), show='headings')
    tree.heading('Status', text='Status')
    tree.heading('Entered Value', text='Entered Value')
    tree.heading('FOB Value', text='FOB Value')
    tree.heading('MPF', text='MPF')
    tree.heading('HMF', text='HMF')
    tree.heading('Duty', text='Duty')
    tree.column('Status', width=100, anchor='center')
    tree.column('Entered Value', width=120, anchor='center')
    tree.column('FOB Value', width=120, anchor='center')
    tree.column('MPF', width=100, anchor='center')
    tree.column('HMF', width=100, anchor='center')
    tree.column('Duty', width=150, anchor='center')
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # Counter for sequential dollar values
    dollar_index = 0

    with open("reasons.txt", 'w') as file:
        # Handle not available invoices
        for current in not_available_invoices:
            fob_value = stored_info_txt.get(current, 0.0)
            Total_FOB += fob_value
            tree.insert('', 'end', values=(
                f"{current} Not Available",
                "N/A",
                locale.format_string('%d', round(fob_value), grouping=True),
                "N/A",
                "N/A",
                "N/A"
            ), tags=('error',))
            problem_count += 1
            file.write(f"{int(current)} this invoice not available in your PDF FOLDER\n")

        # Handle available invoices
        for value in available_invoices:
            try:
                FOB = int(float(stored_info_txt[value]))
                Total_FOB += FOB
                if value not in list_which_arepaired:
                    list_value = stored[value]
                    if len(list_value) in [11, 12]:
                        last_entered_value = list_value[-1]
                        mpfcal = list_value[4]
                        hmfcal = list_value[6]
                        ratecal = list_value[2]
                        
                        MPF_total += mpfcal
                        HMF_total += hmfcal
                        Total_Entered_Value += last_entered_value

                        if mpfcal != "N/A":
                            mpf_list.append(mpfcal)
                        if hmfcal != "N/A":
                            hmf_list.append(hmfcal)
                        # Handle duty display and calculation
                        duty_value = ratecal
                        duty_display_str = ""
                        if dollar_index < len(sequential_dollar_values):
                            extra_duty = sequential_dollar_values[dollar_index]
                            duty_display_str = f"{locale.format_string('%.2f', extra_duty, grouping=True)} + {locale.format_string('%.2f', ratecal, grouping=True)}"
                            duty_value += extra_duty
                            dollar_index += 1
                        else:
                            duty_display_str = f"{locale.format_string('%.2f', ratecal, grouping=True)}"
                        duty_list.append(duty_value)
                        duty_display.append(duty_display_str)

                        issue = False
                        forprint = [value, []]
                        if int(last_entered_value) != FOB and int(last_entered_value) != FOB + 1:
                            issue = True
                            forprint[1].append('Entered Value not matched')
                        if len(list_value) == 12 and int(list_value[-4] + list_value[-3]) != int(last_entered_value):
                            issue = True
                            forprint[1].append(f"After MMV applied {list_value[-4]} with {list_value[-3]} the entered value is not matched {int(last_entered_value)}")
                        if int(list_value[0]) != int(last_entered_value):
                            issue = True
                            forprint[1].append('Entered Value not matched which is at 32 A.Entered Value')
                        
                        pythonratecal = float(list_value[0] * list_value[1] / 100)
                        pythonmpfcal = float(list_value[0] * list_value[3] / 100)
                        pythonhmfcal = float(list_value[0] * list_value[5] / 100)

                        if int(pythonratecal) != int(ratecal) and int(pythonratecal) + 1 != int(ratecal):
                            issue = True
                            forprint[1].append(f'This calculated value {ratecal} not matched with Invoice value {list_value[0]} % rate {list_value[1]}')
                        if int(pythonmpfcal) != int(mpfcal) and int(pythonmpfcal) + 1 != int(mpfcal):
                            issue = True
                            forprint[1].append(f'This calculated value {mpfcal} not matched with Invoice value {list_value[0]} % rate {list_value[3]}')
                        if int(pythonhmfcal) != int(hmfcal) and int(pythonhmfcal) + 1 != int(hmfcal):
                            issue = True
                            forprint[1].append(f'This calculated value {hmfcal} not matched with Invoice value {list_value[0]} % rate {list_value[5]}')

                        status = "OK" if not issue else "NOT OK"
                        tag = 'ok' if not issue else 'error'
                        
                        tree.insert('', 'end', values=(
                            f"{value} {status}",
                            locale.format_string('%d', round(last_entered_value), grouping=True),
                            locale.format_string('%d', round(FOB), grouping=True),
                            locale.format_string('%.2f', mpfcal, grouping=True),
                            locale.format_string('%.2f', hmfcal, grouping=True),
                            duty_display_str
                        ), tags=(tag,))
                        
                        if issue:
                            problem_count += 1
                            for j in forprint[1]:
                                file.write(f"{forprint[0]}: {j}\n")
                                problem_count += 1
            except Exception as e:
                writeLog(text_box, f"Error in invoice validation: {str(e)}", "error")

        # Handle paired invoices
        for key, value in paired_stored.items():
            try:
                dict1 = value
                first_part = []
                second_part = []
                for k, v in dict1.items():
                    if not first_part:
                        first_part.extend(v)
                    else:
                        second_part.extend(v)
                
                mpfcal_total = first_part[4] + second_part[4]
                hmfcal_total = first_part[6] + second_part[6]
                ratecal_total = first_part[2] + second_part[2]
                last_entered_value = second_part[-1]
                FOB = int(float(stored_info_txt[str(second_part[7])]))
                Total_FOB += FOB

                MPF_total += mpfcal_total
                HMF_total += hmfcal_total
                Total_Entered_Value += last_entered_value

                if mpfcal_total != "N/A":
                    mpf_list.append(mpfcal_total)
                if hmfcal_total != "N/A":
                    hmf_list.append(hmfcal_total)
                # Handle duty display and calculation for paired invoices
                duty_value = ratecal_total
                duty_display_str = ""
                if dollar_index < len(sequential_dollar_values):
                    extra_duty = sequential_dollar_values[dollar_index]
                    duty_display_str = f"{locale.format_string('%.2f', extra_duty, grouping=True)} + {locale.format_string('%.2f', ratecal_total, grouping=True)}"
                    duty_value += extra_duty
                    dollar_index += 1
                else:
                    duty_display_str = f"{locale.format_string('%.2f', ratecal_total, grouping=True)}"
                duty_list.append(duty_value)
                duty_display.append(duty_display_str)

                issue = False
                forprint = [str(second_part[7]), []]
                if int(last_entered_value) != FOB and int(last_entered_value) != FOB + 1:
                    issue = True
                    forprint[1].append('Entered Value not matched')
                if len(second_part) == 12 and int(second_part[-4] + second_part[-3]) != int(last_entered_value):
                    issue = True
                    forprint[1].append(f"After MMV applied {second_part[-4]} with {second_part[-3]} the entered value is not matched {int(last_entered_value)}")
                if int(first_part[0] + second_part[0]) != int(last_entered_value):
                    issue = True
                    forprint[1].append(f'Sum of {first_part[0]} and {second_part[0]} is not matched with entered value {last_entered_value}')

                status = "OK" if not issue else "NOT OK"
                tag = 'ok' if not issue else 'error'
                
                tree.insert('', 'end', values=(
                    f"{str(second_part[7])} {status}",
                    locale.format_string('%d', round(last_entered_value), grouping=True),
                    locale.format_string('%d', round(FOB), grouping=True),
                    locale.format_string('%.2f', mpfcal_total, grouping=True),
                    locale.format_string('%.2f', hmfcal_total, grouping=True),
                    duty_display_str
                ), tags=(tag,))
                
                if issue:
                    problem_count += 1
                    for j in forprint[1]:
                        file.write(f"{str(second_part[7])}: {j}\n")
                        problem_count += 1
            except Exception as e:
                writeLog(text_box, f"Error in paired invoice validation: {str(e)}", "error")

        # Calculate displayed totals
        displayed_MPF = sum(mpf_list) if mpf_list else 0.0
        displayed_HMF = sum(hmf_list) if hmf_list else 0.0
        displayed_Duty = sum(duty_list) if duty_list else 0.0

        # Insert totals (original values from PDF)
        tree.insert('', 'end', values=(
            "Totals (PDF)",
            locale.format_string('%.2f', result['Total Entered Value'], grouping=True),
            locale.format_string('%.2f', Total_FOB, grouping=True),
            locale.format_string('%.2f', result['MPF'], grouping=True),
            locale.format_string('%.2f', result['HMF'], grouping=True),
            locale.format_string('%.2f', result['Duty'], grouping=True)
        ), tags=('total',))

        # Insert sum of displayed values
        tree.insert('', 'end', values=(
            "Sum of Displayed",
            locale.format_string('%.2f', Total_Entered_Value, grouping=True),
            locale.format_string('%.2f', Total_FOB, grouping=True),
            locale.format_string('%.2f', displayed_MPF, grouping=True),
            locale.format_string('%.2f', displayed_HMF, grouping=True),
            locale.format_string('%.2f', displayed_Duty, grouping=True)
        ), tags=('additional',))

        # Validate totals
        try:
            pdf_total_MPF = int(result['MPF'])
            if MPF_total < 31.67:
                MPF_total = 31.67
            if int(displayed_MPF) != int(MPF_total):
                writeLog(text_box, f"Displayed MPF total ({displayed_MPF:.2f}) does not match PDF MPF total ({MPF_total:.2f})", "error")
                problem_count += 1
                file.write(f"Displayed MPF total ({displayed_MPF:.2f}) does not match PDF MPF total ({MPF_total:.2f})\n")
            if int(displayed_HMF) != int(HMF_total):
                writeLog(text_box, f"Displayed HMF total ({displayed_HMF:.2f}) does not match PDF HMF total ({HMF_total:.2f})", "error")
                problem_count += 1
                file.write(f"Displayed HMF total ({displayed_HMF:.2f}) does not match PDF HMF total ({HMF_total:.2f})\n")
            Total_Duty = displayed_Duty
            if int(Total_Duty) != int(result['Duty']):
                writeLog(text_box, f"Duty not matched: PDF={locale.format_string('%.2f', result['Duty'], grouping=True)}, Calculated={locale.format_string('%.2f', Total_Duty, grouping=True)}", "error")
                problem_count += 1
                file.write(f"Duty not matched: PDF={locale.format_string('%.2f', result['Duty'], grouping=True)}, Calculated={locale.format_string('%.2f', Total_Duty, grouping=True)}\n")
            if int(result['HMF']) != int(HMF_total):
                writeLog(text_box, f"Total HMF not matched", "error")
                problem_count += 1
                file.write(f"Total HMF not matched\n")
            if int(result['Total Entered Value']) != int(Total_Entered_Value):
                writeLog(text_box, f"Total Entered Value not matched", "error")
                problem_count += 1
                file.write(f"Total Entered Value not matched\n")
            if int(MPF_total + HMF_total) != int(result['Total Other Fees']):
                writeLog(text_box, f"Total Other Fees not matched", "error")
                problem_count += 1
                file.write(f"Total Other Fees not matched\n")
            if int(MPF_total + HMF_total) != int(result['Other']):
                writeLog(text_box, f"Other not matched", "error")
                problem_count += 1
                file.write(f"Other not matched\n")
            if int(Total_Duty + MPF_total + HMF_total) != int(result['Total']):
                writeLog(text_box, f"Total not matched", "error")
                problem_count += 1
                file.write(f"Last Total not matched\n")
        except Exception as e:
            writeLog(text_box, f"Error in totals validation: {str(e)}", "error")

        # Configure Treeview tags
        tree.tag_configure('ok', background='#e8f5e9')
        tree.tag_configure('error', background='#ffebee')
        tree.tag_configure('total', background='#bbdefb')
        tree.tag_configure('additional', background='#b3e5fc')

        # Final status
        if problem_count == 0:
            writeLog(text_box, "Overall Status: OK", "success")
        else:
            writeLog(text_box, f"Overall Status: NOT OK ({problem_count} issues found)", "error")
            
            def download_file():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="Save Validation Report"
                )
                if file_path:
                    with open("reasons.txt", "r") as source_file:
                        with open(file_path, "w") as target_file:
                            target_file.write(source_file.read())
                    messagebox.showinfo("Success", f"Report saved successfully to:\n{file_path}")
            
            download_btn = ttk.Button(
                root,
                text="Download Validation Report",
                command=download_file,
                style='Accent.TButton'
            )
            download_btn.pack

# Main GUI
def main():
    root = tk.Tk()
    root.title("SIPL Invoice Validation System")
    root.geometry('900x700')
    
    try:
        root.iconbitmap("content/SIPL.ico")
    except:
        pass

    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('.', background='#f5f5f5')
    style.configure('TFrame', background='#f5f5f5')
    style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 9))
    style.configure('TButton', font=('Segoe UI', 9), padding=5)
    style.configure('Accent.TButton', background='#4CAF50', foreground='white')
    style.map('Accent.TButton',
              background=[('active', '#45a049'), ('pressed', '#388e3c')])
    
    error, message = Licence()
    if error:
        messagebox.showerror("License Error", error)
        root.destroy()
        return
    
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill='x', pady=(0, 10))
    
    ttk.Label(
        header_frame,
        text="SIPL Invoice Validation System",
        font=('Segoe UI', 14, 'bold')
    ).pack(side='left')
    
    license_frame = ttk.Frame(header_frame)
    license_frame.pack(side='right', padx=10)
    
    ttk.Label(
        license_frame,
        text="License:",
        font=('Segoe UI', 9)
    ).pack(side='left')
    
    ttk.Label(
        license_frame,
        text=message,
        foreground='red',
        font=('Segoe UI', 9, 'bold')
    ).pack(side='left')
    
    input_frame = ttk.LabelFrame(main_frame, text="Invoice Validation", padding=10)
    input_frame.pack(fill='x', pady=5)
    
    console_file = [""]
    console_frame = ttk.Frame(input_frame)
    console_frame.pack(fill='x', pady=5)
    
    ttk.Label(console_frame, text="Console File:").pack(side='left', padx=(0, 5))
    
    console_entry = ttk.Entry(console_frame, width=60)
    console_entry.pack(side='left', expand=True, fill='x')
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select Console File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if filename:
            console_entry.delete(0, tk.END)
            console_entry.insert(0, filename)
            console_file[0] = filename
    
    ttk.Button(
        console_frame,
        text="Browse",
        command=browse_file
    ).pack(side='left', padx=(5, 0))
    
    pdf_folder = [""]
    pdf_frame = ttk.Frame(input_frame)
    pdf_frame.pack(fill='x', pady=5)
    
    ttk.Label(pdf_frame, text="PDF Folder:").pack(side='left', padx=(0, 5))
    
    pdf_entry = ttk.Entry(pdf_frame, width=60)
    pdf_entry.pack(side='left', expand=True, fill='x')
    
    def browse_pdf_folder():
        foldername = filedialog.askdirectory(title="Select PDF Folder")
        if foldername:
            pdf_entry.delete(0, tk.END)
            pdf_entry.insert(0, foldername)
            pdf_folder[0] = foldername
            # Remove existing Treeview and Download button
            for widget in main_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget not in [input_frame, header_frame, output_frame]:
                    widget.destroy()
                elif isinstance(widget, ttk.Button) and widget['text'] == "Download Validation Report":
                    widget.destroy()
            Adding_invoice_and_FOB(pdf_folder[0], text_box, main_frame)
    
    ttk.Button(
        pdf_frame,
        text="Browse",
        command=browse_pdf_folder
    ).pack(side='left', padx=(5, 0))
    
    output_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding=10)
    output_frame.pack(fill='both', expand=True, pady=5)
    
    text_box = ScrolledText(
        output_frame,
        height=10,
        font=('Consolas', 9),
        wrap=tk.WORD
    )
    text_box.pack(fill='both', expand=True)
    
    text_box.tag_config('info', foreground='blue')
    text_box.tag_config('success', foreground='green')
    text_box.tag_config('warning', foreground='orange')
    text_box.tag_config('error', foreground='red')
    
    def start_validate():
        for widget in main_frame.winfo_children():
            if isinstance(widget, ttk.Treeview) or (isinstance(widget, ttk.Frame) and widget not in [input_frame, header_frame, output_frame]):
                widget.destroy()
        validate_invoices(console_file[0], pdf_folder[0], text_box, main_frame, message)
    
    ttk.Button(
        input_frame,
        text="Start Validation",
        command=start_validate,
        style='Accent.TButton'
    ).pack(pady=10)
    
    footer_frame = ttk.Frame(main_frame)
    footer_frame.pack(fill='x', pady=(5, 0))
    
    def open_website(event):
        webbrowser.open("http://sagarinfotech.com")
    
    ttk.Label(
        footer_frame,
        text="Developed By: ",
        font=('Segoe UI', 9)
    ).pack(side='left')
    
    website_link = ttk.Label(
        footer_frame,
        text="SagarInfotech.com",
        font=('Segoe UI', 9, 'underline'),
        foreground='blue',
        cursor='hand2'
    )
    website_link.pack(side='left')
    website_link.bind('<Button-1>', open_website)

    root.mainloop()

if __name__ == "__main__":
    if os.path.exists("comm_invoice_fob.txt"):
        os.remove("comm_invoice_fob.txt")
    main()