import requests
from bs4 import BeautifulSoup
import pandas as pd

# def test_apply(arr):
#     arr = arr.copy()
#     for k, value in enumerate(arr): 
#         print(value)
#         arr[k] = 3
#     return arr

def convert(arr): 
    for k, value in enumerate(arr): 
        if "(" in value: 
            temp = value.replace("(", "").replace(")", "").replace(",", "")
            temp = str(round(float(temp) / 1000, 2))
            arr[k] = "(" + temp + ")"
        elif "-" in value: 
            continue
        else: 
            temp = str(round(float(value) / 1000, 2))
            arr[k] = temp

    return arr 

def get_data(ticker):

    # URLs and headers
    is_url = "https://www.wsj.com/market-data/quotes/" + ticker + "/financials/annual/income-statement"
    cf_url = "https://www.wsj.com/market-data/quotes/" + ticker + "/financials/annual/cash-flow"
    headers = {"User-Agent": "Mozilla/5.0"}

    # Get HTML
    is_res = requests.get(is_url, headers=headers)
    cf_res = requests.get(cf_url, headers=headers)
    is_soup = BeautifulSoup(is_res.text, 'html.parser')
    cf_soup = BeautifulSoup(cf_res.text, 'html.parser')

    # Parse HTML for tables
    table_is = str(is_soup.find_all('table', class_="cr_dataTable"))
    table_op = str(cf_soup.find_all('table', class_="cr_dataTable")[0])
    table_inv = str(cf_soup.find_all('table', class_="cr_dataTable")[1])

    # Read data from tables into dataframes 
    df_is = pd.read_html(table_is)[0]
    df_op = pd.read_html(table_op)[0]
    df_inv = pd.read_html(table_inv)[0]

    # Check if any of the tables are in thousandas instead of millions
    units_is = df_is.columns[0]
    units_op = df_op.columns[0]
    units_inv = df_inv.columns[0]
    ths = ["Thousands" in units_is, "Thousands" in units_op, "Thousands" in units_inv]

    # Rename dataframes to merge
    df_is = df_is.rename(columns={df_is.columns[0]: 'category'})
    df_op = df_op.rename(columns={df_op.columns[0]: 'category'})
    df_inv = df_inv.rename(columns={df_inv.columns[0]: 'category'})

    # Return dataframe and thousandas array
    return [df_is, df_op, df_inv], ths

def filter_data(df, cats): 
    data = df[df["category"].isin(cats)]
    data.set_index("category", inplace=True)
    # Potential point of failure
    data = data.drop(columns=['5-year trend'])
    return data 

def parse_data(dfs, units, cats): 

    dfs = [filter_data(df, cats) for df in dfs]

    for k, unit in enumerate(units): 
        if unit: 
            print("running")
            dfs[k] = dfs[k].apply(convert)

    df = pd.concat(dfs)
    return df

for attempts in range(0, 3): 
    try: 
        dfs, units = get_data("SBUX")
        break 
    except: 
        if(attempts == 2): 
            print("Failed to get data")
            exit() 
        print("Something went wrong. Trying again...")

# cats = ["Sales/Revenue", "Cost of Goods Sold (COGS) incl. D&A", "Other SG&A", "Research & Development", "Income Tax", "Capital Expenditures", "Depreciation, Depletion & Amortization", "Changes in Working Capital"]
cats = ["Sales/Revenue", "Cost of Goods Sold (COGS) incl. D&A", "SG&A Expense", "Research & Development", "Income Tax", "Capital Expenditures", "Depreciation, Depletion & Amortization", "Changes in Working Capital"] # Also include total SGA 
df = parse_data(dfs, units, cats)
df.loc["SGA"] = df.apply(lambda x: (float(x["SG&A Expense"].replace(",", "")) if "-" not in x["SG&A Expense"] else 0) - (float(x["Research & Development"].replace(",", "")) if "-" not in x["Research & Development"] else 0)) # Calculate new row (total SGA - R&D)
df = df.drop(["SG&A Expense"], axis=0) # Drop total SGA, not needed
df.to_csv("data.csv")

