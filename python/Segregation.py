import re
import json
import PDFGeneration

def find_float(obj):
    index = 0
    for key, value in obj.items():
        try:
            float_value = float(value.replace(',',''))
            # print(float_value)
            # print(isinstance(float_value, float))

            if isinstance(float_value, float):
                return index
        except ValueError:
            # print('Haha!')
            pass
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

def segregate(data, threshold):

    new_list = []
    for input_dict in data:
        renewed = {key.upper(): '-' if value == None else value for key, value in input_dict.items()}
        new_list.append(renewed)

    data = new_list

    for raw in data:

        num_index = find_float(raw)
        check_index = num_index + 1
        # print(data)

        # print(check_index)
        # print(raw)
        date = raw[list(raw.keys())[0]].split('\n')[0]
        desc = (raw.get('PARTICULARS') or raw.get('DESCRIPTION') or raw.get('NARRATION')).replace('\n', '')
        type = raw.get('TYPE') or ('CR' if len(raw) - 1 == check_index else ('DR' if raw[list(raw.keys())[check_index]] == '-' else 'CR'))
        type = 'DR' if type == 'Debit' else 'CR' if type == 'Credit' else type
        amount = ( raw.get('AMOUNT') or raw[list(raw.keys())[num_index]] ).replace(',','')
        # print('\n')

        entry = {
            'Date': date,
            'Description': desc,
            'amount': amount,
            'type': type
        }

        # print(entry)
        result.append(entry)
        temp_desc = desc.upper()

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
        if float(amount) > int(threshold):
            # print(entry)
            # print(type+'\n\n')
            if type == 'CR': high_value_transaction['inflow'].append(entry)
            elif type == 'DR': high_value_transaction['outflow'].append(entry)

            new_hvt = [ date, desc, amount if type == 'CR' else '-', amount if type == 'DR' else '-' ]
            hvt_list.append(new_hvt)

    charge_list = [list(obj.values())[:-1] + ['Bank Charges'] for obj in charges]
    charge_header = ['Date', 'Decription', 'Amount', 'Type']
    if len(charge_list) > 0 : charge_list.insert(0, charge_header)

    mode_list = []
    for key, value in m_o_p.items():
        d_imps = sum(float(obj['amount'].replace(',', '')) for obj in value if obj['type'] == 'DR' and float(obj['amount'].replace(',', '')) > 0)
        c_imps = sum(float(obj['amount'].replace(',', '')) for obj in value if obj['type'] == 'CR' and float(obj['amount'].replace(',', '')) > 0)
        mode_list.append([key, str(len(value)), '{:.2f}'.format(d_imps), '{:.2f}'.format(c_imps)])

    mode_header = ['Particular', 'Count', 'Amount INFLOW' , 'Amount OUTFLOE']
    if len(mode_list) > 0 : mode_list.insert(0, mode_header)


    # final list
    final = [charge_list, mode_list, hvt_list]
    # PDFGeneration.create(final)

