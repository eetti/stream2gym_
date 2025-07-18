import pandas as pd

# Input and output file paths
input_file = 'schedule.csv'
output_file = 'schedule_first_1000.csv'

# Read the first 1000 rows including the header
df = pd.read_csv(input_file, nrows=1000)

# Save to a new CSV file
df.to_csv(output_file, index=False)

print(f"Successfully saved first 1000 rows to '{output_file}'")
