import pandas as pd
import numpy as np

# Load your data (replace with your actual file paths)
df1 = pd.read_csv('schedule.csv', index_col=0)
df2 = pd.read_csv('data.csv', index_col=0)

# Ensure the indexes are of the same type (e.g., string, int)
df1.index = df1.index.astype(str)
df2.index = df2.index.astype(str)

# Find index differences
missing_in_df2 = df1.index.difference(df2.index)
missing_in_df1 = df2.index.difference(df1.index)

print("Indexes in df1 but not in df2:")
print(len(missing_in_df2))
rows = []
for idx in missing_in_df2:
    rows.append(idx)

# rows.sort()
# print(rows)

missing_rows_df = df1.loc[missing_in_df2]
missing_rows_df.index = missing_rows_df.index.astype(int)
missing_rows_df = missing_rows_df.sort_index()

# Write to a new CSV file
missing_rows_df.to_csv('missing_in_df2.csv')

# print("\nIndexes in df2 but not in df1:")
# print(missing_in_df1)

# Find common indexes to compare rows
# common_indexes = df1.index.intersection(df2.index)

# Compare rows for differences in content
# mismatched_rows = []
# for idx in common_indexes:
#     if not df1.loc[idx].equals(df2.loc[idx]):
#         mismatched_rows.append(idx)

# print("\nMismatched rows (same index, different data):")
# print(mismatched_rows)
