import google.generativeai as genai
import pdfplumber
import json
import os

# --- API Key Setup ---
API_KEY = "AIzaSyBF8OeewqPzjtl8KwD5h_-KMWoyhF0sZT8"  # Replace with your actual API key

if not API_KEY:
    raise ValueError("API_KEY is not set. Please provide a valid API key.")

genai.configure(api_key=API_KEY)

# Use a valid model name
model = genai.GenerativeModel('gemini-2.0-flash')  # Adjust if needed

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pdfplumber for better table handling.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"  # Add newline to separate pages
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None
    return text

# --- PDF File Path ---
pdf_file_path = r"D:\latest_Error\67therror\ClientCreditNote_EKH-1009235-4.pdf"  # Specify your PDF path

# 1. Extract text from the PDF
document_content = extract_text_from_pdf(pdf_file_path)

if document_content:
    # 2. Construct the generalized prompt
    prompt_text = f"""
    Analyze the following document text, which is a U.S. Customs and Border Protection Entry Summary (CBP Form 7501). The document contains multiple line items, each starting with a three-digit line number (e.g., '001', '002') and continuing until the next line number or a 'Totals for Invoice' section.

    For each line item (from 001 to the last), extract the following fields from within its section:
    - **Line Number**: The three-digit number at the start of the section (e.g., '001', '002').
    - **A. ENTERED VALUE**: The numerical value immediately following '32. A. Entered Value' in the line item’s section. If '32. A. Entered Value' is not present or no value is specified, use 'N/A'.
    - Duty and IR Tax (if there are two values provided under 'Duty and IR Tax Dollars Cents', please list them separately as 'Duty' and 'IR Tax'. For example, if the document shows '$248.30' and '$62.08', extract 'Duty: $248.30' and 'IR Tax: $62.08'. If only one value is clearly Duty, extract that as 'Duty' and note 'IR Tax: N/A' or '$0'.)
    - **MPF**: The value associated with '499 - Merchandise Processing Fee'. If not present, use 'N/A'.
    - **HMF**: The value associated with '501 - Harbor Maintenance Fee'. If not present, use 'N/A'.
    - **Totals for Invoice**: The invoice number following 'Totals for Invoice' (e.g., '2423200699'). If not present, use 'N/A'.
    - **Invoice Value**: The value following 'Invoice Value' in the invoice totals section (e.g., '$7,398.00 USD'). If not present, use 'N/A'.
    - **Entered Value**: The value following 'Entered Value' in the invoice totals section (e.g., '$7,398.00 USD'). If not present, use 'N/A'.

    **Important Instructions**:
    - Extract 'A. ENTERED VALUE' **only** from column 32 within each line item’s section, immediately following '32. A. Entered Value'.
    - Do **not** use 'Entered Value' from the 'Totals for Invoice' section for the 'A. ENTERED VALUE' field.
    - If a line item lacks a specified 'A. ENTERED VALUE' (e.g., no value under '32. A. Entered Value'), use 'N/A'.
    - Ensure all line items from 001 to the last (e.g., 023) are included, even if some fields are missing.
    - Format all monetary values with a dollar sign and two decimal places (e.g., '$1234.56'). Remove commas from large numbers (e.g., '$1234.56' instead of '$1,234.56').
    - Process all available line items in the document.
    - For 'Invoice Value' and 'Entered Value', include the full value as it appears (e.g., '$7,398.00'), but ensure no commas in the output (e.g., '$7398.00').

    Present the extracted data in a markdown table with the headers:
    | Line Number | Duty | IR Tax | MPF | HMF | A. ENTERED VALUE | Totals for Invoice | Invoice Value | Entered Value |

    Additionally, provide the extracted data in a JSON format with the following structure for each line item:
    [
        {{
            "Line": "<Line Number>",
            "Extracted Value": "<A. ENTERED VALUE>",
            "Duty1": "<Duty>",
            "Duty2": "<IR Tax>",
            "MPF": "<MPF>",
            "HMF": "<HMF>",
            "Invoice Number": "<Totals for Invoice>",
            "Invoice Value": "<Invoice Value>",
            "Entered Value": "<Entered Value>",
            "Source File": "<PDF file name>"
        }},
        ...
    ]

    Document:
    --- START DOCUMENT ---
    {document_content}
    --- END DOCUMENT ---
    """

    # 3. Send the prompt to the Gemini API and process the response
    try:
        response = model.generate_content(prompt_text)
        print(f"\nOutput for {pdf_file_path}:\n")
        print(response.text)

        # Extract JSON data from the response (assuming Gemini includes JSON in the response)
        # Since Gemini may return the JSON as part of the text, we need to parse it
        response_text = response.text
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            json_str = response_text[json_start:json_end]
            try:
                json_data = json.loads(json_str)
                # Update the JSON field values as per the request
                for item in json_data:
                    item["Extracted Value"] = item.get("Extracted Value", "N/A")  # Keep A. ENTERED VALUE
                    item["Duty1"] = item.get("Duty1", "N/A")  # Keep Duty
                    item["Duty2"] = item.get("Duty2", "N/A")  # Keep IR Tax
                    item["Source File"] = os.path.basename(pdf_file_path)
                # Print the JSON data
                print("\nJSON Output:\n")
                print(json.dumps(json_data, indent=4))
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from response: {e}")
        else:
            print("No JSON data found in the response.")
    except Exception as api_e:
        print(f"Error communicating with Gemini API: {api_e}")
else:
    print(f"Could not extract text from {pdf_file_path}. Please check the PDF file integrity.")