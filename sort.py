import pandas as pd
import numpy as np

df1 = pd.read_csv('data.csv', index_col=0)

df1.index = df1.index.astype(int)

df1 = df1.sort_index()

# df1.to_csv('data_sort.csv')
duplicates = df1[df1.duplicated()]
print("Duplicate rows in df1:")
print(duplicates)