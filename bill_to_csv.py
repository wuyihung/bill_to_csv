"""Appends transactions of limited credit card bills to AndroMoney file.

Parses following credit card bills and appends parsed transactions to 
AndroMoney CSV file:
    1. HSBC PDF file;
    2. Cathay United Bank CSV file.

MIT License
Copyright (c) 2019 WU, YI-HUNG

Third party copyrights:
    AndroMoney CSV file: Copyright (c) 2016 AndroMoney.
    HSBC PDF file: (c) Copyright. HSBC Bank (Taiwan) Company 
        Limited 2019.
    Cathay United Bank CSV file: (c) Cathay United Bank All rights reserved.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import csv
import datetime
import getpass
import os
import shutil
import tabula
import tkinter

import pandas as pd

from dateutil import relativedelta
from tkinter import filedialog


def read_file(title, initialdir):
    root = tkinter.Tk()
    root.withdraw()
    input_file = tkinter.filedialog.askopenfilename(title=title,
                                                    initialdir=initialdir)
    if not input_file:
        raise FileNotFoundError('Not selected file.')
    else:
        return input_file


class AndroMoney(object):
    """Class to parse AndroMoney file.
    """
    def __init__(self, num_freq_categories, last_directory):
        """Initializes instance object.
        
        Args:
            num_freq_categories: Number of most frequently used categories.
        """
        self._boundary_index = 100
        self._num_freq_categories = num_freq_categories

        self._init_file(last_directory)
        self._init_fieldnames()
        self._init_expenses()
        self._init_frequently_used_categories()
        self._init_all_categories()

    def _init_file(self, last_directory):
        file = read_file(title='Select AndroMoney file to be appended',
                         initialdir=last_directory)
        if 'AndroMoney' in file:
            self._file = file
        else:
            raise FileNotFoundError('Selected file is not AndroMoney file.')

        self.last_directory = os.path.dirname(file)

    def _init_fieldnames(self):
        """Gets fieldnames.
        """
        with open(self._file, mode='r', encoding='cp950', newline='') as f:
            reader = csv.reader(f)
            self._all_fieldnames = [
                row for idx, row in enumerate(reader) if idx == 1
            ][0]

        self._fieldnames = {
            'currency': self._all_fieldnames[1],
            'amount': self._all_fieldnames[2],
            'category': self._all_fieldnames[3],
            'sub_category': self._all_fieldnames[4],
            'date': self._all_fieldnames[5],
            'outflow': self._all_fieldnames[6],
            'inflow': self._all_fieldnames[7]
        }

    def _init_expenses(self):
        """Gets expenses and sorts them by date.
        """
        df = pd.read_csv(self._file, encoding='cp950', header=1)
        df = df[pd.notnull(df[self._fieldnames['outflow']])]
        df = df[pd.isnull(df[self._fieldnames['inflow']])]
        self._expenses = df.sort_values(by=self._fieldnames['date'])

    def _init_frequently_used_categories(self):
        """Initializes frequently used categories.
        
        Initializes codes and levels of frequently used categories.
        """
        expenses = self._expenses
        six_months_ago = relativedelta.relativedelta(months=-6)
        date_divide = (datetime.date.today() +
                       six_months_ago).strftime('%Y%m%d')
        expenses_divide = expenses[
            expenses[self._fieldnames['date']] > int(date_divide)]
        s = expenses_divide.groupby(by=[
            self._fieldnames['category'], self._fieldnames['sub_category']
        ]).size()
        s = s.sort_values(ascending=False)
        self._codes_frequent = s.index.codes
        self._levels_frequent = s.index.levels

    def _make_dir(self, output_file):
        norm_path = os.path.normpath(output_file)
        split_path = norm_path.split(os.sep)
        output_directory = os.path.join(*split_path[:-1])
        os.makedirs(output_directory, exist_ok=True)

    def output_frequently_used_categories(self, output_file):
        """Outputs CSV file of frequently used categories.
        
        Outputs CSV file of frequently used categories in a format Microsoft 
        Excel can open.

        Args:
            output_file: path of output file.
        """
        codes_frequent = self._codes_frequent
        levels_frequent = self._levels_frequent
        num_freq_categories = self._num_freq_categories

        self._make_dir(output_file)
        with open(output_file, mode='w', encoding='utf_16', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['Code', 'Category', 'Sub-Category'],
                delimiter='\t')
            num_codes = (num_freq_categories
                         if len(codes_frequent[0]) > num_freq_categories else
                         len(codes_frequent[0]))

            writer.writerow({
                'Code': 0,
                'Category': '其他',
                'Sub-Category': '待分類'
            })

            for i in range(num_codes):
                writer.writerow({
                    'Code':
                    1 + i,
                    'Category':
                    levels_frequent[0][codes_frequent[0][i]],
                    'Sub-Category':
                    levels_frequent[1][codes_frequent[1][i]]
                })

    def _init_all_categories(self):
        """Initializes all categories.
        
        Initializes codes and levels of all categories.
        """
        expenses = self._expenses
        one_year_ago = relativedelta.relativedelta(years=-1)
        date_divide = (datetime.date.today() + one_year_ago).strftime('%Y%m%d')
        expenses_divide = expenses[
            expenses[self._fieldnames['date']] > int(date_divide)]
        s = expenses_divide.groupby(by=[
            self._fieldnames['category'], self._fieldnames['sub_category']
        ]).size()
        self._codes_all = s.index.codes
        self._levels_all = s.index.levels

    def output_all_categories(self, output_file):
        """Outputs CSV file of all categories.
        
        Outputs CSV file of all categories in a format Microsoft Excel can open.
        
        Args:
            output_file: path of output file.
        """
        codes_all = self._codes_all
        levels_all = self._levels_all

        self._make_dir(output_file)
        with open(output_file, mode='w', encoding='utf_16', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['Code', 'Category', 'Sub-Category'],
                delimiter='\t')
            for i in range(len(codes_all[0])):
                writer.writerow({
                    'Code': self._boundary_index + 1 + i,
                    'Category': levels_all[0][codes_all[0][i]],
                    'Sub-Category': levels_all[1][codes_all[1][i]]
                })

    def append(self, transactions, output_dir):
        """Appends transactions to newly-copied AndroMoney file.

        Copis original AndroMoney file to output file and appends transactions 
        to it (output file).
        
        Args:
            transactions: Transactions to be appended to output file.
            output_dir: Directory of newly-copied output file.
        
        Raises:
            ValueError: User types wrong code.
        """
        output_file = os.path.join(output_dir, 'AndroMoney.csv')
        shutil.copyfile(self._file, output_file)
        with open(output_file, mode='a', encoding='cp950', newline='') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=self._all_fieldnames,
                                    quoting=csv.QUOTE_ALL)
            date = input('Paid date (yyyymmdd): ')

            boundary_index = self._boundary_index
            codes_all = self._codes_all
            codes_frequent = self._codes_frequent
            levels_all = self._levels_all
            levels_frequent = self._levels_frequent

            print('Enter category codes of following transactions.')
            print('Enter 0 to skip a transactions.')
            for amount in transactions:
                print('NT$:', amount, end='')
                code = int(input('; code: '))
                if code is 0:
                    writer.writerow({
                        self._fieldnames['currency']:
                        'TWD',
                        self._fieldnames['amount']:
                        float(amount.replace(',', '')),
                        self._fieldnames['date']:
                        date,
                        self._fieldnames['outflow']:
                        'Winston第一銀行臺幣',
                        self._fieldnames['category']:
                        '其他',
                        self._fieldnames['sub_category']:
                        '待分類'
                    })
                    continue
                elif 0 < code < boundary_index + 1:
                    index = code - 1
                    codes = codes_frequent
                    levels = levels_frequent
                elif boundary_index < code < len(
                        codes_all[0]) + boundary_index + 1:
                    index = code - (boundary_index + 1)
                    codes = codes_all
                    levels = levels_all
                else:
                    raise ValueError('varialbe \'code\' has wrong value.')

                writer.writerow({
                    self._fieldnames['currency']:
                    'TWD',
                    self._fieldnames['amount']:
                    float(amount.replace(',', '')),
                    self._fieldnames['date']:
                    date,
                    self._fieldnames['outflow']:
                    'Winston第一銀行臺幣',
                    self._fieldnames['category']:
                    levels[0][codes[0][index]],
                    self._fieldnames['sub_category']:
                    levels[1][codes[1][index]]
                })


def read_hsbc(file):
    """Returns transactions of HSBC credit card bill.
    
    Args:
        file: File of HSBC credit card bill.
    """
    password = getpass.getpass('Password: ')
    df_bill_list = tabula.read_pdf(file, password=password, pages=2)
    df_bill = df_bill_list[0]

    index = df_bill.index
    na_index = index[df_bill.iloc[:, 0].isna()]
    start_position = index.get_loc(na_index[1]) + 1
    end_position = index.get_loc(na_index[2])

    s_bill = df_bill.iloc[start_position:end_position, -1]

    return s_bill


def read_cathay(file):
    """Returns transactions of Cathay credit card bill.
    
    Args:
        file: File of Cathay United Bank credit card bill.
    """
    # Can be modified if format changes.
    header = 14
    df_bill = pd.read_csv(file, encoding='cp950', header=header)
    # Abstracts transcations by checking existence of card digits.
    boolean = pd.notna(pd.to_numeric(df_bill['卡號末四碼'], errors='coerce'))

    df_bill = df_bill[boolean]
    df_bill = df_bill['臺幣金額']
    df_bill = df_bill.str.strip()
    return df_bill


def read_transactions(last_directory):
    """Returns transactions of credit card bill.
    """
    file = read_file(title='Select credit card bill', initialdir=last_directory)

    # True if file is from HSBC Bank.
    if 'eStatement_' in file:
        return read_hsbc(file)
    # True if file is from Cathay United Bank.
    elif 'Download' in file:
        return read_cathay(file)
    else:
        raise FileNotFoundError('Selected file is not supported bill.')


def main():
    """The first function to execute when running this module.
    """
    last_directory = '~'

    andro_money = AndroMoney(num_freq_categories=20, last_directory=last_directory)

    # Outputs codes of categories for user to refer to.
    output_dir = 'outputs'
    andro_money.output_frequently_used_categories(
        os.path.join(output_dir, 'frequent.csv'))
    andro_money.output_all_categories(os.path.join(output_dir, 'all.csv'))

    # Reads transactions from credit card bill.
    transactions = read_transactions(andro_money.last_directory)

    # Appends transactions to newly-copied AndroMoney file.
    andro_money.append(transactions, output_dir)


if __name__ == '__main__':
    main()