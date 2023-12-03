import re
import PDFGeneration
from collections import defaultdict
import math
# from translate import Translator

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

def charge_checker(input_string):
    charge_keyword = ['CHARGES', 'CHG', 'BG CHARGES', 'CHRGS', 'FEE','MISC', 'MISC-REMIT', 'BULK']
    
    for substring in charge_keyword:
        pattern = re.compile(rf'(?<![a-zA-Z]){re.escape(substring)}(?![a-zA-Z])', re.IGNORECASE)
        if pattern.search(input_string):
            return substring
        
    return None

keywords = ['ACHDr', 'tax', 'ibrtgs', 'ACCOUNT', 'neft', 'upi', 'imps', 'chq', 'rtgs', 'coll', 
            'vps', 'transfer', 'paytm', 'transferee', 'to', 'from', 'by', 'depo', 'clearing', 
            'withdrawal', 'NEWCARDISSUE', 'impbill', 'trf', 'payment', 'chrgs', 'remit', 'bank', 
            'ecom', 'pos', 'apbs', 'chg', 'cash', 'cheque', 'dd', 'eft', 'swift', 'web', 
            'net', 'liq', 'mobile', 'tfr', 'wdl', 'dep', 'deposit', 'tds', 'grant', 'emi', 
            'inst', 'installment', 'int', 'interest', 'pf', 'pension', 'deposit', 'closure', 'rgts',
            'terminated', 'ins', 'insurance', 'refund', 'advtax', 'advancetax', 'bill', 'CHARGES', 'CHARGE',
            'credit', 'debit', 'CHG', 'BG CHARGES', 'FEE','MISC', 'MISC-REMIT', 'BULK', 'neftcr', ]
keyword_list = '|'.join(keywords)
key_pattern = re.compile(r'\b(?:' + keyword_list + r')\b', flags=re.IGNORECASE)


deduct_keywords = ['INS', 'INSURANCE', 'LIFE', 'HEALTH', 'PROVI', 'FUND', 'PF', 'SCHL', 'SCHOOL', 'CLG', 
                   'COLLEGE', 'UNIVERSITY', 'EDUCATIONAL INSTITUTE', 'EDU INST', 'STAMP DUTY', 'REGISTRATION FEES',
                    'STAMP', 'REGISTRAR OFFICE', 'PENSION', 'MONEY', 'MUTUAL', 'FUND', 'ASSET', 'FINAN', 'LIFE', 
                    'MEDI', 'HOSP', 'HOSPITAL', 'CHECKUP', 'BODYCHECKUP', 'SCAN', 'INT', 'EDU', 'FINAN', 'INSTITU', 
                    'CHARITAB', 'DONATION', 'DONA', 'TRUST', 'HOME', 'RENT', 'INT', 'HOUSE LOAN', 'INTEREST', 'INTREST', 
                    'ELECTRIC', 'VEHICLE', 'POLITICAL', 'PARTY']

deduct_dict = {
    '80c': ['INS', 'INSURANCE', 'LIFE', 'HEALTH', 'PROVI', 'FUND', 'PF', 'SCHL', 'SCHOOL', 'CLG','COLLEGE', 
            'UNIVERSITY', 'EDUCATIONAL INSTITUTE', 'EDU INST', 'STAMP DUTY', 'REGISTRATION FEES', 'STAMP', 
            'REGISTRAR OFFICE'],
    '80ccc': [ 'PENSION' ],
    '80ccg': [  'MONEY', 'MUTUAL', 'FUND', 'ASSET', 'FINAN', 'LIFE' ],
    '80d/80dd': ['MEDI', 'HOSP', 'HOSPITAL', 'CHECKUP', 'BODYCHECKUP', 'SCAN'],
    '80ee': [ 'INT', 'EDU', 'FINAN', 'INSTITU', 'CHARITAB', 'INT', 'HOUSE LOAN', 'INTEREST', 'INTREST' ],
    '80g': [ 'DONATION', 'DONA', 'TRUST', 'HOME', 'RENT' ],
    '80eeb': [ 'ELECTRIC', 'VEHICLE' ],
    '80ggb': [  'POLITICAL', 'PARTY' ]
}


