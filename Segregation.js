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
const m_o_p = {}
const highValueTransaction = []

function Segregate(data){
  // console.log(data);
  for(var d in data){
      const raw =  data[d];
      // console.log(raw);
      const num_index = findFloat(raw);
      const check_index = num_index + 1;

      const desc = (raw['Particulars'] ? raw['Particulars'] : ( raw['Description'] ? raw['Description'] : raw['Narration'] )).replace('\n', '') ;
      const amount = raw['Amount'];
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
      if (  tempDesc.includes('CHARGES') || tempDesc.includes('CHG') || 
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

      if (mode!==undefined && !m_o_p.hasOwnProperty(mode)) m_o_p[mode] = [];
      if(mode!==undefined) m_o_p[mode].push(entry);


      // To find: High Value Transaction
      if(amount > 3000) highValueTransaction.push(entry)

  };

  // Charge Table Data
  // console.log(charges);
  let ChargeList = charges.map(obj => Object.values(obj));
  ChargeList = ChargeList.map(list => list.slice(0, -1)).map(list => [...list, 'Bank Charges']);

  // Mode_Of_Payment Table Data
  const modeList = []
  for(var key in m_o_p){
    const dIMPS = m_o_p[key].reduce((acc, obj) => {
      const amount = parseFloat((obj.amount).replace(',',''));
      if (obj.type === 'Debit' && amount>0) { return acc + amount }
      return acc;
    }, 0);
    
    const cIMPS = m_o_p[key].reduce((acc, obj) => {
      const amount = parseFloat((obj.amount).replace(',',''));
      if (obj.type === 'Credit' && amount>0) { return acc + amount }
      return acc;
    }, 0);

    modeList.push([key, String(m_o_p[key].length), dIMPS.toFixed(2), cIMPS.toFixed(2)])
  }

  let final = []
  // console.log(highValueTransaction);
  final.push(ChargeList, modeList)
}

module.exports = Segregate;