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

import time
import bs4
import xlsxwriter
import geopy
from contextlib import closing
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import Select

# global variable
bft_number = 1 # for bft
pts_number = 1 # for pts
row = 0
rowCount = 0
# http://www.zipcodestogo.com/Pennsylvania/
f = open("pazip",'r')
zipList = f.read().split()    
f.close()

# swithch key
DUPFILTER = 0 # avoid duplicated information, change it to 1, or leave it 0 if you need original information
PROVINCE = "PA" # if you want to get all, change it to ''


def open_url_by_se(driver):
    # main page
    chooseList = ["0", "2", "8"]
    checkboxId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_chkGrids_"
    formId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_LocationTextBox"
    rangId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_ddlMiles"    
    srchBtId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_imgbtn_Locate"
    # Basic Firearms Training
    bftPageCtrlId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_BasicFirearmPagerPanel"
    bftNtPageId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg2NextPage"    
    bftTableId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg2"
    bftDataTag = "ET"
    # Places to Shoot
    ptsPageCtrlId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_NationalRegistryShootPagerPanel"
    ptsNtPageId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg1NextPage"
    ptsTableId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg1"
    ptsDataTag = "RANGE"
    # Clubs and Associations
    try:
        for i in chooseList:
            driver.find_element_by_id(checkboxId+i).click()
    except Exception as e:
        print(e)
    elem = driver.find_element_by_id(formId)
    # http://www.netstate.com/states/geography/pa_geography.htm
    #elem.send_keys("16823") # The geographic center of Pennsylvania
    elem.send_keys("16411") # for test and confirm
    select = Select(driver.find_element_by_id(rangId))
    select.select_by_visible_text("75")
    button = driver.find_element_by_id(srchBtId)
    button.click()
    workbook = xlsxwriter.Workbook("data_confirm_p6_75.xlsx")
    worksheet = workbook.add_worksheet('NRA Address') 
    worksheet.set_column("A:A",40)
    worksheet.set_column("B:C",60)
    # handle bft
    bftRslt = crawl_one_category(driver, bftPageCtrlId, bftNtPageId, bftTableId, bftDataTag, 2)
    write_to_excel(bftRslt, worksheet, 'Basic Firearms Training')
    # handle pts
    ptsRslt = crawl_one_category(driver, ptsPageCtrlId, ptsNtPageId, ptsTableId, ptsDataTag, 0)
    write_to_excel(ptsRslt, worksheet, 'Place to Shoot')
    # handle cad
    #cadRslt = crawl_cad()
    #write_to_excel(cadRslt, worksheet, 'Club and Associations Directory')
    workbook.close()
    return


def write_to_excel(content,worksheet,category):
    #content [(name, adrs, PA, Postcode, geo),...]
    global row
    for unit in content:
        worksheet.write(row, 0, category)
        column = 1
        for k in range(4):
            worksheet.write(row, column, unit[k])
            column += 1
        for item in unit[4]:
            worksheet.write(row, column, item)
            column += 1
        row += 1
    return


def search_page(soup, tableId, dataTag, omitNumber):
    global pts_number
    global bft_number
    cad_number = 1
    if dataTag == "ET":
        choose = bft_number
    elif dataTag == "RANGE":
        choose = pts_number
    elif dataTag == "CLUBDIRECTORY":
        choose = cad_number
    
    #cases = {"ET":bft_number,"RANGE":pts_number}
    table = soup.find(id = tableId)
    allItem = table.find_all(class_= "tableItem")
    resultList = []
    for el in allItem:
        item = []
        courseNameList = el.find(class_="findCourse").get_text().split()
        courseName = " ".join(courseNameList)
        courseBriefList = el.find(class_="findBrief").get_text().split()
        while True:
            if courseBriefList == []:
                break
            if courseBriefList[0] == "-":
                courseBriefList.pop(0)
                break
            else:
                courseBriefList.pop(0)
        courseBrief = " ".join(courseBriefList)
        info = el.find(id = dataTag + str(choose))
        
        if info != None:
            adrsList = info_catch(info.get_text(), omitNumber)
            if adrsList != None:
                adrsList [0] = courseName + ", " +courseBrief
                resultList.append(adrsList)
        choose += 1
    if dataTag == "ET":
        bft_number = choose
    elif dataTag == "RANGE":
        pts_number = choose   
    return resultList


# Based on Google Map Geolocation API
def geocoding(onePgAdrsList): #[(name, address, province, zip，(100,100)),(),()]
    global rowCount
    googlev3 = geopy.GoogleV3()
    geoAdrsList = []
    for el in onePgAdrsList:
        adrsCnt = ''
        newItem = []
        gps = tuple()
        for i in range(1,4):
            adrsCnt += (el[i]+' ')
        rowCount += 1
        try:
            place,gps = googlev3.geocode(adrsCnt)
        except Exception as err:
            print ("on row: "+str(rowCount)+". Cannot find Geolation for: "+adrsCnt+" ziplist[0] is: "+str(zipList[0]))
        for item in el:
            newItem.append(item)
        newItem.append(gps)
        geoAdrsList.append(newItem)
    return geoAdrsList


