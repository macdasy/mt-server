import pdfplumber
import re
import sys
import PyPDF2
import os
import Segregation


a = 0
file = sys.argv[1]
bank = sys.argv[5]
password = '' if sys.argv[2] == 'null' else str(sys.argv[2])
lang = 0 if sys.argv[4] == 'null' else int(sys.argv[4])

pdf_reader = PyPDF2.PdfReader(open(file, "rb"))

if pdf_reader.is_encrypted:
    pdf_reader.decrypt(password)
    pdf_writer = PyPDF2.PdfWriter()

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    decrypted_file_path = "decrypted_ "+sys.argv[3]+".pdf"
    pdf_writer.write(open(decrypted_file_path, "wb"))
    file = decrypted_file_path

entry_dict = {}
texts = []
final = []
invalid_running_bal = False
invalid_running_bal_index = 0

#  ----------- # ----------- With Breaker  ----------- #  ----------- #
# {'text': 'ACH/AIEPM2049R-AY2020-21/CE20125793409', 'x0': 143.75667040000002, 'x1': 284.9339024, 'top': 360.6293499999999, 'doctop': 360.6293499999999, 'bottom': 367.3793499999999, 'upright': True, 'direction': 1},

def extract_numbers(input_string):
    check = re.sub(r'[^0-9.]', '', input_string) 
    if check and len(check) > 0 and check[-1] is '.' :
            return check[:-1]
    
    else:
        return check


def with_breaker(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        tables = []

        for page in pdf.pages:
            table_data = []
            rows = page.extract_table()
            if rows:
                table_data.extend(rows)

            tables.extend(table_data)

        headers = [ value.lower() for value in tables[0] ]
        table_data = []
        print(headers)
        
        for row in tables[1:]:
            row_dict = {}
            for col, val in enumerate(row):
                if val == "":
                    row_dict[headers[col]] = None

                else:

                    try:
                        num = val
                        if val != None and '.' in val : 
                            num = float(val)
                        
                        row_dict[headers[col]] = str(num)

                    except ValueError:
                        pattern = re.compile(r'^\d+(\.\d*)?\n(?:[a-zA-Z]{0,2}|\d+)$')

                        if bool(pattern.match(val)):

                            if 'DR' in val:
                                temp = ((val.split('\n')[0]).replace('.','')).replace(',', '')

                                if temp.isnumeric():
                                    temp = val.split('\n')[0]
                                    row_dict[headers[col]] =  f"-{temp}"

                                else:
                                    row_dict[headers[col]] =  val.split('\n')[0]

                            elif len(val.split('\n')) > 1 and bool(extract_numbers(val.split('\n')[0])) and bool(extract_numbers(val.split('\n')[1])):
                                row_dict[headers[col]] =  ''.join( val.split('\n') )

                            else:
                                row_dict[headers[col]] =  val.split('\n')[0]
                            

                        else:
                            if '\n' in val:
                                row_dict[headers[col]] = ' '.join( val.split('\n') )
                            else: 
                                row_dict[headers[col]] = val

            table_data.append(row_dict)

        return table_data
    

#  ----------- # ----------- Without Breaker  ----------- #  ----------- #


from tabula.io import read_pdf
import math
from itertools import chain


def without_breaker(pdf_path):

    global invalid_running_bal
    global invalid_running_bal_index

    df = read_pdf(pdf_path, pages='all')
    raw_entries = {
        'columns': [],
        'data': []
    }

    for i in df:
        raw_entries['columns'].append( (i.to_dict(orient='split', index=False))['columns'] )
        raw_entries['data'].append( (i.to_dict(orient='split', index=False))['data'] )
    
    raw_entries['columns'] = raw_entries['columns'][1:]

    # combining all the lists into a single list
    all_data = list(chain.from_iterable(sublist + [r'%break%'] for sublist in raw_entries['data']))

    closing_balance = []

    current_data_index = 0

    for index, d in enumerate(all_data):

        # breaking after this occurs
        if d[1] == "STATEMENT SUMMARY :-": break

        # adding the first row to data if it's not a header (ex. Date, Desc, value)
        if len(raw_entries['columns']) > 0 and d == r'%break%':

            if ( '/' in raw_entries['columns'][0][0] ) or ( 'Unnamed' in raw_entries['columns'][0][0] ):
                all_data[index] = raw_entries['columns'][0]
                d = raw_entries['columns'][0]
                raw_entries['columns'].pop(0)

        # handling the broken description  
        if ( type(d[0]) is float and math.isnan(float(d[0])) ) or ( type(d[0]) is str and 'Unnamed' in d[0] ):
            final[current_data_index-1]['description'] = final[current_data_index-1]['description'] + str(d[1]) 
        
        else:
            if '/' in d[0]:
                # Unnamed: 0
                if ':' in str(d[4]): d[4] =  float('nan')
                if ':' in str(d[5]): d[5] =  float('nan')

                amount = str(d[4]).replace(',', '') if not math.isnan(float( str(d[4]).replace(',', '') )) else str(d[5]).replace(',', '')
                trans_type = 'DR' if not math.isnan(float( str(d[4]).replace(',', '') )) else 'CR'

                new_entry = {
                    'date': d[0],
                    'description': d[1],
                    'amount': amount,
                    'type': trans_type,
                }

                closing_balance.append(d[-1])

                if current_data_index != 0 and not invalid_running_bal_index:
                    
                    prev_balance = float(closing_balance[0].replace(',', ''))
                    curr_balance = float(d[-1].replace(',',''))
                    amount = float(amount.replace(',',''))

                    if type == 'DR':
                        if curr_balance == prev_balance - amount:
                            invalid_running_bal = True
                            invalid_running_bal_index = current_data_index

                    if type == 'CR':
                        if curr_balance == prev_balance + amount:
                            invalid_running_bal = True
                            invalid_running_bal_index = current_data_index

                final.append(new_entry)

                # keeping up for adding the broken desc
                current_data_index = current_data_index + 1
    
    return final

if bank == "HDFC":
    final = without_breaker(file)
    Segregation.segregate(final, lang, bank, invalid_running_bal_index, invalid_running_bal)

else:
    final = with_breaker(file)
    Segregation.segregate(final, lang, bank)

# final = with_breaker(file)

# Segregation.segregate(final, lang, bank)

os.remove(file)