deduct_keyword_list = '|'.join(deduct_keywords)
deduct_key_pattern = re.compile(
    r'\b(?:' + deduct_keyword_list + r')\b', flags=re.IGNORECASE)

isDate = ''


def find_float(obj):
    index = 0
    for key, value in obj.items():

        if '.' in value:
            try:
                float_value = float(value.replace(',', ''))

                if index != 0 and isinstance(float_value, float):
                    return index
                
            except ValueError:
                pass

        index += 1
    return index


def segregate(data, current_lang, bank, invalid_running_bal_index=0, invalid_running_bal=False):
    result = []
    attr_desc = []
    charges = []
    m_o_p = {}
    high_value_transaction = {
        'inflow': [],
        'outflow': []
    }

    hvt_list = []
    grouped_transactions = {}
    final = []
    table_headings = []
    attr_result = []

    tds = []
    grant = []
    deduction = []
    tax_refund = []
    ad_tax = []
    emi_list = []
    closure_list = []
    interest_list = []

    lang_heading = {
        0: [
            ['Date', 'Decription', 'Amount', 'Type'],
            ['Particular', 'Count', 'Amount INFLOW', 'Amount OUTFLOW'],
            ['Date', 'Decription', 'Amount INFLOW', 'Amount OUTFLOW'],
            ['Date', 'Decription', 'Amount', 'Type'],
            ['Date', 'Decription', 'Amount', 'Type'],
            ['Description', 'Debit', 'Credit'],
            ['Date', 'Decription', 'Amount'],
            ['Date', 'Decription', 'Amount', 'Section'],
            ['Date', 'Decription', 'OUT', 'IN'],
        ],

        1: [
            ['தேதி', 'விளக்கம்', 'தொகை', 'வகை'],
            ['விளக்கம்', 'எண்ணிக்கை', 'வரவுத்தொகை', 'செலவுத்தொகை'],
            ['தேதி', 'விளக்கம்', 'வரவுத்தொகை', 'செலவுத்தொகை'],
            ['தேதி', 'விளக்கம்', 'தொகை', 'வகை'],
            ['தேதி', 'விளக்கம்', 'தொகை', 'வகை'],
            ['விளக்கம்', 'செலவு', 'வரவு']
        ],

        2: [
            ['തീയതി', 'വിവരണം', 'തുക', 'തരം'],
            ['വിവരണം', 'എണ്ണുക', 'തുകയുടെ വരവ്', 'തുക പുറത്തേക്ക് ഒഴുകുന്നു'],
            ['തീയതി', 'വിവരണം', 'തുകയുടെ വരവ്', 'തുക പുറത്തേക്ക് ഒഴുകുന്നു'],
            ['തീയതി', 'വിവരണം', 'തുക', 'തരം'],
            ['തീയതി', 'വിവരണം', 'തുക', 'തരം'],
            ['വിവരണം', 'ഡെബിറ്റ്', 'കടപ്പാട്']
        ],

        3: [
            ['తేదీ', 'వివరణ', 'మొత్తం', 'రకము'],
            ['వివరణ', 'లెక్కించు', 'ఇన్‌ఫ్లో మొత్తం', 'అవుట్‌ఫ్లో మొత్తం'],
            ['తేదీ', 'వివరణ', 'ఇన్‌ఫ్లో మొత్తం', 'అవుట్‌ఫ్లో మొత్తం'],
            ['తేదీ', 'వివరణ', 'మొత్తం', 'రకము'],
            ['తేదీ', 'వివరణ', 'మొత్తం', 'రకము'],
            ['వివరణ', 'డెబిట్', 'క్రెడిట్']
        ],

        4: [
            ['तारीख', 'विवरण', 'मात्रा', 'प्रकार'],
            ['विवरण', 'गणना', 'राशि का प्रवाह', 'राशि का बहिर्प्रवाह'],
            ['तारीख', 'विवरण', 'राशि का प्रवाह', 'राशि का बहिर्प्रवाह'],
            ['तारीख', 'विवरण', 'मात्रा', 'प्रकार'],
            ['तारीख', 'विवरण', 'मात्रा', 'प्रकार'],
            ['विवरण', 'नामे', 'श्रेय']
        ],
    }

    outflow_labels = []
    inflow_labels = []

    total_income = [0, 0]
    total_outcome = [0, 0]
    table_lang_head = lang_heading[current_lang]

    new_list = []
    for input_dict in data:
        renewed = {key.upper(): '-' if value == None else value for key, value in input_dict.items()}
        new_list.append(renewed)


    data = new_list
    sub_total_len = len(data)

    for key, raw in enumerate(data):

        num_index = find_float(raw)
        check_index = num_index + 1

        charge_or_mod = False


        isDate = raw[list(raw.keys())[0]] if len(raw[list(raw.keys())[0]]) > 6 else raw[list(raw.keys())[1]]

        date = (isDate.split('\n')[0] if len(isDate.split('\n')[1]) > 4 else isDate.replace('\n', '')) if len(isDate.split('\n')) > 1 else isDate
        alpha_pattern = re.compile(r'\d+')

        if len(date) > 2 and bool(alpha_pattern.search(date)):

            desc = r"" + (raw.get('PARTICULARS') or raw.get('DESCRIPTION') or raw.get('DETAILS')
                          or raw.get('NARRATION')).replace('\n', '')

            transc_type = raw.get('TYPE') or ('CR' if len(raw) - 1 == check_index
                                              else ('DR' if raw[list(raw.keys())[check_index]] == '-' else 'CR'))

            transc_type = 'DR' if transc_type == 'Debit' else 'CR' if transc_type == 'Credit' else transc_type

            amount = (raw.get('AMOUNT') or raw[list(raw.keys())[num_index]]).replace(',', '')

            balance = [raw[key] for key in raw.keys() if 'BALANCE' in key]
            # print(balance)

            entry = {
                'DATE': date,
                'DESCRIPTION': desc,
                'AMOUNT': amount,
                'TYPE': transc_type,
                'BALANCE' : balance
            }

            pattern = re.compile(r'(?=.*[a-zA-Z]{3,})(?=.*\d{3,})[a-zA-Z\d.]+@[a-zA-Z]{3,}')
            match = re.findall(pattern, desc)

            if 'ATM' in desc:
                if transc_type == 'DR':
                    attr_desc.append( 'ATM WITHDRAWAL' )
                else:
                    attr_desc.append( 'ATM DEPOSIT' )

            elif match == []:
                pattern = re.compile(r"\b[a-zA-Z@\s]{6,}\d*\b")
                match = re.findall(pattern, desc)
            
            if len(match) > 0:
                if 'WITHDRAWAL TRANSFER' in match[0]:
                    print(True, 0)
                    match[0] = match[0].replace('WITHDRAWAL TRANSFER', '')
                
                elif 'WITHDRAWALTRANSFER' in match[0]: 
                    print(True, 1)
                    match[0] = match[0].replace('WITHDRAWALTRANSFER', '')
                
                for string in match:
                    pattern_result = key_pattern.search(string)
                    if not bool(pattern_result):
                        attr_desc.append(string)

            if attr_desc:
                new_attr_entry = {
                    'DATE': date,
                    'DESCRIPTION': str(attr_desc[0]),
                    'AMOUNT': amount,
                    'TYPE': transc_type
                }

                if (len(date) > 1) and (len(str(attr_desc[0])) > 1) and (len(amount) > 1) and (len(transc_type) > 1):
                    attr_result.append(new_attr_entry)

            else:
                # if none returned
                pass

            attr_desc.clear()

            if (len(date) > 1) and (len(desc) > 1) and (len(amount) > 1) and (len(transc_type) > 1):
                result.append(entry)

            temp_desc = desc.upper()

            # Totals
            if transc_type == 'CR':
                total_income[0] += float(amount)
                total_income[1] += 1

            if transc_type == 'DR':
                total_outcome[0] += float(amount)
                total_outcome[1] += 1

            charg_result = charge_checker(temp_desc) 
            if bool(charg_result):
                charges.append(entry)
                charge_or_mod = True

            mode = None
            if re.search(r'UPI.*?(?=\s|$)', temp_desc):
                mode = 'UPI'
            elif re.search(r'IMPS.*?(?=\s|$)', temp_desc):
                mode = 'IMPS'
            elif re.search(r'NEFT.*?(?=\s|$)', temp_desc):
                mode = 'NEFT'
            elif re.search(r'CHQ.*?(?=\s|$)', temp_desc):
                mode = 'CHQ'
            elif re.search(r'RTGS.*?(?=\s|$)', temp_desc) or re.search(r'RTG.*?(?=\s|$)', temp_desc):
                mode = 'RTGS'
            elif re.search(r'WDL.*?(?=\s|$)', temp_desc) or re.search(r'CASH WDL.*?(?=\s|$)', temp_desc) or re.search(r'ATM WDL.*?(?=\s|$)', temp_desc):
                mode = 'CASH WITHDRAWAL'
            elif re.search(r'Cash DEP.*?(?=\s|$)', temp_desc) or re.search(r'CDM DEP.*?(?=\s|$)', temp_desc) or re.search(r'CCM DEP.*?(?=\s|$)', temp_desc) or re.search(r'CMS DEP.*?(?=\s|$)', temp_desc):
                mode = 'CASH DEPOSIT'

            if mode and mode not in m_o_p:
                m_o_p[mode] = []

            if mode:
                m_o_p[mode].append(entry)
                charge_or_mod = True

            sub_entry = [entry['DATE'], entry['DESCRIPTION'],  entry['AMOUNT']]
            
            deduct_section = ''
            ded_pattern_result = deduct_key_pattern.search(temp_desc)
            if bool(ded_pattern_result) and transc_type == 'DR':
                
                if deduct_section == '':
                    for k in deduct_dict:
                        if  ded_pattern_result.group(0) in deduct_dict[k]:
                            deduct_section = k
                            break
                
                ded_entry = [entry['DATE'], entry['DESCRIPTION'],  entry['AMOUNT'], deduct_section]
                deduction.append(ded_entry)


            if not charge_or_mod:
                # TDS
                if 'TDS' in temp_desc:
                    
                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        tds.append(sub_entry)

                elif 'GRANT' in temp_desc:
                    
                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        grant.append(sub_entry)

                elif 'REFUND' in temp_desc or 'TAXDEPARTMENT' in temp_desc:

                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        tax_refund.append(sub_entry)

                elif 'ADVTAX' in temp_desc or 'ADVANCETAX' in temp_desc or 'PAID' in temp_desc or 'ADVANCETAX' in temp_desc:
                    
                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        ad_tax.append(sub_entry)

                elif 'EMI' in temp_desc or 'INST' in temp_desc or 'INSTALLMENT' in temp_desc or 'INSTALMENT' in temp_desc:

                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        emi_list.append(sub_entry)

                elif 'PF CLOSURE' in temp_desc or 'PENSION CLOSURE' in temp_desc or 'DEPOSIT CLOSURE' in temp_desc or 'CLOSURE' in temp_desc or 'TERMINATED' in temp_desc:

                    if entry not in list(m_o_p.values())[0] and entry not in charges:  
                        closure_list.append(sub_entry)

                elif 'INT' in temp_desc or 'INTEREST' in temp_desc or 'INT RECEIVED' in temp_desc or 'INTEREST RECEIVED' in temp_desc:
                    new_interest = [entry['DATE'], desc, entry['AMOUNT'] if entry['TYPE'] == 'DR' else 0,
                                    entry['AMOUNT'] if entry['TYPE'] == 'CR' else 0]

                    interest_list.append(new_interest)

            if ((key+1) == len(data)):
                threshold = (max(float(total_income[0]) , float(total_outcome[0])) * 15) / 100

                gross_outcome = total_outcome[0] * 85 / 100
                gross_income = total_income[0] * 85 / 100

                # High Value Transaction
                if (float(amount) > float(threshold)) and float(threshold) > 0:
                    # if transc_type == 'CR': high_value_transaction['inflow'].append(sub_entry)
                    # elif transc_type == 'DR': high_value_transaction['outflow'].append(sub_entry)

                    new_hvt = [date, desc, amount if transc_type == 'CR' else '-', amount if transc_type == 'DR' else '-']
                    hvt_list.append(new_hvt)

        else:
            sub_total_len = sub_total_len - 1

            if (key) == sub_total_len or (key-1) == sub_total_len:
                threshold = (max(float(total_income[0]) , float(total_outcome[0])) * 15) / 100

                gross_outcome = total_outcome[0] * 85 / 100
                gross_income = total_income[0] * 85 / 100

                # High Value Transaction
                if (float(amount) > float(threshold)) and float(threshold) > 0:
                    # if transc_type == 'CR': high_value_transaction['inflow'].append(sub_entry)
                    # elif transc_type == 'DR': high_value_transaction['outflow'].append(sub_entry)

                    new_hvt = [date, desc, amount if transc_type == 'CR' else '-', amount if transc_type == 'DR' else '-']
                    hvt_list.append(new_hvt)

    
    # Unusual Transaction
    date = ''
    desc_amount_type = {}
    first_date_value = dict

    unsual_list = []
    duplicate_list = []

    for d in attr_result:
        current_date = d['DATE']
        current_desc = d['DESCRIPTION']
        current_amount = d['AMOUNT']
        current_type = d['TYPE']

        dr_threshold_amount = 0
        dr_threshold_item = []

        combined_text = str(current_desc) + "/" + str(current_amount)

        if current_date != date:

            desc_amount_type.clear()
            date = current_date
            desc_amount_type[combined_text] = current_type

            first_date_value = d  # keeping the first value for adding it later =>

        else:

            if combined_text in desc_amount_type.keys():

                if desc_amount_type[combined_text] != current_type:

                    # adding the first value after checking <=
                    if first_date_value not in unsual_list:
                        unsual_list.append(first_date_value)

                    # avoiding duplicate values.
                    if d not in unsual_list:
                        unsual_list.append(d)

                else:
                    desc_amount_type[combined_text] = current_type

                    if len(duplicate_list) == 0 : duplicate_list.append(d)

                    duplicate_list.append(d)

                    
                    if desc_amount_type[combined_text] == 'DR':
                        dr_threshold_amount = float(dr_threshold_amount) + float(current_amount)
                        dr_threshold_item.append(d)

                        if dr_threshold_amount > threshold:
                            new_hvt = [ current_date, current_desc, '-' , curr_amount ]
                            hvt_list.extend(dr_threshold_item)


            # checking for new payee under the same date
            else:
                desc_amount_type[combined_text] = current_type
                first_date_value = d
                dr_threshold_amount = 0
                dr_threshold_item = []

    # Bank Charges
    charge_list = [list(obj.values())[:-1] + ['Bank Charges'] for obj in charges]

    total_charges_amount_list = [ float(sublist[2].replace(',',''))  for sublist in charge_list]
    charges_total =  [ ' ', 'Total', round(sum(total_charges_amount_list), 2), ' ', ' ']

    # charge_header = ['Date', 'Decription', 'Amount', 'Type']
    charge_header = table_lang_head[0]

    if len(charge_list) > 0:
        charge_list.append(charges_total)
        charge_list.insert(0, charge_header)
        final.append(charge_list)
        table_headings.append('Bank Charges Analysis')
    else:
        charge_list.append(['-', '- ', '- ', '-'])
        charge_list.insert(0, charge_header)
        final.append(charge_list)
        table_headings.append('Bank Charges Analysis')

    # Mode Of Payment
    mode_list = []
    for key, value in m_o_p.items():
        d_imps = sum(float(obj['AMOUNT'].replace(
            ',', '')) for obj in value if obj['TYPE'] == 'DR' and float(obj['AMOUNT'].replace(',', '')) > 0)
        c_imps = sum(float(obj['AMOUNT'].replace(
            ',', '')) for obj in value if obj['TYPE'] == 'CR' and float(obj['AMOUNT'].replace(',', '')) > 0)
        mode_list.append([key, str(len(value)), '{:.2f}'.format(
            d_imps), '{:.2f}'.format(c_imps)])

    # mode_header = ['Particular', 'Count', 'Amount INFLOW' , 'Amount OUTFLOW']
    mode_header = table_lang_head[1]
    if len(mode_list) > 0:
        mode_list.insert(0, mode_header)
        final.append(mode_list)
        table_headings.append('UPI - MODE OF PAYMENT\n(STATUS COUNT)')
    else:
        mode_list.append(['-', '- ', '- '])
        mode_list.insert(0, mode_header)
        final.append(mode_list)
        table_headings.append('UPI - MODE OF PAYMENT\n(STATUS COUNT)')

    # High Value Transaction
    hvt_header = table_lang_head[2]
    # hvt_header = ['Date', 'Decription', 'Amount INFLOW' , 'Amount OUTFLOW']
    if len(hvt_list) > 0:
        hvt_list.insert(0, hvt_header)
        final.append(hvt_list)
        table_headings.append(
            f"High Value Transactions")
    else:
        hvt_list.append(['-', '-', '-', '-'])
        hvt_list.insert(0, hvt_header)
        final.append(hvt_list)
        table_headings.append(
            f"High Value Transactions")

    # Unusual Transactions
    unusual_trans_list = [list(my_dict.values()) for my_dict in unsual_list]
    unusual_header = table_lang_head[3]
    # unusual_header = ['Date', 'Decription', 'Amount', 'Type']
    if len(unusual_trans_list) > 0:
        unusual_trans_list.insert(0, unusual_header)
        final.append(unusual_trans_list)
        table_headings.append('Unusual Transactions')

    else:
        unusual_trans_list.append([' -', '- ', '- ', '-'])
        unusual_trans_list.insert(0, unusual_header)
        final.append(unusual_trans_list)
        table_headings.append('Unusual Transactions')

    duplicates = [list(my_dict.values()) for my_dict in duplicate_list]
    dup_header = table_lang_head[4]
    # dup_header = ['Date', 'Decription', 'Amount', 'Type']

    if len(duplicates) > 0:
        duplicates.insert(0, dup_header)
        final.append(duplicates)
        table_headings.append(f'Duplicate Transactions')

    else:
        duplicates.append([' -', '- ', '- ', '-'])
        duplicates.insert(0, dup_header)
        final.append(duplicates)
        table_headings.append(f'Duplicate Transactions')


    # Attribute Classification & Month Wise Data
    description_stats = {}
    limit = 3
    month_data = {}
    graph_months = []

    graph_dates = []
    date_data = {}

    min_amount = 0
    max_amount = 0
    graph_dots = []
    govt_list = []
    final_line_data = []

    for my_dict in attr_result:

        # --------------- Attr. Classftn. --------------- #
        description_value = my_dict['DESCRIPTION']
        amount_value = float(my_dict['AMOUNT'].replace(',', ''))
        transaction_type = my_dict['TYPE']

        # Initialize count and sum if the 'Description' is not seen before
        if description_value not in description_stats:
            description_stats[description_value] = {
                'Desc': description_value, 'DR': 0, 'CR': 0, 'count': 0}

        # Update count and sum for the 'Description' and type
        description_stats[description_value][transaction_type] = round(
            amount_value, 2) + round(description_stats[description_value][transaction_type])
        description_stats[description_value]['count'] += 1


        # --------------- Month Wise Data --------------- #
        present_date = list(my_dict.values())[0]

        seperator = '-' if '-' in present_date else ' ' if ' ' in present_date else '/'

        if bool(re.search('[a-zA-Z]', present_date)) and (present_date.split(seperator)[1].isalpha() or present_date.split(seperator)[1].isalpha()):
            month_key = present_date.split(seperator)[1] + f" '{ present_date.split(seperator)[-1][-2:] }"

            date_key = present_date.split(seperator)[0] + '\n' + present_date.split(seperator)[1]

        else:
            present_date = present_date.split(',') if ',' in present_date else present_date.split(
                '-') if '-' in present_date else present_date.split('/')

            
            if present_date[1].isnumeric():
                month_key = MONTHS[int(present_date[1]) - 1][:3] + \
                    f" '{ present_date[-1][-2:] }"
                
                date_key = present_date[0] + '\n' + MONTHS[int(present_date[1]) - 1][:3]

            else:
                month_key = present_date[1] + f" '{ present_date[-1][-2:] }"
                date_key = present_date.split(seperator)[0] + '\n' + MONTHS[int(present_date[1]) - 1][:3]

        if month_key not in graph_months:
            graph_months.append(month_key)

        if month_key not in month_data:
            month_data[month_key] = {'Month': month_key, 'DR': 0, 'CR': 0}

        month_data[month_key][transaction_type] += amount_value


        if date_key not in graph_dates:
            graph_dates.append(date_key)

        if date_key not in date_data:
            date_data[date_key] = {'Date': date_key, 'DR':0, 'CR': 0}
        
        date_data[date_key][transaction_type] += amount_value


        if min_amount != 0:
            min_amount = amount_value if amount_value < min_amount else min_amount

        max_amount = amount_value if amount_value > max_amount else max_amount


        if my_dict['TYPE'] == 'Debit':
            graph_dots.append((0, amount_value))

        if my_dict['TYPE'] == 'Credit':
            graph_dots.append((amount_value, 0))


    if len(graph_months) > 1:
        final_line_data = [month_data, graph_months]

    else:
        final_line_data = [date_data, graph_dates]


    attributes_list = [list(my_dict.values())[:-1] for my_dict in description_stats.values() if my_dict['count']]

    chart_data = []
    attr_header = table_lang_head[5]

    # attr_header = ['Description', 'Debit', 'Credit']
    if len(attributes_list) > 0:

        attr_outflow_list = [sublist[-2] for sublist in attributes_list]
        attr_inflow_list = [sublist[-1] for sublist in attributes_list]

        debit_sorted = sorted(attributes_list[1:], key=lambda x: x[1], reverse=True)
        credit_sorted = sorted(attributes_list[1:], key=lambda x: x[2], reverse=True)

        # attributes_list.insert(0, attr_header)
        # final.append(attributes_list)

        new_attr_outflow_list =[]
        debit_tracker = 0
        debit_count = 0
        
        new_attr_inflow_list =[]
        credit_tracker = 0
        credit_count = 0

        for li in debit_sorted:
            debit_value = float(li[1])
            debit_tracker += debit_value

            if debit_tracker < float(gross_outcome):
                new_attr_outflow_list.append(debit_value) 
                debit_count += 1

            elif debit_tracker > float(gross_outcome) and debit_tracker - debit_value == 0:
                new_attr_outflow_list.extend( [sublist[-2] for sublist in debit_sorted[:5]] )
                debit_count = 5
                gross_outcome = total_outcome[0]
                break

        for li in credit_sorted:
            credit_value = float(li[-1])
            credit_tracker += credit_value

            if credit_tracker < float(gross_income):
                new_attr_inflow_list.append(credit_value) 
                credit_count += 1

            elif credit_tracker > float(gross_income) and ((credit_tracker - credit_value) == 0):
                new_attr_inflow_list.extend( [sublist[-1] for sublist in credit_sorted[:5]] )
                credit_count = 5
                gross_income = total_income[0]
                break

        outflow_labels = [ d[:2] for d in debit_sorted] [:debit_count]
        inflow_labels = [ [d[0], d[2]] for d in credit_sorted] [:credit_count]


        debit_sorted.insert(0, attr_header)
        final.append(debit_sorted)
        
        if (len(new_attr_outflow_list) > 0):
            new_attr_outflow_list.insert(0, 'Debit')
            
            if len( new_attr_outflow_list ) > 11 : 
                chart_data.append(new_attr_outflow_list[:11])
                outflow_labels = outflow_labels[:10]
                
            else: chart_data.append(new_attr_outflow_list)

        if (len(new_attr_inflow_list) > 0):
            new_attr_inflow_list.insert(0, 'Credit')
            
            if len( new_attr_inflow_list ) > 11: 
                chart_data.append(new_attr_inflow_list[:11])
                inflow_labels = inflow_labels[:10]

            else: chart_data.append(new_attr_inflow_list)
            
        # Old pie chart data
        # if (len(attr_outflow_list) > 0):
        #     chart_data.append(attr_outflow_list)
        # if (len(attr_inflow_list) > 0):
        #     chart_data.append(attr_inflow_list)

    else:
        attributes_list.append(['-', '-', '-'])
        attributes_list.insert(0, attr_header)
        final.append(attributes_list)
    table_headings.append(f'Attribute Classification')

    # TDS
    govt_heading = lang_heading[current_lang][6]
    if len(tds) > 0:
        tds.insert(0, govt_heading)
        govt_list.append(tds)

    else:
        tds.append(['-', '-', '-'])
        tds.insert(0, govt_heading)
        govt_list.append(tds)
    table_headings.append(f'List of TDS detucted')
    # print(tds)

    if len(grant) > 0:
        grant.insert(0, govt_heading)
        govt_list.append(grant)

    else:
        grant.append(['-', '-', '-'])
        grant.insert(0, govt_heading)
        govt_list.append(grant)
    table_headings.append(f'Recepit of Government Grant')
    # print(grant)

    if len(deduction) > 0:
        deduction.insert(0, lang_heading[current_lang][7])
        govt_list.append(deduction)

    else:
        deduction.append(['-', '-', '-'])
        deduction.insert(0, lang_heading[current_lang][7])
        govt_list.append(deduction)
    table_headings.append(f'Deduction')

    if len(tax_refund) > 0:
        tax_refund.insert(0, govt_heading)
        govt_list.append(tax_refund)

    else:
        tax_refund.append(['-', '-', '-'])
        tax_refund.insert(0, govt_heading)
        govt_list.append(tax_refund)
    table_headings.append(f'Tax Refund')
    # print(tax_refund)

    if len(ad_tax) > 0:
        ad_tax.insert(0, govt_heading)
        govt_list.append(ad_tax)

    else:
        ad_tax.append(['-', '-', '-'])
        ad_tax.insert(0, govt_heading)
        govt_list.append(ad_tax)
    table_headings.append(f'Advance tax')
    # print(ad_tax)

    if len(emi_list) > 0:
        emi_list.insert(0, govt_heading)
        govt_list.append(emi_list)

    else:
        emi_list.append(['-', '-', '-'])
        emi_list.insert(0, govt_heading)
        govt_list.append(emi_list)
    table_headings.append(f'EMI')
    # print(emi_list)

    if len(closure_list) > 0:
        closure_list.insert(0, govt_heading)
        govt_list.append(closure_list)

    else:
        closure_list.append(['-', '-', '-'])
        closure_list.insert(0, govt_heading)
        govt_list.append(closure_list)
    table_headings.append(f'Closure')
    # print(closure_list)

    govt_heading = lang_heading[current_lang][8]

    if len(interest_list) > 0:
        interest_list.insert(0, govt_heading)
        govt_list.append(interest_list)

    else:
        interest_list.append(['-', '-', '-'])
        interest_list.insert(0, govt_heading)
        govt_list.append(interest_list)
    table_headings.append(f'Interest credited and debited')


    # Running balance
    def extract_numbers(input_string):
        if re.sub(r'[^0-9.-]', '', input_string)[-1] is '.' :
            return re.sub(r'[^0-9.-]', '', input_string)[:-1]
        
        else:
            return re.sub(r'[^0-9.-]', '', input_string)


    for i, r in enumerate(result):

        if len(r['BALANCE']) > 0:
            if i != 0 and not invalid_running_bal and bank != 'HDFC':

                prev_balance = extract_numbers(str(result[i - 1]['BALANCE'][0]).replace(',', ''))
                curr_balance = extract_numbers(str(r['BALANCE'][0]).replace(',', ''))
                curr_amount = extract_numbers(str(r['AMOUNT']).replace(',', ''))

                # print("prev_balance: ", prev_balance)
                # print("curr_balance: ", curr_balance)

                if r['TYPE'] == 'DR':
                    if float(curr_balance) != round(float(prev_balance) - float(curr_amount), 2) :
                        invalid_running_bal = True
                        invalid_running_bal_index = i

                if r['TYPE'] == 'CR':
                    # print(float(prev_balance), '+', float(curr_amount), '=', float(prev_balance) + float(curr_amount), 2)
                    if float(curr_balance) != round(float(prev_balance) + float(curr_amount), 2) :
                        invalid_running_bal = True
                        invalid_running_bal_index = i
        
        else:
            invalid_running_bal = 'NO'

    if len(final) > 0 and len(govt_list) > 0:
        PDFGeneration.create(
            final,
            govt_list=govt_list,
            outflow_labels=outflow_labels,
            inflow_labels=inflow_labels,
            current_lang=current_lang,
            table_headings=table_headings,
            chart_data=chart_data,
            gross_income = gross_income,
            gross_outcome = gross_outcome,
            total_income=total_income,
            total_outcome=total_outcome,
            line_chart_data=final_line_data,
            running_balance = not invalid_running_bal if type(invalid_running_bal) == bool else invalid_running_bal,
            running_balance_item = result[invalid_running_bal_index]
        )

    
if __name__ == "__main__":
    segregate()
