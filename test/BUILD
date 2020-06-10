py_test(
    name = "test",
    srcs = ["test.py"],
    data = [
        ".env",
        "inputs/AndroMoney.csv",
        "inputs/Download.csv",
        "inputs/eStatement_201911.pdf",
        "inputs/eStatement_202004.pdf",
        "references/AndroMoney_cathay.csv",
        "references/AndroMoney_hsbc.csv",
        "references/all.csv",
        "references/frequent.csv",
        "references/hsbc_2_pages_transactions.csv",
    ],
    deps = ["//:bill_to_csv_lib"],
)