# Example usage:
# data = [
    # {"DATE": "23/03/2023", "DESCRIPTION": "TO ONL UPI/DR/308248255168/KAVITHA /PYTM/PAYTMQR281/U::00607", "CHEQUE NO": null, "DEBIT": "30.00", "CREDIT": null, "BALANCE": "145.56"}, {"DATE": "22/03/2023", "DESCRIPTION": "TO ONL UPI/DR/308130535462/DHARANIS/UTIB/DHARANISH5/U::00607", "CHEQUE NO": null, "DEBIT": "40.00", "CREDIT": null, "BALANCE": "175.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "BY ONL UPI/CR/308098824819/NAVANEET/KARB/NAVANEETHA/U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "100.00", "BALANCE": "215.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "TO ONL UPI/DR/308005135653/NAVANEET/KARB/NAVANEETHA/O::00607", "CHEQUE NO": null, "DEBIT": "100.00", "CREDIT": null, "BALANCE": "115.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "BY ONL UPI/CR/308098720779/GOOGLEPA/UTIB/GOOG-PAYME/U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "5.00", "BALANCE": "215.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "TO ONL UPI/DR/308005072971/NAVANEET/KARB/NAVANEETHA/U::00607", "CHEQUE NO": null, "DEBIT": "200.00", "CREDIT": null, "BALANCE": "210.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "BY ONL UPI/CR/308098178922/VISWANAT/CNRB/SUGADEV070/U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "100.00", "BALANCE": "410.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "BY ONL UPI/CR/308098078771/NAVANEET/KARB/NAVANEETHA/U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "180.00", "BALANCE": "310.56"}, {"DATE": "21/03/2023", "DESCRIPTION": "TO ONL UPI/DR/308000564035/PARTHIBA/PYTM/PAYTMQR281/U::00607", "CHEQUE NO": null, "DEBIT": "10.00", "CREDIT": null, "BALANCE": "130.56"}, {"DATE": "16/03/2023", "DESCRIPTION": "TO ONL UPI/DR/307592555486/KEVIN KI/HDFC/KIRSTENBAB/U::00607", "CHEQUE NO": null, "DEBIT": "50.00", "CREDIT": null, "BALANCE": "140.56"}, {"DATE": "13/03/2023", "DESCRIPTION": "BY ONL UPI/CR/307244232618/MR S B K/CIUB/KRISHNA07 /U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "60.00", "BALANCE": "190.56"}, {"DATE": "13/03/2023", "DESCRIPTION": "TO ONL UPI/DR/307229568339/ABBAS M/PYTM/PAYTMQR281/UP::00607", "CHEQUE NO": null, "DEBIT": "140.00", "CREDIT": null, "BALANCE": "130.56"}, {"DATE": "12/03/2023", "DESCRIPTION": "TO ONL UPI/DR/307120562870/SURYAPRA/IOBA/VELUMANIAR/U::00607", "CHEQUE NO": null, "DEBIT": "1.00", "CREDIT": null, "BALANCE": "270.56"}, {"DATE": "12/03/2023", "DESCRIPTION": "TO ONL UPI/DR/307120551673/SURYAPRA/IOBA/VELUMANIAR/U::00607", "CHEQUE NO": null, "DEBIT": "1,079.00", "CREDIT": null, "BALANCE": "271.56"}, {"DATE": "12/03/2023", "DESCRIPTION": "BY ONL UPI/CR/307120344564/SURYAPRA/IOBA/VELUMANIAR/U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "1,080.00", "BALANCE": "1,350.56"}, {"DATE": "11/03/2023", "DESCRIPTION": "TO ONL UPI/DR/307094625500/MUTHUSAN/YESB/Q435352089/U::00607", "CHEQUE NO": null, "DEBIT": "40.00", "CREDIT": null, "BALANCE": "270.56"}, {"DATE": "11/03/2023", "DESCRIPTION": "BY ONL UPI/CR/307068867834/MR S B K/CIUB/KRISHNA07 /U::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "30.00", "BALANCE": "310.56"}, {"DATE": "10/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306965837728/M DHIREN/BARB/MDPNKL2004/U::00607", "CHEQUE NO": null, "DEBIT": "70.00", "CREDIT": null, "BALANCE": "280.56"}, {"DATE": "10/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306961091469/ABBAS M/PYTM/PAYTMQR281/UP::00607", "CHEQUE NO": null, "DEBIT": "140.00", "CREDIT": null, "BALANCE": "350.56"}, {"DATE": "09/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306846603856/SRI GANG/YESB/Q488710188/T::00607", "CHEQUE NO": null, "DEBIT": "54.00", "CREDIT": null, "BALANCE": "490.56"}, {"DATE": "09/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306837550664/MAHESWAR/KVBL/IAMKISHORE/U::00607", "CHEQUE NO": null, "DEBIT": "30.00", "CREDIT": null, "BALANCE": "544.56"}, {"DATE": "07/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306645568927/MS LAVAN/CIUB/LAVANYAAKB/U::00607", "CHEQUE NO": null, "DEBIT": "25.00", "CREDIT": null, "BALANCE": "574.56"}, {"DATE": "07/03/2023", "DESCRIPTION": "BY ONL UPI/CR/306605199218/MR J PRA/IDIB/PRASATH J1/B::00032", "CHEQUE NO": null, "DEBIT": null, "CREDIT": "100.00", "BALANCE": "599.56"}, {"DATE": "04/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306354299342/BILLDESK/ICIC/BILLDESK P/U::00607", "CHEQUE NO": null, "DEBIT": "15.00", "CREDIT": null, "BALANCE": "499.56"}, {"DATE": "03/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306236170398/EURONETG/ICIC/EURONETGPA/U::00607", "CHEQUE NO": null, "DEBIT": "15.00", "CREDIT": null, "BALANCE": "514.56"}, {"DATE": "02/03/2023", "DESCRIPTION": "TO ONL UPI/DR/306178163555/EURONETG/ICIC/EURONETGPA/U::00607", "CHEQUE NO": null, "DEBIT": "54.00", "CREDIT": null, "BALANCE": "529.56"}, {"DATE": "TOTAL", "DESCRIPTION": null, "CHEQUE NO": null, "DEBIT": "2,093.00", "CREDIT": "1,655.00", "BALANCE": "529.56"}]

# result = segregate(data)
# print(json.dumps(result, indent=2))

if __name__ == "__main__":
    segregate()