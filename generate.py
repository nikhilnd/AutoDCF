from importlib.resources import open_binary
import pandas as pd
from data import get_data, parse_data
import openpyxl
import os
import uuid

def generate_dcf(ticker, path, id):

    # Get data 
    print("Getting data...")
    for attempt in range(0, 4): 
        try: 
            dfs, units = get_data(ticker)
            break
        except: 
            if(attempt == 3): 
                print("Failed to retrieve data. Please try again.")
                raise RuntimeError("Failed to get data")
            print("Error, trying again...")

    # Set up file path 
    files = os.path.join(path, "files")
    os.mkdir(os.path.join(files, str(id)))
    template = os.path.join(files, "DCF_Template.xlsx")

    # Filter and parse necessary data
    cats = ["Sales/Revenue", "Cost of Goods Sold (COGS) incl. D&A", "SG&A Expense", "Research & Development", "Income Tax", "Capital Expenditures", "Depreciation, Depletion & Amortization", "Changes in Working Capital"]
    data = parse_data(dfs, units, cats)

    updatedCats = ["Sales/Revenue", "Cost of Goods Sold (COGS) incl. D&A", "SGA", "Research & Development", "Income Tax", "Capital Expenditures", "Depreciation, Depletion & Amortization", "Changes in Working Capital"]
    data = data.reindex(updatedCats)
    cols = data.columns

    row_nums = [7, 9, 13, 15, 19, 21, 23, 24] 
    curr = 0

    wb = openpyxl.load_workbook(template)
    model = wb.active

    # Enter data into spreadsheet by row 
    for index, row in data.iterrows(): 
        curr_row = str(row_nums[curr])
        model['C' + curr_row] = row[cols[2]] if row[cols[2]] != "-" else 0
        model['D' + curr_row] = row[cols[1]] if row[cols[1]] != "-" else 0
        model['E' + curr_row] = row[cols[0]] if row[cols[0]] != "-" else 0
        curr = curr + 1

    new_file = os.path.join(os.path.join(files, str(id)), "DCF_" + ticker + ".xlsx")
    wb.save(filename=new_file)

    return new_file 


### TESTING: 
# ticker = input("Enter ticker symbol: ")
# id = uuid.uuid4()
# file = generate_dcf(ticker, "/Users/nikhildeorkar/code/swe/AutoDCF/src", id)
# print(file)