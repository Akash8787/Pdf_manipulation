# from invoice2data import extract_data
# from invoice2data.extract.loader import read_templates
# import re
# def clean_check_block(raw_text):
#     """Clean a single check block text to start from HS Code line and return removed portion."""
#     lines = raw_text.splitlines()
#     line_number = lines[0].split()[0] if lines else ""

#     try:
#         # Find HS code line
#         start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))

#         # Cleaned block starts from HS code
#         cleaned_lines = [f" {line_number} " + lines[start_idx]] + lines[start_idx + 1:]
#         cleaned_text = "\r\n".join(cleaned_lines)

#         # Removed block is everything before HS code
#         removed_lines = lines[:start_idx]
#         removed_text = "\r\n".join(removed_lines)

#         return cleaned_text, removed_text
#     except StopIteration:
#         return raw_text, ""  # Return original block, no removed section

# # Load templates
# temp1 = read_templates('Template3/')
# browse_file_var=r"D:\Python\Pdf_Manipulation\input_folder\EKH-1007199-6-7501.pdf"
# try:
    
#     result2 = extract_data(browse_file_var, templates=temp1)
#     print("Original Result2:", result2)

#     removed_texts = []  # To hold removed content

#     if result2 and 'check2' in result2:
#         cleaned_checks = []
#         for block in result2['check2']:
#             cleaned_block, removed_block = clean_check_block(block)
#             cleaned_checks.append(cleaned_block)
#             removed_texts.append(removed_block)  # Store removed part

#         result2['check2'] = cleaned_checks
#         result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference

#     print("\nCleaned Result2:", result2)


#     # dollar_lines = []

#     # Extract only the dollar amounts like $356.90, remove the '$', and convert to float
#     dollar_values = [
#         float(match.replace(",", "").replace("$", ""))
#         for text in removed_texts
#         for match in re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', text)
#     ]

#     print("Extracted Dollar Values:", dollar_values)
# except Exception as e:
#     print('Error while fetching all invoices details: ' + str(e))






# from invoice2data import extract_data
# from invoice2data.extract.loader import read_templates
# import re

# def clean_check_block(raw_text):
#     """Clean a single check block text to start from HS Code line and return removed portion."""
#     lines = raw_text.splitlines()
#     line_number = lines[0].split()[0] if lines else ""

#     try:
#         # Find HS code line
#         start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))

#         # Cleaned block starts from HS code
#         cleaned_lines = [f" {line_number} " + lines[start_idx]] + lines[start_idx + 1:]
#         cleaned_text = "\r\n".join(cleaned_lines)

#         # Removed block is everything before HS code
#         removed_lines = lines[:start_idx]
#         removed_text = "\r\n".join(removed_lines)

#         return cleaned_text, removed_text
#     except StopIteration:
#         return raw_text, ""  # Return original block, no removed section

# # Load templates
# temp1 = read_templates('Template3/')
# browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\EKH-1007199-6-7501.pdf"

# try:
#     result2 = extract_data(browse_file_var, templates=temp1)
#     print("Original Result2:", result2)

#     removed_texts = []  # To hold removed content

#     if result2 and 'check2' in result2:
#         cleaned_checks = []
#         # Check if check2 is a string or a list
#         check2_data = result2['check2']
#         if isinstance(check2_data, str):
#             # Treat as a single block
#             cleaned_block, removed_block = clean_check_block(check2_data)
#             cleaned_checks.append(cleaned_block)
#             removed_texts.append(removed_block)
#         elif isinstance(check2_data, list):
#             # Process each block in the list
#             for block in check2_data:
#                 cleaned_block, removed_block = clean_check_block(block)
#                 cleaned_checks.append(cleaned_block)
#                 removed_texts.append(removed_block)
#         else:
#             raise ValueError("Unexpected type for check2: {}".format(type(check2_data)))

#         result2['check2'] = cleaned_checks
#         result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference

#     print("\nCleaned Result2:", result2)

#     # Extract dollar amounts like $356.90, remove '$' and ',', and convert to float
#     dollar_values = [
#         float(match.replace(",", "").replace("$", ""))
#         for text in removed_texts
#         for match in re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', text)
#     ]

#     print("Extracted Dollar Values:", dollar_values)

# except Exception as e:
#     print('Error while fetching all invoices details: ' + str(e))




from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import re

def clean_check_block(raw_text):
    """Clean a single check block text to start from HS Code line and return removed portion."""
    lines = raw_text.splitlines()
    line_number = lines[0].split()[0] if lines and lines[0].strip() else ""

    try:
        # General HS code pattern: 4-10 digits with optional dots (e.g., 8708.99.8180, 8708998180, 8708.99)
        hs_code_pattern = r'\b\d{4}(?:\.\d{2}(?:\.\d{4})?)?\b'
        start_idx = next(i for i, line in enumerate(lines) if re.search(hs_code_pattern, line))

        # Cleaned block starts from HS code line, without prepending line_number
        cleaned_lines = [lines[start_idx]] + lines[start_idx + 1:]
        cleaned_text = "\r\n".join(cleaned_lines)

        # Removed block is everything before HS code
        removed_lines = lines[:start_idx]
        removed_text = "\r\n".join(removed_lines)

        return cleaned_text, removed_text
    except StopIteration:
        return raw_text, ""  # Return original block, no removed section

# Load templates
temp1 = read_templates('Template3/')
browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\EKH-1007199-6-7501.pdf"

try:
    result2 = extract_data(browse_file_var, templates=temp1)
    print("Original Result2:", result2)

    removed_texts = []  # To hold removed content

    if result2 and 'check2' in result2:
        cleaned_checks = []
        check2_data = result2['check2']
        if isinstance(check2_data, str):
            # Split into blocks if multiple HS codes exist (e.g., separated by double newlines)
            blocks = [block for block in check2_data.split('\r\n\r\n') if block.strip()]
            if not blocks:
                blocks = [check2_data]  # Treat as single block if no split
            for block in blocks:
                cleaned_block, removed_block = clean_check_block(block)
                cleaned_checks.append(cleaned_block)
                removed_texts.append(removed_block)
        elif isinstance(check2_data, list):
            # Process each block in the list
            for block in check2_data:
                cleaned_block, removed_block = clean_check_block(block)
                cleaned_checks.append(cleaned_block)
                removed_texts.append(removed_block)
        else:
            raise ValueError(f"Unexpected type for check2: {type(check2_data)}")

        result2['check2'] = cleaned_checks
        result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference

    print("\nCleaned Result2:", result2)

    # Extract dollar amounts from both check2 and removed_texts
    dollar_values = [
        float(match.replace(",", "").replace("$", ""))
        for text in (removed_texts)  # Combine all relevant texts
        for match in re.findall(r'\$\d{1,3}(?:,\d{3})*\.\d{2}\b', text)
    ]

    print("Extracted Dollar Values:", dollar_values)

except Exception as e:
    print('Error while fetching all invoices details: ' + str(e))