import re
import PDFGeneration
from collections import defaultdict

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]


def find_float(obj):
    index = 0
    for key, value in obj.items():
        try:
            float_value = float(value.replace(',',''))

            if isinstance(float_value, float):
                return index
        except ValueError: pass

        index += 1
    return index

result = []
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

def segregate(data, threshold):

    total_income = 0;
    total_outcome = 0;


    new_list = []
    for input_dict in data:
        renewed = {key.upper(): '-' if value == None else value for key, value in input_dict.items()}
        new_list.append(renewed)

    data = new_list

    for raw in data:
        num_index = find_float(raw)
        check_index = num_index + 1
       
        date = raw[list(raw.keys())[0]].split('\n')[0]
        desc = (raw.get('PARTICULARS') or raw.get('DESCRIPTION') or raw.get('NARRATION')).replace('\n', '')
        type = raw.get('TYPE') or ('CR' if len(raw) - 1 == check_index else ('DR' if raw[list(raw.keys())[check_index]] == '-' else 'CR'))
        type = 'DR' if type == 'Debit' else 'CR' if type == 'Credit' else type
        amount = ( raw.get('AMOUNT') or raw[list(raw.keys())[num_index]] ).replace(',','')

        entry = {
            'DATE': date,
            'DESCRIPTION': desc,
            'AMOUNT': amount,
            'TYPE': type
        }

        if (len(date) > 1) and (len(desc) > 1) and (len(amount) > 1) and (len(type) > 1):
            result.append(entry)

        temp_desc = desc.upper()

        # Totals
        if type == 'DR': total_income += float(amount)
        if type =='CR': total_outcome += float(amount)

        if ('CHARGES' in temp_desc or 'CHG' in temp_desc or 'BG CHARGES' in temp_desc or 'CHRGS' in temp_desc
            or 'FEE' in temp_desc or 'MISC' in temp_desc or 'MISC-REMIT' in temp_desc or 'BULK' in temp_desc):
            charges.append(entry)

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

        if mode and mode not in m_o_p:
            m_o_p[mode] = []
        if mode:
            m_o_p[mode].append(entry)

        # High Value Transaction
        if (float(amount) > float(threshold) ) and float(threshold) > 0 :
            if type == 'CR': high_value_transaction['inflow'].append(entry)
            elif type == 'DR': high_value_transaction['outflow'].append(entry)

            new_hvt = [ date, desc, amount if type == 'CR' else '-', amount if type == 'DR' else '-' ]
            hvt_list.append(new_hvt)

    
    # Unusual Transaction    
    date = ''
    decs = set()
    amounts = set()
    trans_type = ''
    first_date_value = dict

    unsual_list = []

    for d in result:
        current_date = d['DATE']
        current_desc = d['DESCRIPTION']
        current_amount = d['AMOUNT']
        current_type = d['TYPE']

        if current_date != date:
            date = current_date
            decs.add(current_desc)
            amounts.add(current_amount)

            trans_type = current_type
            first_date_value = d # keeping the first value for adding it later => 

        else:
            
            if (current_desc in decs and current_amount in amounts and current_type != trans_type):

                # adding the first value after checking <=
                if first_date_value not in unsual_list: 
                    unsual_list.append(first_date_value)

                # avoiding duplicate values.
                if d not in unsual_list: unsual_list.append(d)
                # final.append(d)

            # checking for new payee under the same date
            if current_desc not in decs or current_amount not in amounts:
                decs.add(current_desc)
                amounts.add(current_amount)
                first_date_value = d

            trans_type = current_type
    

    # Unusual Transactions
    unusual_trans_list = [list(my_dict.values()) for my_dict in unsual_list]
    unusual_header = ['Date', 'Decription', 'Amount', 'Type']
    if len(unusual_trans_list) > 0 : 
        unusual_trans_list.insert(0, unusual_header)
        final.append(unusual_trans_list)
        table_headings.append('Unusual Transactions')


    # Bank Charges
    charge_list = [list(obj.values())[:-1] + ['Bank Charges'] for obj in charges]
    charge_header = ['Date', 'Decription', 'Amount', 'Type']
    if len(charge_list) > 0 :
        charge_list.insert(0, charge_header)
        final.append(charge_list)
        table_headings.append('Bank Charges Analysis')


    # Mode Of Payment
    mode_list = []
    for key, value in m_o_p.items():
        d_imps = sum(float(obj['AMOUNT'].replace(',', '')) for obj in value if obj['TYPE'] == 'DR' and float(obj['AMOUNT'].replace(',', '')) > 0)
        c_imps = sum(float(obj['AMOUNT'].replace(',', '')) for obj in value if obj['TYPE'] == 'CR' and float(obj['AMOUNT'].replace(',', '')) > 0)
        mode_list.append([key, str(len(value)), '{:.2f}'.format(d_imps), '{:.2f}'.format(c_imps)])

    mode_header = ['Particular', 'Count', 'Amount INFLOW' , 'Amount OUTFLOW']
    if len(mode_list) > 0 : 
        mode_list.insert(0, mode_header)
        final.append(mode_list)
        table_headings.append('UPI - MODE OF PAYMENT\n(STATUS COUNT)')



    # High Value Transaction
    hvt_header = ['Date', 'Decription', 'Amount INFLOW' , 'Amount OUTFLOW']
    if len(hvt_list) > 0 : 
        hvt_list.insert(0, hvt_header)
        final.append(hvt_list)
        table_headings.append(f'High Value Transactions({threshold})')


    # Duplicate Transaction
    seen = defaultdict(list)
    duplicates = []

    for my_dict in data:
        frozenset_dict = frozenset(my_dict.items())

        if frozenset_dict in seen:
            duplicates.extend([seen[frozenset_dict], my_dict])
        else:
            seen[frozenset_dict] = my_dict
    
    dup_header = ['Date', 'Decription', 'Amount', 'Type']

    if len(duplicates) > 0: 
        duplicates.insert(0, dup_header)
        final.append(duplicates)
        table_headings.append(f'Duplicate Transactions')


    # Attribute Classification & Month Wise Data

    description_stats = {}
    limit = 1
    date_data = {}
    graph_months = []
    min_amount = 0
    max_amount = 0
    graph_dots = []

    for my_dict in result:

        # --------------- Attr. Classftn. --------------- #
        description_value = my_dict['DESCRIPTION']
        amount_value = float(my_dict['AMOUNT'].replace(',', ''))
        transaction_type = my_dict['TYPE']

        # Initialize count and sum if the 'Description' is not seen before
        if description_value not in description_stats:
            description_stats[description_value] = { 'Desc': description_value , 'DR': 0, 'CR': 0, 'count':0 }

        # Update count and sum for the 'Description' and type
        description_stats[description_value][ transaction_type ] += amount_value
        description_stats[description_value]['count'] += 1


        # --------------- Month Wise Data --------------- #
        present_date = list(my_dict.values())[0]
        
        present_date = present_date.split(',') if ',' in present_date else present_date.split('-') if '-' in present_date else present_date.split('/')
        # print(present_date)

        if present_date[1].isnumeric():
            date_key = MONTHS[int(present_date[1]) - 1 ][:3] + f" '{ present_date[-1][-2:] }"
        else:
            date_key = present_date[1] + f" '{ present_date[-1][-2:] }"

        if date_key not in graph_months: graph_months.append(date_key)

        if date_key not in date_data:
            date_data[date_key] = { 'Month': date_key, 'DR': 0, 'CR':0 }

        date_data[date_key][ transaction_type ] += amount_value

        if min_amount != 0:
            min_amount = amount_value if amount_value < min_amount else min_amount

        max_amount = amount_value if amount_value > max_amount else max_amount

        if my_dict['TYPE'] == 'Debit' : graph_dots.append( (0, amount_value) )
        if my_dict['TYPE'] == 'Credit' : graph_dots.append( (amount_value, 0) )

    attributes_list = [ list(my_dict.values())[:-1] for my_dict in description_stats.values() if my_dict['count'] > limit ]

    # line_chart = [ graph_months, graph_dots, min_amount, max_amount ]

    chart_data = []
    if len(attributes_list) > 0:

        attr_header = ['Description', 'Debit', 'Credit']
        attributes_list.insert(0, attr_header)
        final.append(attributes_list)
        table_headings.append(f'Attribute Classification')


        attr_outflow_list = [sublist[-2] for sublist in attributes_list ]
        attr_inflow_list = [sublist[-1] for sublist in attributes_list ]

        if(len(attr_outflow_list) > 0): chart_data.append(attr_outflow_list)
        if(len(attr_inflow_list) > 0): chart_data.append(attr_inflow_list)


    # PDF Generation
    if len(final) > 0: PDFGeneration.create(
            final, 
            table_headings=table_headings,
            chart_data=chart_data, 
            total_income=total_income, 
            total_outcome=total_outcome,
            line_chart_data=[date_data, graph_months],
            min_amount=min_amount, 
            max_amount=max_amount
        )


if __name__ == "__main__":
    segregate()