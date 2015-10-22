#!/user/bin/python3
# -*- coding: utf-8 -*-
# compatible with Python 3.4.3

__author__="Bo Zhou"
__copyright__ = "Copyright 2015, The NRA project "
__credits__ = ["Bo Zhou"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Bo Zhou"
__email__ = "bzhou2@ualberta.ca"
__status__ = "Testing"

from openpyxl import Workbook
from openpyxl import load_workbook
import json
import requests
import time


inFile = input("Please enter xlsx file name: ")
startTime = time.time()
inwb = load_workbook(filename=inFile)
sheetRange = inwb ['NRA Address']
#sheetRange['H1'] = 123
#print(sheetRange["A2000"].value)
row = 1
while True:
    la = sheetRange["F"+str(row)].value
    lo = sheetRange["G"+str(row)].value
    #la_test = 28.35975
    #lo_test = -81.421988
    if sheetRange["A"+str(row)].value == None:
        break
    url = "http://data.fcc.gov/api/block/find?format=json&latitude="+str(la)+"&longitude="+str(lo)+"&showall=true"
    try:
        response = requests.get(url)
    except Exception as e:
        print("Request fail try again")
        time.sleep(5)
        continue
    data = response.json()
    sheetRange["H"+str(row)] = data["Block"]["FIPS"]
    print (data["Block"]["FIPS"],data["County"]["name"],row)
    #print(data["Block"]["FIPS"])
    row += 1
inwb.save(inFile)
print("Finish")
elapsedTime = time.time() - startTime
print ("time use: ", elapsedTime)
