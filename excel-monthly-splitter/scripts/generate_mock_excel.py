import pandas as pd
from datetime import datetime, timedelta

# Create mock data for Sheet1
dates1 = [datetime(2026, 3, 1), datetime(2026, 3, 1), datetime(2026, 3, 2)]
data1 = {
    'Date': dates1,
    'ValueA': [10, 20, 30],
    'Category': ['X', 'Y', 'Z']
}
df1 = pd.DataFrame(data1)

# Create mock data for Sheet2
dates2 = [datetime(2026, 3, 1), datetime(2026, 3, 3)]
data2 = {
    '日期': dates2,
    'ID': [1001, 1002],
    'Status': ['OK', 'FAIL']
}
df2 = pd.DataFrame(data2)

# Write to excel
with pd.ExcelWriter('/Users/wxj/gitsource/skills/excel-monthly-splitter/scripts/test.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)

print("Mock Excel file created at /Users/wxj/gitsource/skills/excel-monthly-splitter/scripts/test.xlsx")
