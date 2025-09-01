from invoice2data import extract_data  
from invoice2data.extract.loader import read_templates

temp1 = read_templates('Template3/')
browse_file_var=r"D:\Python\Pdf_Manipulation\input_folder\56th1error\EKH-1007117-8-7501.pdf"
try:
    ## result2 variable where   Invoices details data extracted
    result2 = extract_data(browse_file_var,templates=temp1)
    print("Result2:",result2)
    # print("--------------------------------")
except Exception as e:
    print('Error while fetching all invoices details '+str(e))



# from invoice2data import extract_data
# from invoice2data.extract.loader import read_templates
# import re

# def clean_check_block(raw_text):
#     """Clean a single check block text to start from HS Code line."""
#     # Split into lines
#     lines = raw_text.splitlines()

#     # Get the line number from the very first line
#     line_number = lines[0].split()[0] if lines else ""

#     # Find where the HS Code (8708.xx.xxxx) line starts
#     try:
#         start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))
#         # Rebuild cleaned block: starting from HS Code, but keep line number attached
#         cleaned_lines = [f" {line_number} " + lines[start_idx]] + lines[start_idx + 1:]
#         cleaned_text = "\r\n".join(cleaned_lines)
#         return cleaned_text
#     except StopIteration:
#         # If no 8708... line is found, return the original
#         return raw_text

# # Main code
# temp1 = read_templates('test_template/')
# browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\53therror.PDF"

# try:
#     # Extract invoice data
#     result2 = extract_data(browse_file_var, templates=temp1)
#     print("Original Result2:", result2)

#     # Check if 'check' field exists and clean it
#     if result2 and 'check2' in result2:
#         cleaned_checks = []
#         for block in result2['check2']:
#             cleaned_block = clean_check_block(block)
#             cleaned_checks.append(cleaned_block)
#         result2['check2'] = cleaned_checks  # Update with cleaned blocks

#     print("\nCleaned Result2:", result2)

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
# temp1 = read_templates('test_template/')
# browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\55therror.PDF"

# try:
#     result2 = extract_data(browse_file_var, templates=temp1)
#     # print("Original Result2:", result2)

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
#         # Find HS code line (looking for 8708.xx.xxxx)
#         start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))

#         # Cleaned block starts from HS code
#         cleaned_lines = [f" {line_number} " + lines[start_idx]] + lines[start_idx + 1:]
#         cleaned_text = "\r\n".join(cleaned_lines)

#         # Removed block is everything before HS code
#         removed_lines = lines[:start_idx]
#         removed_text = "\r\n".join(removed_lines) if removed_lines else ""

#         return cleaned_text, removed_text
#     except StopIteration:
#         # If HS code not found, return the entire block as cleaned and empty removed portion
#         return raw_text, ""
#     except Exception as e:
#         # Log any other unexpected errors for debugging
#         print(f"Error in clean_check_block: {str(e)}")
#         return raw_text, ""

# # Load templates
# temp1 = read_templates('test_template/')
# browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\57therror.PDF"

# try:
#     result2 = extract_data(browse_file_var, templates=temp1)
#     # print("Original Result2:", result2)

#     removed_texts = []  # To hold removed content
#     cleaned_checks = []

#     if result2 and 'check2' in result2:
#         for idx, block in enumerate(result2['check2']):
#             try:
#                 cleaned_block, removed_block = clean_check_block(block)
#                 cleaned_checks.append(cleaned_block)
#                 removed_texts.append(removed_block)
#             except Exception as e:
#                 print(f"Error processing check2 block {idx}: {block}")
#                 print(f"Error: {str(e)}")
#                 cleaned_checks.append(block)  # Keep the original block if it fails
#                 removed_texts.append("")  # No removed portion

#         result2['check2'] = cleaned_checks
#         result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference
#     print("\nCleaned Result2:", result2)
#     # Extract dollar amounts with error handling
#     dollar_values = []
#     for text in removed_texts:
#         matches = re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', text)
#         for match in matches:
#             try:
#                 value = float(match.replace(",", "").replace("$", ""))
#                 dollar_values.append(value)
#             except ValueError as e:
#                 print(f"Error converting dollar value {match}: {str(e)}")

