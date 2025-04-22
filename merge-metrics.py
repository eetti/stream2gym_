import pandas as pd
import numpy as np

# List to store all dataframes
all_dfs = []

# Generate file names (states-h1.csv through states-h10.csv)
file_paths = [f'metrics/states-h{i}.csv' for i in range(1, 11)]

# Process each file
for file_path in file_paths:
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Drop columns we don't want to average
        df = df.drop(columns=['timestamp', 'host'])
        
        # Keep run_index as a column for now
        all_dfs.append(df)
    except FileNotFoundError:
        print(f"Warning: Could not find file {file_path}")
        continue
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        continue

# Check if we have any data
if not all_dfs:
    print("No files were successfully processed!")
else:
    # Combine all dataframes along rows
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Get numeric columns excluding run_index
    numeric_columns = combined_df.select_dtypes(include=[np.number]).columns
    numeric_columns = numeric_columns.drop('run_index')  # Exclude run_index from averaging
    
    # Group by run_index and calculate mean for numeric columns
    mean_df = combined_df.groupby('run_index')[numeric_columns].mean()
    
    # Round numeric values to 2 decimal places
    mean_df = mean_df.round(2)
    
    # Sort columns alphabetically (optional)
    mean_df = mean_df.reindex(sorted(mean_df.columns), axis=1)
    
    # Reset index to make run_index a column again
    mean_df = mean_df.reset_index()
    
    # Save to CSV
    mean_df.to_csv('merged_means_by_index.csv', index=False)
    
    # Print results
    print("Mean values across all files by run_index:")
    print(mean_df.to_string(index=False))
    print("\nNumber of unique run_index values:", len(mean_df))
    print("Number of files processed:", len(all_dfs))
    

# Read the existing merged means file
try:
    existing_df = pd.read_csv('merged_means_by_index.csv')
except FileNotFoundError:
    print("Error: 'merged_means_by_index.csv' not found. Please run the previous script first.")
    exit(1)

# Read the new performance metrics file
new_file_path = 'data.csv'  # Change this to your actual file name
try:
    new_df = pd.read_csv(new_file_path)
except FileNotFoundError:
    print(f"Error: Could not find file '{new_file_path}'")
    exit(1)
except Exception as e:
    print(f"Error reading {new_file_path}: {str(e)}")
    exit(1)

# Select only the columns we need
new_df = new_df[['index', 'Throughput', 'Latency']]

# Rename 'index' to 'run_index' to match the existing file
new_df = new_df.rename(columns={'index': 'run_index'})

# Merge with existing dataframe
# Using left join to keep all rows from existing_df
merged_df = pd.merge(existing_df, new_df, on='run_index', how='left')

# Round the new columns to 2 decimal places
merged_df['Throughput'] = merged_df['Throughput'].round(2)
merged_df['Latency'] = merged_df['Latency'].round(2)

# Sort columns alphabetically (optional, excluding run_index)
cols = ['run_index'] + sorted([col for col in merged_df.columns if col != 'run_index'])
merged_df = merged_df[cols]

# Save the updated file
merged_df.to_csv('states.csv', index=False)

# Print results
print("Merged means with Throughput and Latency:")
print(merged_df.to_string(index=False))
print("\nNumber of rows in merged file:", len(merged_df))