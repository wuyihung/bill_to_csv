"""Tests bill_to_csv.py.

Considering copyrights and privacy, bills, passwords of bills, and AndroMoney 
file for testing are unavailable on GitHub.

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

import bill_to_csv
import csv
import datetime
import dotenv
import freezegun
import os
import unittest

import numpy as np
import pandas as pd

from os import path
from unittest import mock


def _compare_csv_files(self, file, ref_file, encoding):
    """For class unittest.TestCase to compare csv files."""
    with open(file, encoding=encoding, newline='') as csv_file:
        with open(ref_file, encoding=encoding, newline='') as csv_file_ref:
            reader = csv.reader(csv_file)
            reader_ref = csv.reader(csv_file_ref)
            for row, row_ref in zip(reader, reader_ref):
                self.assertEqual(row, row_ref)


class TestAndroMoney(unittest.TestCase):
    @freezegun.freeze_time('2019-05-20')
    @mock.patch('bill_to_csv.read_file')
    def setUp(self, read_file):
        self._test_dir = path.dirname(path.relpath(__file__))
        self._out_dir = 'outputs'
        self._ref_dir = 'references'

        in_dir = 'inputs'
        file_name = 'AndroMoney.csv'
        read_file.return_value = path.join(self._test_dir, in_dir, file_name)
        self._andro_money = bill_to_csv.AndroMoney(num_freq_categories=20, last_directory='')

    def test_init_fieldnames(self):
        """Tests Chinese or English fieldnames."""
        self._andro_money._init_fieldnames()

        all_fieldnames = self._andro_money._all_fieldnames
        fieldnames = self._andro_money._fieldnames

        if fieldnames['currency'] == '幣別':
            all_fieldnames_ref = [
                'Id', '幣別', '金額', '分類', '子分類', '日期', '付款(轉出)', '收款(轉入)', '備註',
                'Periodic', '專案', '商家(公司)', 'uid', '時間'
            ]
        elif fieldnames['currency'] == 'Currency':
            all_fieldnames_ref = [
                'Id', 'Currency', 'Amount', 'Category', 'Sub-Category', 'Date',
                'Expense(Transfer Out)', 'Income(Transfer In)', 'Note',
                'Periodic', 'Project', 'Payee/Payer', 'uid', 'Time'
            ]
        else:
            raise ValueError("fieldnames['currency'] has an unexpected value")

        fieldnames_ref = {
            'currency': all_fieldnames[1],
            'amount': all_fieldnames[2],
            'category': all_fieldnames[3],
            'sub_category': all_fieldnames[4],
            'date': all_fieldnames[5],
            'outflow': all_fieldnames[6],
            'inflow': all_fieldnames[7]
        }

        self.assertListEqual(all_fieldnames, all_fieldnames_ref)
        self.assertDictEqual(fieldnames, fieldnames_ref)

    def test_init_expenses(self):
        expenses = self._andro_money._expenses
        self.assertTrue(pd.notnull(expenses['Expense(Transfer Out)']).all)
        self.assertTrue(pd.isnull(expenses['Income(Transfer In)']).all)
        self.assertEqual(list(expenses['Date']), sorted(expenses['Date']))

    def test_init_frequently_used_categories(self):
        codes_frequent = [list(x) for x in self._andro_money._codes_frequent]
        levels_frequent = [list(x) for x in self._andro_money._levels_frequent]

        codes_frequent_ref = [[
            11, 10, 8, 3, 8, 11, 8, 11, 10, 1, 0, 2, 0, 9, 1, 2, 5, 1, 5, 4, 5,
            3, 8, 5, 4, 3, 3, 6, 10, 8, 3, 1, 1, 8, 4, 9, 5, 2, 0, 9, 8, 4, 6,
            1, 3, 9, 2, 7, 2, 2, 3
        ],
                              [
                                  0, 11, 16, 28, 7, 49, 14, 50, 6, 13, 30, 12,
                                  17, 15, 26, 21, 47, 44, 10, 40, 48, 20, 37,
                                  36, 18, 46, 43, 1, 5, 4, 27, 41, 45, 34, 24,
                                  2, 3, 33, 32, 38, 42, 23, 9, 29, 31, 35, 19,
                                  39, 22, 25, 8
                              ]]
        levels_frequent_ref = [
            [
                '人情交際', '休閒娛樂', '其他', '居家生活', '教育學習', '服飾美容', '理財投資', '費用',
                '運輸交通', '醫療保健', '長期不影響負債', '餐飲食品'
            ],
            [
                '三餐+食材', '事業經營', '保險', '保養/化妝', '保養維修費', '借他人錢', '借出錢', '停車費',
                '傢俱', '儲蓄險', '內衣褲', '公司代墊', '其他', '出遊/拜訪親戚', '加油', '勞健保/國民年金',
                '大眾運輸', '孝養父母', '影印', '慈善捐款', '房租', '手續費/規費', '換匯', '文具',
                '書籍雜誌', '會員費/卡片押金', '玩具/小物', '瓦斯費', '生活用品', '福利金', '禮物/請客',
                '租屋押金', '紅白包', '繳稅', '罰單', '藥物', '衣裙褲襪外套', '計程車/租車', '診所/醫院',
                '轉帳費用', '進修課程', '運動', '郵資', '電信費', '電動/Netflix', '電影院/KTV',
                '電費', '鞋包配件', '頭髮相關', '飲品', '點心零嘴'
            ]
        ]

        self.assertListEqual(codes_frequent, codes_frequent_ref)
        self.assertListEqual(levels_frequent, levels_frequent_ref)

    def test_init_all_categories(self):
        codes_all = [list(x) for x in self._andro_money._codes_all]
        levels_all = [list(x) for x in self._andro_money._levels_all]

        codes_all_ref = [[
            0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4,
            4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 8, 8, 9, 10, 10,
            10, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 14,
            14, 14, 14, 15, 16, 16, 16, 16, 16, 16
        ],
                         [
                             44, 21, 40, 42, 1, 15, 36, 39, 54, 55, 60, 61, 14,
                             25, 28, 30, 35, 45, 0, 10, 26, 37, 38, 41, 48, 59,
                             62, 23, 31, 33, 53, 5, 12, 29, 49, 63, 64, 9, 3,
                             11, 43, 27, 34, 58, 52, 6, 9, 16, 19, 20, 22, 46,
                             50, 56, 57, 4, 17, 47, 51, 7, 8, 13, 14, 24, 2,
                             18, 32, 65, 66, 67
                         ]]
        levels_all_ref = [
            [
                '3C通訊', '人情交際', '休閒娛樂', '其他', '居家生活', '教育學習', '服飾美容', '汽機車',
                '理財投資', '繳稅', '規費', '費用', '運輸交通', '醫療保健', '長期不影響負債', '電子發票',
                '餐飲食品'
            ],
            [
                '3C用品', 'Netflix', '三餐+食材', '事業經營', '保險', '保養/化妝', '保養維修費',
                '借他人錢', '借出錢', '停車費', '傢俱', '儲蓄險', '內衣褲', '公司代墊', '其他',
                '出遊/拜訪親戚', '加油', '勞健保/國民年金', '午餐', '台鐵', '大眾運輸', '孝養父母', '客運',
                '影印', '悠遊卡', '慈善捐款', '房租', '手續費', '手續費/規費', '按摩保養', '換匯', '文具',
                '晚餐', '書籍雜誌', '會員費', '會員費/卡片押金', '玩具/小物', '瓦斯費', '生活用品', '福利金',
                '禮物/請客', '租屋押金', '紅白包', '綜合所得稅', '網路&電話費', '繳稅', '罰單', '藥物',
                '衛生用品', '衣裙褲襪外套', '計程車/租車', '診所/醫院', '轉帳費用', '進修課程', '運動',
                '運動健身', '郵資', '配件用品', '銀行手續費', '電信費', '電動/Netflix', '電影院/KTV',
                '電費', '鞋包配件', '頭髮相關', '食材與器材', '飲品', '點心零嘴'
            ]
        ]

        self.assertListEqual(codes_all, codes_all_ref)
        self.assertListEqual(levels_all, levels_all_ref)

    _compare_csv_files = _compare_csv_files

    def test_output_frequently_used_categories(self):
        file_name = 'frequent.csv'

        out_file = path.join(self._test_dir, self._out_dir, file_name)
        self._andro_money.output_frequently_used_categories(out_file)

        ref_file = path.join(self._test_dir, self._ref_dir, file_name)
        self._compare_csv_files(out_file, ref_file, 'utf_16')

    def test_output_all_categories(self):
        file_name = 'all.csv'

        out_file = path.join(self._test_dir, self._out_dir, file_name)
        self._andro_money.output_all_categories(out_file)

        ref_file = path.join(self._test_dir, self._ref_dir, file_name)
        self._compare_csv_files(out_file, ref_file, 'utf_16')


class TestReadAppend(unittest.TestCase):
    @freezegun.freeze_time('2019-05-20')
    @mock.patch('bill_to_csv.read_file')
    def setUp(self, read_file):
        self._test_dir = path.dirname(path.relpath(__file__))
        self._in_dir = 'inputs'
        self._out_dir = 'outputs'
        self._ref_dir = 'references'

        file_name = 'AndroMoney.csv'
        read_file.return_value = path.join(self._test_dir, self._in_dir,
                                           file_name)
        self._andro_money = bill_to_csv.AndroMoney(num_freq_categories=20, last_directory='')

    def _get_mock_transactions(self, file_name, read_file, getpass):
        read_file.return_value = path.join(self._test_dir, self._in_dir,
                                           file_name)

        dotenv.load_dotenv()
        getpass.return_value = os.environ.get('PASSWORD')

        mock_transactions = bill_to_csv.read_transactions(last_directory='')
        return mock_transactions

    @mock.patch('bill_to_csv.getpass.getpass')
    @mock.patch('bill_to_csv.read_file')
    def test_read_hsbc_transactions(self, read_file, getpass):
        file_name = 'eStatement_201911.pdf'
        transactions = self._get_mock_transactions(file_name, read_file,
                                                   getpass)
        transactions_ref = pd.Series([
            '3', '6', '13', '6', '300', '110', '199', '317', '367', '130',
            '177', '245', '660', '725', '199', '736', '10,976', '793', '77',
            '2,918', '145', '390', '245', '360', '60,000', '790', '3,192',
            '69', '670', '20,000', '300', '300', '83', '99', '321', '50', '60',
            '75', '136', '881', '370'
        ])

        ndarray = transactions.to_numpy()
        ndarray_ref = transactions_ref.to_numpy()
        self.assertTrue(np.array_equal(ndarray, ndarray_ref))

    @mock.patch('bill_to_csv.getpass.getpass')
    @mock.patch('bill_to_csv.read_file')
    def test_read_cathay_transactions(self, read_file, getpass):
        file_name = 'Download.csv'
        transactions = self._get_mock_transactions(file_name, read_file,
                                                   getpass)
        transactions_ref = pd.Series([
            '64', '62', '71', '86', '519', '1985', '57', '35', '10', '109',
            '81', '47', '39', '93', '4545', '64', '67', '99', '1573'
        ])

        ndarray = transactions.to_numpy()
        ndarray_ref = transactions_ref.to_numpy()
        self.assertTrue(np.array_equal(ndarray, ndarray_ref))

    def _get_mock_iterable_of_input(self, transactions_size):
        """Gets iterable for side effect of mock built-in function input.
        
        Args:
            transactions_size (pandas.Series.size): Number of transactions.
        
        Returns:
            An mock iterable containing paid date and category codes for each transaction.
        
        Raises:
            IndexError: Number of transactions is more than number of distinct category codes.
        """
        num_freq_categories = self._andro_money._num_freq_categories
        boundary_index = self._andro_money._boundary_index
        input_codes = [0] + list(range(1, num_freq_categories + 1)) + list(
            range(boundary_index + 1,
                  boundary_index + 1 + len(self._andro_money._codes_all[0])))

        if transactions_size > len(input_codes):
            raise IndexError(
                'Number of transactions is more than number of distinct category codes'
            )
        else:
            mock_iterable = ['20191231'] + input_codes[:transactions_size]

        return mock_iterable

    _compare_csv_files = _compare_csv_files

    def _test_append_transactions(self, transactions, ref_file_name):
        out_dir = path.join(self._test_dir, self._out_dir)
        self._andro_money.append(transactions, out_dir)

        out_file_name = 'AndroMoney.csv'
        out_file = path.join(out_dir, out_file_name)
        ref_file = path.join(self._test_dir, self._ref_dir, ref_file_name)
        self._compare_csv_files(out_file, ref_file, 'cp950')

    @mock.patch('bill_to_csv.input')
    @mock.patch('bill_to_csv.getpass.getpass')
    @mock.patch('bill_to_csv.read_file')
    def test_append_hsbc_transactions(self, read_file, getpass, mock_input):
        in_file_name = 'eStatement_201911.pdf'
        transactions = self._get_mock_transactions(in_file_name, read_file,
                                                   getpass)
        mock_input.side_effect = self._get_mock_iterable_of_input(
            transactions.size)

        self._test_append_transactions(transactions, 'AndroMoney_hsbc.csv')

    @mock.patch('bill_to_csv.input')
    @mock.patch('bill_to_csv.getpass.getpass')
    @mock.patch('bill_to_csv.read_file')
    def test_append_cathay_transactions(self, read_file, getpass, mock_input):
        in_file_name = 'Download.csv'
        transactions = self._get_mock_transactions(in_file_name, read_file,
                                                   getpass)
        mock_input.side_effect = self._get_mock_iterable_of_input(
            transactions.size)

        self._test_append_transactions(transactions, 'AndroMoney_cathay.csv')


if __name__ == '__main__':
    unittest.main()