def crawl_one_category(driver, pageCtrlId, ntPageId, tableId, dataTag, omitNumber):
    currentPage = -2
    totalPage = -1
    retryNo = 0
    rsltList = []
    geoChcekList = []
    while currentPage < totalPage:
        content = driver.page_source
        soup = bs4.BeautifulSoup(content) 
        pageCtrl = soup.find(id=pageCtrlId)
        if pageCtrl == None:
            retryNo += 1
            time.sleep(10)
            print("try to reload "+str(currentPage+1))
            if retryNo <= 3:
                continue
        try:
            pageContent = pageCtrl.get_text()
        except Exception as err:
            print("No page control on page: "+str(currentPage+1))
            if retryNo <= 3:
                continue
        if retryNo != 4:
            pageList = pageContent.split()
            currentPage = int(pageList[1].replace('of', ''))
            totalPage = int(pageList[2])
        onePgList = search_page(soup, tableId, dataTag, omitNumber)
        geoedList = geocoding(onePgList)        
        if DUPFILTER == 1:
            for finalItem in geoedList:
                if (finalItem[4] in geoChcekList) and finalItem[4] != ():
                    continue
                else:
                    geoChcekList.append(finalItem[4])
                    rsltList.append(finalItem)
        else:
            for finalItem in geoedList:
                rsltList.append(finalItem)  
        if currentPage == totalPage or currentPage == -2:
            break 
        try:
            npBt = driver.find_element_by_id(ntPageId)
        except Exception as e:
            print (e)
            print ('stuck in page: '+str(currentPage))
            time.sleep(5)    
        npBt = driver.find_element_by_id(ntPageId)  
        npBt.click()
    return rsltList
    
    
def info_catch(item, omitNumber):
    global PROVINCE
    itemList = item.split()
    for i in range(omitNumber):
        itemList.pop(0)
    etAdrs = ''
    etPost = []
    j = 0
    length = len(itemList)
    while j < length:
        if itemList[j] != ',':
            etAdrs += (' '+itemList[j])
        else:
            for k in range (1,3):
                etPost.append(itemList[j+k])
            break
        j += 1
    if PROVINCE == '' or PROVINCE == etPost[0]:
        return [None, etAdrs, etPost[0], etPost[1]]
    else:
        return None
        

def crawl_cad():
    global zipList
    rsltList = []
    resultSet = []
    while zipList != []:
        onePgSet = []
        zipCode = zipList.pop(0)
        driver = webdriver.Firefox()
        driver.maximize_window()
        driver.get('http://findnra.nra.org/')      
        driver = do_cad_search(driver, zipCode)
        content = driver.page_source
        soup = bs4.BeautifulSoup(content)
        tableId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg11"
        dataTag = "CLUBDIRECTORY"
        onePgList = search_page(soup, tableId, dataTag, 1)
        for item in onePgList:
            if item not in resultSet:        
                onePgSet.append(item)
                resultSet.append(item)
        geoedList = geocoding(onePgSet)  
        for el in geoedList:
            rsltList.append(el)
        driver.close()
    return rsltList
        
    

def do_cad_search(driver, zipCode):
    failCount = 0
    failSwitch = True
    checkId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_chkGrids_2"
    while failSwitch:
        try: 
            driver.find_element_by_id(checkId).click()
            failSwitch = False
        except Exception as e:
            failCount += 1
            print("Fail to load main search Page. Failed: "+str(failCount)+" time(s)")
            time.sleep(5)
            if failCount == 10: 
                raise
            continue
    elem = driver.find_element_by_id("ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_LocationTextBox")
    # http://www.netstate.com/states/geography/pa_geography.htm
    elem.send_keys(zipCode) # The geographic center of Pennsylvania
    select = Select(driver.find_element_by_id("ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_ddlMiles"))
    select.select_by_visible_text("25")
    button = driver.find_element_by_id("ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_imgbtn_Locate")
    button.click()
    return driver


def show_time(time):
    hours = time//3600
    minutes = (time//60)%60
    seconds = time%60
    print ("program runs for "+str(int(hours))+" hours, "+str(int(minutes))+" minutes, "+str(seconds)+" seconds.")

    
if __name__ == '__main__':
    saveFileName = "nra"
    crawlUrl = 'http://findnra.nra.org/'
    startTime = time.time()
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(crawlUrl)
    open_url_by_se(driver)
    driver.close()
    elapsedTime = time.time() - startTime
    show_time(elapsedTime)   
    print('all finish! ')