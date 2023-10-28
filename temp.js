
data = [{
    'Date': '29-Aug-2023',
    'Description': 'UPI/324158479418/DR/SYED\nBAHRUDEEN AM/PYT/Payment',
    'amount': '190.00',
    'Type': 'DR'
  },
  {
    'Date (Value\nDate)': '29-Aug-2023\n(29-Aug-2023)',
    Particulars: 'CHQ 324177275589/DR/Mr D\nRAMESH/IDI/Payment f',
    'Ref\nNo__PMSC/Cheque\nNo': 'S33252658',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '-',
    'Credit(Rs)': '3100.00',
    'Balance(Rs)': '72026.73'
  },
  {
    'Date (Value\nDate)': '30-Aug-2023\n(30-Aug-2023)',
    Particulars: 'RTGS 324296111933/DR/NEW S\nARAVANAA SUP/PYT/Payment',
    'Ref\nNo__PMSC/Cheque\nNo': 'S44710782',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '3503.00',
    'Credit(Rs)': '-',
    'Balance(Rs)': '68523.73'
  },
  {
    'Date (Value\nDate)': '31-Aug-2023\n(31-Aug-2023)',
    Particulars: 'TO NEFT TRF - RSURA: 025203485\n000019-DAYALAN S and so',
    'Ref\nNo__PMSC/Cheque\nNo': 'S47570209',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '102.00',
    'Credit(Rs)': '-',
    'Balance(Rs)': '68421.73'
  },
  {
    'Date (Value\nDate)': '31-Aug-2023\n(31-Aug-2023)',
    Particulars: 'UPI/324353434643/DR/TATA PLAY\nDIRECT/YES/Payment',
    'Ref\nNo__PMSC/Cheque\nNo': 'S48273905',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '214.00',
    'Credit(Rs)': '-',
    'Balance(Rs)': '68207.73'
  },
  {
    'Date (Value\nDate)': '31-Aug-2023\n(31-Aug-2023)',
    'Narration': '324378857068/DR/IMPS/LOGES\nHWARAN M/UCB/Payment f',
    'Ref\nNo__PMSC/Cheque\nNo': 'S49368857',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '80.00',
    'Credit(Rs)': '-',
    'Balance(Rs)': '68127.73'
  },
  {
    'Date (Value\nDate)': '31-Aug-2023\n(31-Aug-2023)',
    'Description': 'Charges for payment',
    'Ref\nNo__PMSC/Cheque\nNo': 'S51074594',
    'Transaction\nType': 'Transfer',
    'Debit(Rs)': '-',
    'Credit(Rs)': '5000.00',
  }
]

function findFloat(obj) {
    let index = 0;
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          const value = obj[key];
          // Check if the value is a string and can be parsed as a two-decimal float
          const floatValue = parseFloat(value);
          if (!isNaN(floatValue) && floatValue.toFixed(2) === value) {
            return index; // Return the index (key) of the first matching string
          }
        } index++;
      }
      return null;  // Return null if no float value is found
}


const result = []
const charges = []
const MOP = {}
const highValueTransaction = []
  
for(var d in data){
    const raw =  data[d];
    const num_index = findFloat(raw);
    const check_index = num_index + 1;

    const desc = (raw['Particulars'] ? raw['Particulars'] : ( raw['Description'] ? raw['Description'] : raw['Narration'] )).replace('\n', '') ;
    const amount = Number(Object.values(raw)[num_index]);
    const type = raw['Type'] ? raw['Type'] : ( Object.keys.length - 1 === check_index ? 'CR' : ( Object.values(raw)[check_index] === '-' ? 'DR' : 'CR' ) )

    const entry = {
        Date: Object.values(raw)[0].split('\n')[0],
        Description: desc,
        amount: amount,
        type: type
    }

    result.push(entry);
    const tempDesc = desc.toUpperCase();


    // To find: Charges
    if (    tempDesc.includes('CHARGES') || tempDesc.includes('CHG') || 
            tempDesc.includes('BG CHARGES') || tempDesc.includes('CHRGS') ||  
            tempDesc.includes('FEE') ||  tempDesc.includes('MISC') ||  
            tempDesc.includes('MISC-REMIT') ||  tempDesc.includes('BULK') 
        ) { charges.push(entry); }


    // To find: Mode Of Payment
    let mode;
    if (tempDesc.match(/UPI[^]*?(?=\s|$)/g)) mode = "UPI";
    else if (tempDesc.match(/IMPS[^]*?(?=\s|$)/g)) mode = "IMPS";
    else if (tempDesc.match(/NEFT[^]*?(?=\s|$)/g)) mode = "NEFT";
    else if (tempDesc.match(/CHQ[^]*?(?=\s|$)/g)) mode = "CHQ";
    else if (tempDesc.match(/RTGS[^]*?(?=\s|$)/g)) mode = "RTGS";

    if (mode!==undefined && !MOP.hasOwnProperty(mode)) MOP[mode] = [];
    if(mode!==undefined) MOP[mode].push(entry);


    // To find: High Value Transaction
    if(amount > 3000) highValueTransaction.push(entry)

};

// result.forEach(element => {
//     console.log(element);
// });

console.log(highValueTransaction);
