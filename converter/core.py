import os
import re
import csv
import zipfile
from decimal import *

# Account CSV file names

zipsDict = {'Name' : 'transaction_history_Name.zip'}
accountsDict = {'Name' : '00000000'}

outputTextFileName = "output.txt"

multipliers = {'Name' : 1}

ignorePattern = 'IGNORE'

lastName = 'Doe'

# Create output file

outputFile = open (outputTextFileName, 'w')
    

# Function to record output

def log (output_file, text):
    print (text)
    output_file.write(text+"\n")
    
 
for accName, accNumber in accountsDict.items():

    log (outputFile, accName)

    #Unzip
    zf = zipfile.ZipFile(zipsDict[accName])
    zf.extract(accNumber + ".csv")


    # Open Input CSV
    csvInput = open(accNumber + ".csv", 'r')
    csvReader = csv.reader(csvInput, delimiter=',')


    # Open Output CSV
    csvOutput = open("YNAB_" + accName + ".csv", 'w', newline='')
    csvWriter = csv.writer(csvOutput, delimiter=',')



    # Check Input Header

    item = csvReader.__next__()
    assert (item[0].startswith("ACCOUNT TRANSACTION HISTORY") )

    item = csvReader.__next__()
    assert (item.__len__() == 0)  # Make this a function

    item = csvReader.__next__()
    assert (item[2].find (lastName) >= 0)

    item = csvReader.__next__()
    assert (item[1].find (accNumber) >= 0)

    item = csvReader.__next__()
    balanceA = item[1]
    balanceB = item[2]

    item = csvReader.__next__()
    assert (item.__len__() == 0)  # Make this a function

    item = csvReader.__next__()
    assert (item[0].find ("Date") >= 0)
    assert (item[1].find ("Amount") >= 0)
    assert (item[2].find ("Balance") >= 0)
    assert (item[3].find ("Description") >= 0)



    # Reformat and Write for Output

    header = ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']
    csvWriter.writerow(header)

    multiplier = multipliers[accName]

    for item in csvReader:
        dateItem        = item[0].strip()
        amountItem      = item[1].strip()
        descriptionItem = item[3].strip()
        row = []

        ignoreRegex = re.compile(ignorePattern)
        if ignoreRegex.match(descriptionItem):
            continue
        
        row.append (dateItem)
        row.append (descriptionItem)
        row.append ('')
        row.append (descriptionItem)
        
        number = (Decimal(amountItem) * Decimal(multiplier)).quantize(Decimal('.01'))
        if number < 0:
            row.append (-number)
            row.append ('')
        else:
            row.append ('')
            row.append (number)
            
        csvWriter.writerow(row)
        
    csvInput.close ()
    csvOutput.close ()

    decimalRegex = re.compile('[ \.\d]+$')

    # Print account balances for easy viewing
    if decimalRegex.match(balanceA) == None:
        log (outputFile, 'Balance: ' + str((Decimal(balanceB) * Decimal(multiplier)).quantize(Decimal('.01'))))
        log (outputFile, '')
    elif decimalRegex.match(balanceB) == None:
        log (outputFile, 'Balance: ' + str((Decimal(balanceA) * Decimal(multiplier)).quantize(Decimal('.01'))))
        log (outputFile, '')
    else:
        log (outputFile, 'Balance A: ' + str((Decimal(balanceA) * Decimal(multiplier)).quantize(Decimal('.01'))))
        log (outputFile, 'Balance B: ' + str((Decimal(balanceB) * Decimal(multiplier)).quantize(Decimal('.01'))))
        log (outputFile, '')


# Pause console
os.system('pause')