#     print("Extracted Dollar Values:", dollar_values)

# except Exception as e:
#     print('Error while fetching all invoices details: ' + str(e))


#cleaning text


# from invoice2data import extract_data
# from invoice2data.extract.loader import read_templates
# import re

# def clean_check_block(raw_text):
#     """Clean a single check block text to start from HS Code line, remove preceding lines, and remove weight."""
#     lines = raw_text.splitlines()
#     line_number = lines[0].split()[0] if lines else ""

#     try:
#         # Find the HS code line
#         start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))

#         # Clean the HS code line by removing weight (e.g., "592 KG") but keeping quantity (e.g., "7,200.00 NO")
#         hs_line = lines[start_idx]
#         # Remove the weight portion (e.g., "592 KG") while preserving the quantity and dollar amounts
#         cleaned_hs_line = re.sub(
#             r'^(.*?8708\.\d{2}\.\d{4})\s*(\d{1,3}(?:,\d{3})?\s*KG)?\s*(.*)$',
#             r'\1 \3',
#             hs_line
#         )

#         # Cleaned block starts from the modified HS code line
#         cleaned_lines = [f" {line_number} " + cleaned_hs_line] + lines[start_idx + 1:]
#         cleaned_text = "\r\n".join(cleaned_lines)

#         # Removed block is everything before HS code
#         removed_lines = lines[:start_idx]
#         removed_text = "\r\n".join(removed_lines) if removed_lines else ""

#         return cleaned_text, removed_text

#     except StopIteration:
#         # If HS code not found, return the entire block as cleaned and empty removed portion
#         return raw_text, ""
#     except Exception as e:
#         print(f"Error in clean_check_block: {str(e)}")
#         return raw_text, ""

# # Load templates
# temp1 = read_templates('test_template/')
# browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\57therror.PDF"

# try:
#     result2 = extract_data(browse_file_var, templates=temp1)
#     # print("Original Result2:", result2)

#     removed_texts = []  # To hold removed content for all blocks
#     cleaned_checks = []
#     cleaned_checks2 = []

#     # Process 'check' field
#     if result2 and 'check' in result2:
#         # Since 'check' is a single string, wrap it in a list for consistent processing
#         check_block = result2['check']
#         try:
#             cleaned_block, removed_block = clean_check_block(check_block)
#             cleaned_checks.append(cleaned_block)
#             removed_texts.append(removed_block)
#         except Exception as e:
#             print(f"Error processing check block: {check_block}")
#             print(f"Error: {str(e)}")
#             cleaned_checks.append(check_block)  # Keep the original block if it fails
#             removed_texts.append("")  # No removed portion

#         result2['check'] = cleaned_checks[0]  # Update the 'check' field

#     # Process 'check2' field
#     if result2 and 'check2' in result2:
#         for idx, block in enumerate(result2['check2']):
#             try:
#                 cleaned_block, removed_block = clean_check_block(block)
#                 cleaned_checks2.append(cleaned_block)
#                 removed_texts.append(removed_block)
#             except Exception as e:
#                 print(f"Error processing check2 block {idx}: {block}")
#                 print(f"Error: {str(e)}")
#                 cleaned_checks2.append(block)  # Keep the original block if it fails
#                 removed_texts.append("")  # No removed portion

#         result2['check2'] = cleaned_checks2  # Update the 'check2' field

#     # result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference

#     # Extract dollar amounts with error handling
#     dollar_values = []
#     for text in removed_texts:
#         matches = re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', text)
#         for match in matches:
#             try:
#                 value = float(match.replace(",", "").replace("$", ""))
#                 dollar_values.append(value)
#             except ValueError as e:
#                 print(f"Error converting dollar value {match}: {str(e)}")

#     print("Cleaned Result2:", result2)
#     print("Extracted Dollar Values:", dollar_values)

# except Exception as e:
#     print('Error while fetching all invoices details: ' + str(e))



#appending check to check2

from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import re

