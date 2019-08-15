import csv, tkinter
import pandas as pd
from os import makedirs, path
from tabula import read_pdf
from dateutil.relativedelta import relativedelta
from datetime import date
from shutil import copyfile
from getpass import getpass
from tkinter import filedialog

# Get the fieldnames of csv file.
with open(
        '../inputs/AndroMoney.csv', mode='r', encoding='cp950', 
        newline='') as f:
    reader = csv.reader(f)
    fieldnames = [row for idx, row in enumerate(reader) if idx == 1][0]

# Preprocess csv file.
df = pd.read_csv('../inputs/AndroMoney.csv', encoding='cp950', header=1)
df = df[pd.notnull(df['Expense(Transfer Out)'])]
df = df[pd.isnull(df['Income(Transfer In)'])]
df = df.sort_values(by='Date')

# Output frequently used categories as reference.
date_divide = (date.today()+relativedelta(months=-6)).strftime('%Y%m%d')
df_divide = df[df['Date']>int(date_divide)]
s = df_divide.groupby(['Category', 'Sub-Category']).size()
s = s.sort_values(ascending=False)
codes_frequent = s.index.codes
levels_frequent = s.index.levels
makedirs('./outputs/', exist_ok=True)
# In Microsoft Excel format.
with open(
        './outputs/frequent.csv', mode='w', encoding='utf_16',
        newline='') as f:
    writer = csv.DictWriter(
        f, fieldnames=['Code', 'Category', 'Sub-Category'], delimiter='\t')
    frequent_max = 20
    num_codes = frequent_max if len(codes_frequent[0])>frequent_max \
        else len(codes_frequent[0])
    for i in range(num_codes):
        writer.writerow({
            'Code': i, 'Category': levels_frequent[0][codes_frequent[0][i]],
            'Sub-Category': levels_frequent[1][codes_frequent[1][i]]})

# Output all categories as reference.
date_divide = (date.today()+relativedelta(years=-1)).strftime('%Y%m%d')
df_divide = df[df['Date']>int(date_divide)]
s = df_divide.groupby(['Category', 'Sub-Category']).size()
codes_all = s.index.codes
levels_all = s.index.levels
with open('./outputs/all.csv', mode='w', encoding='utf_16', newline='') as f:
    writer = csv.DictWriter(
        f, fieldnames=['Code', 'Category', 'Sub-Category'], delimiter='\t')
    for i in range(len(codes_all[0])):
        writer.writerow({
            'Code': i+frequent_max, 'Category': levels_all[0][codes_all[0][i]],
            'Sub-Category': levels_all[1][codes_all[1][i]]})

# Preprocess bill file.
root = tkinter.Tk()
root.withdraw()
input_path = filedialog.askopenfilename(initialdir ='../inputs/')
if not input_path: raise FileNotFoundError('Not selected file.')
pdf_basename = path.basename(input_path)
# Bill of HSBC Bank.
if 'eStatement_' in pdf_basename:
    password = getpass('Password: ')
    param = [2, 4, -1] # [pages, index_head, column]
    df_bill = read_pdf(input_path, password=password, pages=param[0])
    df_bill = df_bill.iloc[param[1]:,param[2]]
# Bill of Cathay United Bank.
elif 'Download' in pdf_basename:
    header = 14 # For future modification.
    df_bill = pd.read_csv(input_path, encoding='cp950', header=header)
    # Abstract transcations by checking existence of card digits.
    boolean = pd.notna(pd.to_numeric(df_bill['卡號末四碼'], errors='coerce'))
    
    df_bill = df_bill[boolean]
    df_bill = df_bill['臺幣金額']
else:
    FileNotFoundError('Selected file is not supported bill.')
    
copyfile('../inputs/AndroMoney.csv', './outputs/AndroMoney.csv')
# Ouput appended csv file.
with open(
        './outputs/AndroMoney.csv', mode='a', encoding='cp950',
        newline='') as f:
    writer = csv.DictWriter(
        f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    date = input('Paid date (yyyymmdd): ')
    for amount in df_bill:
        print('NT$:', amount, end='')
        code = int(input('; code: '))
        if code is -1:
            continue
        elif 0 <= code < frequent_max:
            codes = codes_frequent
            levels = levels_frequent
        elif frequent_max <= code < len(codes_all[0])+frequent_max:
            codes = codes_all
            levels = levels_all
            code -= frequent_max # codes_all and levels_all start from index 0.
        else:
            raise ValueError('varialbe \'code\' has wrong value.')
        writer.writerow(
            {'Currency': 'TWD', 'Amount': float(amount.replace(',','')),
                'Date': date, 'Expense(Transfer Out)': 'Winston第一銀行臺幣',
                'Category': levels[0][codes[0][code]],
                'Sub-Category': levels[1][codes[1][code]]})