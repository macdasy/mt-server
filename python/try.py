
data = [
    {'Date': '10-11-2022', 'Description': 'IMPS/P2A/231417192935/XXXXXXXXXX6446/methu', 'amount': '3005.90', 'type': 'DR'},
    {'Date': '10-11-2022', 'Description': 'IMPS/P2A/231417192935/XXXXXXXXXX6446/methu', 'amount': '3005.90', 'type': 'CR'},
    {'Date': '10-11-2022', 'Description': 'IMPS/P2A/231417192935/XXXXXXXXXX6446/methu', 'amount': '3005.90', 'type': 'CR'},

    {'Date': '11-11-2022', 'Description': 'IMPS/P2A/231417192935/XXXXXXXXXX6446/methu', 'amount': '3005.90', 'type': 'CR'},
    {'Date': '11-11-2022', 'Description': 'IMPS/P2A/231417192935/XXXXXXXXXX6446/methu', 'amount': '3005.90', 'type': 'CR'},

    {'Date': '05-11-2022', 'Description': '09530100026966:Int.Pd:01-08-2022 to 31-10-2022', 'amount': '7.00', 'type': 'CR'},
    {'Date': '11-10-2022', 'Description': 'UPI/228422570101/18:25:51/UPI/suriya740227-1@okax', 'amount': '15.00', 'type': 'CR'},
    {'Date': '06-10-2022', 'Description': 'UPI/227989221739/14:46:16/UPI/dmdakshesh@oksbi/UP', 'amount': '31.00', 'type': 'CR'},
    {'Date': '23-09-2022', 'Description': 'IMPS/P2A/226616401918/XXXXXXXXXX4918/dk', 'amount': '502.95', 'type': 'DR'},
    {'Date': '23-09-2022', 'Description': 'UPI/226693761466/16:39:33/UPI/kesavhari2000@okici', 'amount': '500.00', 'type': 'CR'},
    {'Date': '23-09-2022', 'Description': 'SMS Alert charges for Qtr Sep-22', 'amount': '17.70', 'type': 'DR'},
    {'Date': '21-09-2022', 'Description': 'MBK/226440127774/18:43:49/', 'amount': '19.00', 'type': 'DR'},
]

# for d in data:

    # if d['type'] == 'DR':


# dates = set()
# decs = set()
# amounts = set()

# for d in data:
#     target_date = d['Date']
#     target_desc = d['Description']
#     target_amount = d['amount']

#     # print(target_date)
#     if target_date not in dates:
#         decs.clear()
#         amounts.clear()

#         date_dicts = [transaction for transaction in data if transaction['Date'] == target_date]

#         sample_dicts = [ transaction for transaction in data if transaction['Date'] == target_date and
#                                                             transaction['Description'] == target_desc and
#                                                             transaction['amount'] == target_amount ]

#         if(len(sample_dicts) > 1):
#             # print(sample_dicts)   

#             current_value = sample_dicts[0]
#             for i in range(len(sample_dicts)):
#                 next_value = sample_dicts[i+1] if i+1 < len(sample_dicts) else {}

#                 if len(next_value.keys()) > 0:
#                     print(current_value)
#                     print(next_value)
#                     print()
                    
#                 current_value = next_value

#     amounts.add(target_amount)
#     decs.add(target_desc)
#     dates.add(target_date)
                


                # current_value = sample_dicts[i+1]

        # if(len(date_dicts) > 1):     
        #     # print(date_dicts)
        #     # print('\n')
        #     if target_desc not in decs:
        #         desc_dicts = [transaction for transaction in date_dicts if transaction['Description'] == target_desc]
        #         # print(desc_dicts)
        #         # print('\n')

        #         if(len(desc_dicts) > 1):
        #             # print(desc_dicts)
        #             # print('\n')

        #             if target_amount not in amounts:
        #                 amount_dicts = [transaction for transaction in desc_dicts if transaction['amount'] == target_amount]

        #                 if(len(amount_dicts) > 1):
        #                     for i in range(len(amount_dicts)):
        #                         current_value = amount_dicts[i]
        #                         next_value = amount_dicts[i+1] if i+1 < len(amount_dicts) else {}

        #                         if len(next_value.keys()) > 0:
        #                             # print(current_value)
        #                             # print(next_value)
        #                             print()

                                # if i+1 < len(amount_dicts):
                                #     print(i, i+1)
                                #     print('\n')

                            # pass

    #                 amounts.add(target_amount)

    #         decs.add(target_desc)

    # dates.add(target_date)


    # if d['Date'] == target_date:
    #     description = d['Description']
    #     if description in description_counts:
    #         matching_dicts.append(d)
    #     else:
    #         description_counts[description] = 1


# for transaction in date_dicts:
#     print(transaction)

# print(description_counts)

    # if d['Date'] not in dates: dates.append(d['Date'])
    # else: pass