def clean_check_block(raw_text):
    """Clean a single check block text to start from HS Code line, remove preceding lines, and remove weight."""
    lines = raw_text.splitlines()
    line_number = lines[0].split()[0] if lines else ""

    try:
        # Find the HS code line
        start_idx = next(i for i, line in enumerate(lines) if re.search(r'\b8708\.\d{2}\.\d{4}\b', line))

        # Clean the HS code line by removing weight (e.g., "592 KG") but keeping quantity (e.g., "7,200.00 NO")
        hs_line = lines[start_idx]
        # Remove the weight portion (e.g., "592 KG") while preserving the quantity and dollar amounts
        cleaned_hs_line = re.sub(
            r'^(.*?8708\.\d{2}\.\d{4})\s*(\d{1,3}(?:,\d{3})?\s*KG)?\s*(.*)$',
            r'\1 \3',
            hs_line
        )

        # Cleaned block starts from the modified HS code line
        cleaned_lines = [f" {line_number} " + cleaned_hs_line] + lines[start_idx + 1:]
        cleaned_text = "\r\n".join(cleaned_lines)

        # Removed block is everything before HS code
        removed_lines = lines[:start_idx]
        removed_text = "\r\n".join(removed_lines) if removed_lines else ""

        return cleaned_text, removed_text

    except StopIteration:
        # If HS code not found, return the entire block as cleaned and empty removed portion
        return raw_text, ""
    except Exception as e:
        print(f"Error in clean_check_block: {str(e)}")
        return raw_text, ""

# Load templates
temp1 = read_templates('test_template/')
browse_file_var = r"D:\Python\Pdf_Manipulation\input_folder\57therror.PDF"

try:
    result2 = extract_data(browse_file_var, templates=temp1)
    # print("Original Result2:", result2)

    removed_texts = []  # To hold removed content for all blocks
    cleaned_checks = []
    cleaned_checks2 = []

    # Process 'check' field
    if result2 and 'check' in result2:
        # Since 'check' is a single string, wrap it in a list for consistent processing
        check_block = result2['check']
        try:
            cleaned_block, removed_block = clean_check_block(check_block)
            cleaned_checks.append(cleaned_block)
            removed_texts.append(removed_block)
        except Exception as e:
            print(f"Error processing check block: {check_block}")
            print(f"Error: {str(e)}")
            cleaned_checks.append(check_block)  # Keep the original block if it fails
            removed_texts.append("")  # No removed portion

        result2['check'] = cleaned_checks[0]  # Update the 'check' field

    # Process 'check2' field
    if result2 and 'check2' in result2:
        for idx, block in enumerate(result2['check2']):
            try:
                cleaned_block, removed_block = clean_check_block(block)
                cleaned_checks2.append(cleaned_block)
                removed_texts.append(removed_block)
            except Exception as e:
                print(f"Error processing check2 block {idx}: {block}")
                print(f"Error: {str(e)}")
                cleaned_checks2.append(block)  # Keep the original block if it fails
                removed_texts.append("")  # No removed portion
    else:
        # If 'check2' doesn't exist, initialize it as an empty list
        result2['check2'] = []

    # Append the cleaned 'check' block to 'check2'
    if cleaned_checks:
        result2['check2'].append(cleaned_checks[0])

    # Update 'check2' in result2
    result2['check2'] = cleaned_checks2 + result2['check2'] if cleaned_checks2 else result2['check2']

    # Remove 'missingboxes2' and 'check' from result2
    if 'missingboxes2' in result2:
        del result2['missingboxes2']
    if 'check' in result2:
        del result2['check']

    # result2['removed_texts'] = removed_texts  # Add removed list to result2 for reference

    # Extract dollar amounts with error handling
    dollar_values = []
    for text in removed_texts:
        matches = re.findall(r'\$\d{1,3}(?:,\d{3})?\.\d{2}', text)
        for match in matches:
            try:
                value = float(match.replace(",", "").replace("$", ""))
                dollar_values.append(value)
            except ValueError as e:
                print(f"Error converting dollar value {match}: {str(e)}")

    print("Cleaned Result2:", result2)
    print("Extracted Dollar Values:", dollar_values)

except Exception as e:
    print('Error while fetching all invoices details: ' + str(e))