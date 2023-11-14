import pdfplumber, re, json, sys, PyPDF2
import os
import Segregation

a = 0
file = sys.argv[1]
password = '' if sys.argv[2] == 'null' else str(sys.argv[2])
threshold = '' if sys.argv[4] == 'null' else str(sys.argv[4])


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

#  ----------- # ----------- With Breaker  ----------- #  ----------- #

def with_breaker(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:
        tables = []

        for page in pdf.pages:
            table_data = []
            rows = page.extract_table()
            if rows:
                table_data.extend(rows)

            tables.extend(table_data)

        headers = tables[0]
        table_data = []
        for row in tables[1:]:
            row_dict = {}
            for col, val in enumerate(row):
                if val == "":
                    row_dict[headers[col]] = None
                else:
                    row_dict[headers[col]] = val
            table_data.append(row_dict)

        return table_data
    

#  ----------- # ----------- Without Breaker  ----------- #  ----------- #


def returnValue(value, p_no):  
        global texts
        
        p = pdf.pages[p_no]
        raw_text1 = p.extract_words()
        rvalue = [item for item in raw_text1 if item.get('text') == value]

        if(len(rvalue) > 1):
            
            if len(texts) == 0 and value not in texts:
                texts.append(value)
                
            elif len(texts) != 0 and value in texts:
                texts.append(value)

            elif len(texts) !=0 and value not in texts:
                texts = []
                texts.append(value)

            return [rvalue[len(texts)-1]]
        
        elif rvalue != []:
                texts = []
                return [item for item in raw_text1 if item.get('text') == value]


with pdfplumber.open(file) as pdf:
    for page_num in range(len(pdf.pages)):
        # print(page_num)
    
        page = pdf.pages[page_num]
        text = page.extract_text()
        raw_text = page.extract_words()

        new_line = re.compile(r"(\b\d{2}/\d{2}/\d{2}\b) ([a-zA-Z0-9\-@#*/.]+)\s+([a-zA-Z0-9]+)\s+(\b\d{2}/\d{2}/\d{2}\b) (?:(\s |[\d,]+\.\d{2})) ?(?:(\s |[\d,]+\.\d{2}))?\s([\d,]+\.\d{2})")
        second_line = re.compile(r"([a-zA-Z0-9\-@#*/.]+)")
        decimal = re.compile("[\d,]+\.\d{2}")

        combined_text = ''
        condition_met = False
        line_num  = 0

        for line in text.split('\n'):

            if not condition_met:
                condition_met = new_line.match(line)

            if(condition_met):
                if not (decimal.match(line.split(' ')[-1])):
                        line_num+=1
                        cod1 = bool(re.search(r"\s", line))
                        if not cod1:
                            combined_text += f' {line}'
                
                else:
                        if new_line.match(line):
                            combined_text += f'\n{line}'
                    
        found = None
        for line in combined_text.split('\n') :
            trimmed = line.split(' ')[:7]

            if(len(trimmed) > 1):
                
                entry = trimmed
                entry_dict['Date'] = entry[0]
                entry_dict['Description'] = entry[1] + entry[-1] if len(entry) == 7 else entry[1]

                found = returnValue(entry[4], page_num)
                pos = found[0]['x1']
                text = found[0]['text']
                entry_dict['Amount'] = text.replace(",", "")
                
                if pos == 548.187: entry_dict['Type'] = 'CR'
                elif pos == 470.235: entry_dict['Type'] = 'DR'

                entry_dict['Closing Balance'] = entry[5].replace(",", "")

                final.append(entry_dict.copy())

if (json.dumps(final) == '[]'):
    final = with_breaker(file)

print(Segregation.segregate(final, threshold))
os.remove(file)