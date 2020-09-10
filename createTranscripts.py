import pandas
import xlrd
wb = xlrd.open_workbook('index.xlsx')
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

for i in range(sheet.nrows):
    with open( str(i-1) + ".txt", 'w') as output_file:
        output_file.write(sheet.cell_value(i, 1))