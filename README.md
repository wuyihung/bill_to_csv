### Purpose
Parse following credit card bills and append parsed data to [AndroMoney](https://web.andromoney.com) CSV  file:
1. HSBC PDF file;
1. Cathay United Bank CSV file.
### Inputs
User puts PDF file and to-be-appended CSV file in the directory `../inputs/`.
### Outputs
`./outputs/` is the directory of the following outputs:
1. `frequent.csv` lists the codes of the frequently used categories.
1. `all.csv` lists the codes of all the categories.
1. `AndroMoney.csv` is the appended file and can be updated to AndroMoney application.
