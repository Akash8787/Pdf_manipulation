import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pdfminer.high_level import extract_text
import os
import re
import threading
import json
from flask import Flask, jsonify
from werkzeug.serving import run_simple

class PDFProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Invoice Processor")
        self.root.geometry("720x540")
        self.root.configure(bg="#212121")  # Dark background for modern look

        # Set custom icon
        try:
            icon_path = "D:/PDF_Manuplation/content/SIPL.ico"
            self.root.iconbitmap(icon_path)
        except tk.TclError as e:
            print(f"Error loading icon: {e}. Using default icon.")

        # Initialize Flask app and in-memory data storage
        self.flask_app = Flask(__name__)
        self.processed_data = []
        self.setup_flask_routes()

        # Custom styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=5, font=("Roboto", 9, "bold"))
        style.configure("Process.TButton", background="#42a5f5", foreground="white", borderwidth=0)
        style.map("Process.TButton", background=[("active", "#2196f3")])
        style.configure("Browse.TButton", background="#546e7a", foreground="white", borderwidth=0)
        style.map("Browse.TButton", background=[("active", "#455a64")])
        style.configure("TLabel", font=("Roboto", 9), background="#212121", foreground="#ffffff")
        style.configure("Header.TLabel", font=("Roboto", 16, "bold"), foreground="#ffffff")
        style.configure("Info.TLabel", font=("Roboto", 8, "italic"), foreground="#b0bec5")
        style.configure("TEntry", font=("Roboto", 9), background="#37474f", foreground="#000000")
        style.configure("TFrame", background="#212121")

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with gradient background (simulated with a Canvas)
        self.header_frame = tk.Frame(self.main_frame, height=70)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Create a canvas for the gradient background
        self.header_canvas = tk.Canvas(self.header_frame, height=70, highlightthickness=0)
        self.header_canvas.pack(fill=tk.BOTH, expand=True)

        # Initial gradient draw
        self.create_gradient(self.header_canvas)

        # Title and API labels
        self.title_label = ttk.Label(self.header_frame, text="PDF Invoice Processor", style="Header.TLabel")
        self.title_label.place(relx=0.5, rely=0.3, anchor="center")

        self.api_label = ttk.Label(
            self.header_frame,
            text="Processed data available at: http://127.0.0.1:5000/get",
            style="Info.TLabel"
        )
        self.api_label.place(relx=0.5, rely=0.7, anchor="center")

        # Bind the resize event to redraw the gradient and reposition labels
        self.root.bind("<Configure>", self.on_resize)

        # Content frame with padding
        self.content_frame = ttk.Frame(self.main_frame, padding=5)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection frame (compact)
        self.folder_frame = tk.Frame(self.content_frame, bg="#424242", relief=tk.RAISED, borderwidth=1, pady=5, padx=5)
        self.folder_frame.pack(fill=tk.X, pady=(0, 8))

        self.folder_label = ttk.Label(self.folder_frame, text="📁 Select Folder:", background="#424242")
        self.folder_label.pack(side=tk.LEFT, padx=5)

        self.folder_entry = ttk.Entry(self.folder_frame, width=35, style="TEntry")
        self.folder_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.browse_button = ttk.Button(self.folder_frame, text="Browse", command=self.browse_folder, style="Browse.TButton")
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Process button
        self.process_button = ttk.Button(self.content_frame, text="Process PDFs", command=self.start_processing, style="Process.TButton")
        self.process_button.pack(pady=5)

        # Output area with shadow effect
        self.output_frame = tk.Frame(self.content_frame, bg="#424242", relief=tk.RAISED, borderwidth=2, highlightbackground="#616161", highlightthickness=1)
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        self.output_text = tk.Text(
            self.output_frame, height=10, font=("Roboto", 11), wrap=tk.WORD, bg="#fafafa", bd=0, fg="#000000", spacing1=5, spacing2=2, spacing3=5
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure tags for styling the text
        self.output_text.tag_configure("flask", font=("Roboto", 11, "bold"), foreground="#26a69a")  # Teal for Flask message
        self.output_text.tag_configure("processed", font=("Roboto", 11), foreground="#66bb6a")  # Lime green for processed files
        self.output_text.tag_configure("separator", font=("Roboto", 11, "bold"), foreground="#78909c")  # Gray-blue for separator
        self.output_text.tag_configure("separator_bg", background="#e0e0e0")  # Light gray background for separator
        self.output_text.tag_configure("label", font=("Roboto", 11, "bold"), foreground="#455a64")  # Dark blue-gray for labels
        self.output_text.tag_configure("value", font=("Roboto", 11), foreground="#000000")  # Black for values
        self.output_text.tag_configure("row_even", background="#eceff1")  # Softer light gray for even rows
        self.output_text.tag_configure("row_odd", background="#ffffff")  # White for odd rows

        self.output_scrollbar = ttk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)
        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Start Flask server
        self.start_flask_server()

    def create_gradient(self, canvas):
        """Create a gradient background on the canvas from color1 to color2."""
        canvas.delete("all")
        # Get the current width of the canvas
        width = canvas.winfo_width()
        if width <= 1:  # If the canvas hasn't been rendered yet, use a default width
            width = 720
        height = 70
        color1 = "#37474f"
        color2 = "#263238"
        limit = height
        r1, g1, b1 = canvas.winfo_rgb(color1)
        r2, g2, b2 = canvas.winfo_rgb(color2)
        r_ratio = (r2 - r1) / limit
        g_ratio = (g2 - g1) / limit
        b_ratio = (b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr:04x}{ng:04x}{nb:04x}'
            canvas.create_line(0, i, width, i, fill=color)

    def on_resize(self, event):
        """Handle window resize by redrawing the gradient and repositioning labels."""
        # Redraw the gradient with the new width
        self.create_gradient(self.header_canvas)
        # Ensure labels remain centered
        self.title_label.place(relx=0.5, rely=0.3, anchor="center")
        self.api_label.place(relx=0.5, rely=0.7, anchor="center")

    def setup_flask_routes(self):
        @self.flask_app.route('/get', methods=['GET'])
        def get_invoices():
            if not self.processed_data:
                return jsonify({"error": "No data processed yet"}), 404
            try:
                return jsonify(self.processed_data)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def start_flask_server(self):
        threading.Thread(
            target=lambda: run_simple('0.0.0.0', 5000, self.flask_app, use_reloader=False), daemon=True
        ).start()
        self.root.after(0, lambda: self.output_text.insert(tk.END, "🌐 Flask server started at http://127.0.0.1:5000/get\n\n", "flask"))

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Clear the previous output text
            self.output_text.delete(1.0, tk.END)
            # Insert the Flask server message again since we cleared the text
            self.output_text.insert(tk.END, "🌐 Flask server started at http://127.0.0.1:5000/get\n\n", "flask")
            self.output_text.see(tk.END)
            # Set the new folder path in the entry box
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

    def start_processing(self):
        folder_path = self.folder_entry.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Clear the text area and add the initial message
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "🌐 Flask server started at http://127.0.0.1:5000/get\n\n", "flask")
        self.processed_data = []
        self.process_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")

        threading.Thread(target=self.process_pdfs, args=(folder_path,), daemon=True).start()

    def process_pdfs(self, folder_path):
        def clean_exporter_details(text):
            """Extract exporter details, including Rex No if present, stopping before IEC Code or Invoice No."""
            pattern = r'^(.*?)(?:\nRex No:[^\n]*\n)?(?=\n(?:IEC Code:|Invoice No:|$))'
            match = re.match(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                result = match.group(1).strip()
                rex_no_match = re.search(r'\n(Rex No:[^\n]*)', text, re.MULTILINE)
                if rex_no_match:
                    result += f"\n{rex_no_match.group(1)}"
                return result
            return "Exporter details not found."

        all_json_data = []
        skipped_messages = []  # Will not be displayed
        processed_messages = []
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        for filename in pdf_files:
            pdf_path = os.path.join(folder_path, filename)
            try:
                text = extract_text(pdf_path)
            except Exception as e:
                skipped_messages.append(f"Skipped {filename} due to error: {e}")
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

            # Structure the data for JSON
            data = {
                "pdf_file": filename,
                "Manufacture & Exporter": exporter_details,
                "Invoice No.": invoice_no,
                "FOB Value IN USD": fob_value
            }

            # Check if we should skip this record
            if "not found" in exporter_details:
                skipped_messages.append(f"Skipped {filename} due to missing exporter details.")
            else:
                try:
                    fob_numeric = float(fob_value.replace(',', '').strip())
                    data["FOB Value IN USD"] = fob_numeric
                    all_json_data.append(data)
                    processed_messages.append(f"  ✅ {filename}")
                except ValueError:
                    skipped_messages.append(f"Skipped {filename} due to invalid FOB value: {fob_value}")

        self.processed_data = all_json_data

        # Combine all messages in the desired order for sequential display
        all_messages = processed_messages
        # Add the separator line before the invoice/FOB messages
        all_messages.append("📊 ------ Extracted Data ------ 📊")
        for i, data in enumerate(all_json_data):
            # Format each row with labels and values
            row = [
                ("Invoice No.: ", "label"),
                (f"{data['Invoice No.']},  ", "value"),
                ("FOB Value IN USD: ", "label"),
                (f"{data['FOB Value IN USD']}", "value")
            ]
            all_messages.append((row, "row_even" if i % 2 == 0 else "row_odd"))

        # Display messages one by one with a delay
        def display_messages(index=0):
            if index < len(all_messages):
                message = all_messages[index]
                if isinstance(message, str):
                    # Handle processed files and separator
                    tag = "processed" if message.startswith("  ✅") else ("separator", "separator_bg")
                    self.output_text.insert(tk.END, f"{message}\n", tag)
                else:
                    # Handle extracted data rows
                    row, row_tag = message
                    for text, tag in row:
                        self.output_text.insert(tk.END, text, (tag, row_tag))
                    self.output_text.insert(tk.END, "\n")
                self.output_text.see(tk.END)
                self.root.after(100, lambda: display_messages(index + 1))
            else:
                # After all messages are displayed, update the UI
                self.process_button.configure(state="normal")
                self.browse_button.configure(state="normal")

        # Start displaying messages
        display_messages()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFProcessorApp(root)
    root.mainloop()