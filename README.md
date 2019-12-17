## Purpose
Parses specific credit card bills and appends parsed transactions to [AndroMoney](https://web.andromoney.com) CSV file. Supported bills are:
1. HSBC Bank (Taiwan) PDF file and
1. Cathay United Bank CSV file.
## Getting started
1. Run module:
    ```
    python bill_to_csv.py
    ```
1. In first dialog, select `AndroMoney.csv` to be appended.
1. In second dialog, select either `eStatement_*.pdf` of HSBC bill or `Download.csv` of Cathay bill.
1. Follow instructions shown on screen.
1. When keying in codes of transactions, refer to generated files `./output/frequent.csv` or `./output/all.csv`, which are codes of most frequently used categories or codes of all categories, respectively.
1. `./output/AndroMoney.csv` is then generated and can be loaded to update mobile application of AndroMoney.
