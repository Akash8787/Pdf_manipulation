import math

# Sample values (replace these with your actual values)
total_added_duty = 100.00
total_duty_val = 100.00

total_added_mpf = 291.00
total_mpf_val = 291.41

total_added_hmf = 123.45
total_hmf_val = 123.45

total_added_entered_value = 84124.00
total_entered_val = 84124.00

tolerance = 0.011

# Function to check match within bounds and other logic
def check_within_bounds(label, actual, expected, tolerance):
    lower_bound = expected - tolerance
    upper_bound = expected + tolerance
    lower_plus1 = expected - 1
    upper_plus1 = expected + 1

    # print(f"\n🔍 Checking {label}:")
    # print(f"   ➤ Expected: {expected}")
    # print(f"   ➤ Actual: {actual}")
    # print(f"   ➤ Allowed Range (±{tolerance}): {lower_bound:.2f} to {upper_bound:.2f}")

    if lower_bound <= actual <= upper_bound:
        print(f"✅ Total {label} matches.")
    elif int(actual) == int(expected):
        print(f"✅ Total {label} matches.")
    elif lower_plus1 <= actual <= upper_plus1:
        print(f"ℹ️ Total {label} not within tolerance or int match, but within ±1 range: {lower_plus1:.2f} to {upper_plus1:.2f}")
    else:
        print(f"❌ Total {label} mismatch! Expected: {expected}, Found: {actual:.2f}")

# Compare and report
check_within_bounds("Duty", total_added_duty, total_duty_val, tolerance)
check_within_bounds("MPF", total_added_mpf, total_mpf_val, tolerance)
check_within_bounds("HMF", total_added_hmf, total_hmf_val, tolerance)
check_within_bounds("Entered Value", total_added_entered_value, total_entered_val, tolerance)



# value = 2.50
# tolerance = 0.100

# lower_bound = 2.50 - 0.01 = 2.49  
# upper_bound = 2.50 + 0.01 = 2.51