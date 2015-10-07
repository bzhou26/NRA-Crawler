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

# swithch key
DUPFILTER = 0 # avoid duplicated information, change it to 1, or leave it 0 if you need original information
PROVINCE = "" # if you want to get all, change it to ''


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
    # Places to Shoot
    ptsPageCtrlId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_NationalRegistryShootPagerPanel"
    ptsNtPageId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg1NextPage"
    ptsTableId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg1"
    try:
        for i in chooseList:
            driver.find_element_by_id(checkboxId+i).click()
    except Exception as e:
        print(e)
    elem = driver.find_element_by_id(formId)
    # http://www.netstate.com/states/geography/pa_geography.htm
    elem.send_keys("16823") # The geographic center of Pennsylvania
    select = Select(driver.find_element_by_id(rangId))
    select.select_by_visible_text("200")
    button = driver.find_element_by_id(srchBtId)
    button.click()
    # handle bft
    #bftRslt = get_all_bft(driver, bftPageCtrlId, bftNtPageId)
    #write_to_excel(bftRslt, 'excelTest111_PA_filted.xlsx', 'Basic Firearms Training')
    # handle pts
    ptsRslt = crawl_one_category(driver, ptsPageCtrlId, ptsNtPageId, ptsTableId, 0)
    #write_to_excel(ptsRslt, 'ptsexcelTest.xlsx', 'Place to Shoot')    
    return

# list/set/tuple 
def write_to_file(content,saveFileName):
    with open(saveFileName,'a') as f:
        for el in content:
            f.write(el)
    #text = content #.encode("utf-8")


def write_to_excel(content,saveFileName,category):
    #content [(name, adrs, PA, Postcode, geo),...]
    global row
    workbook = xlsxwriter.Workbook(saveFileName)
    worksheet = workbook.add_worksheet('NRA Address')
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


# find Basic Firearms Training
def find_bft(soup):
    global bft_number
    bftTitleId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg2_lblClassType_"
    resultList = []
    for i in range(15):
        bft = soup.find(id='ET'+str(bft_number))
        if bft != None:    
            adrsList = info_catch_bft(bft.get_text())
            if adrsList != None:
                bftTitle = soup.find(id = bftTitleId+str(i)).get_text()
                adrsList[0] = bftTitle
                resultList.append(adrsList)
        bft_number += 1  
    return resultList 


# find Place to Shoot
def find_pst(soup):
    global pts_number
    tableId = "ContentPlaceHolderDefault_DivMainCPH_ctl01_NRANearYouControl_2_dg1"
    table = soup.find(id = tableId)
    allItem = table.find_all(class_= "tableItem")
    resultList = []
    for el in allItem:
        item = []
        courseNameList = el.find(class_="findCourse").get_text().split()
        courseName = " ".join(courseNameList)
        #print(courseName)
        pts = el.find(id = "RANGE" + str(pts_number))
        if pts != None:
            adrsList = info_catch_pts(pts.get_text())
            if adrsList != None:
                adrsList [0] = courseName
                resultList.append(adrsList)
        pts_number += 1
    return resultList

def search_page(soup, tableId, dataTag, omitNumber):
    global pts_number
    global bft_number
    table = soup.find(id = tableId)
    allItem = table.find_all(class_= "tableItem")
    resultList = []
    for el in allItem:
        item = []
        courseNameList = el.find(class_="findCourse").get_text().split()
        courseName = " ".join(courseNameList)
        #print(courseName)
        pts = el.find(id = "RANGE" + str(pts_number))
        if pts != None:
            adrsList = info_catch_pts(pts.get_text())
            if adrsList != None:
                adrsList [0] = courseName
                resultList.append(adrsList)
                
        pts_number += 1
        
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
            print ("cannot find Geolation for Address: "+adrsCnt+"\n"+"please find it manually, on row: "+str(rowCount))
        for item in el:
            newItem.append(item)
        newItem.append(gps)
        geoAdrsList.append(newItem)
    return geoAdrsList


def get_all_bft(driver, pageCtrlId, ntPageId):
    currentPage = -2
    totalPage = -1
    rsltList = []
    geoChcekList = []
    while currentPage < totalPage:
        content = driver.page_source
        soup = bs4.BeautifulSoup(content) 
        pageCtrl = soup.find(id=pageCtrlId)
        if pageCtrl == None:
            time.sleep(10)
            print("try to reload "+str(currentPage+1))
            continue
        try:
            pageContent = pageCtrl.get_text()
        except Exception as err:
            print("problem on page "+str(currentPage+1))
            continue
        pageList = pageContent.split()
        currentPage = int(pageList[1].replace('of', ''))
        totalPage = int(pageList[2])
        onePgAdrsList = find_bft(soup)
        geoedList = geocoding(onePgAdrsList)        
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
        if currentPage == totalPage:
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


def get_all_pts(driver, pageCtrlId, ntPageId):
    currentPage = -2
    totalPage = -1
    rsltList = []
    geoChcekList = []
    while currentPage < totalPage:
        content = driver.page_source
        soup = bs4.BeautifulSoup(content) 
        pageCtrl = soup.find(id=pageCtrlId)
        if pageCtrl == None:
            time.sleep(10)
            print("try to reload "+str(currentPage+1))
            continue
        try:
            pageContent = pageCtrl.get_text()
        except Exception as err:
            print("problem on page "+str(currentPage+1))
            continue
        pageList = pageContent.split()
        currentPage = int(pageList[1].replace('of', ''))
        totalPage = int(pageList[2])
        onePgAdrsList = find_pst(soup)
        geoedList = geocoding(onePgAdrsList)        
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
        if currentPage == totalPage:
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


def crawl_one_category(driver, pageCtrlId, ntPageId, tableId, omitNumber):
    currentPage = -2
    totalPage = -1
    rsltList = []
    geoChcekList = []
    while currentPage < totalPage:
        content = driver.page_source
        soup = bs4.BeautifulSoup(content) 
        pageCtrl = soup.find(id=pageCtrlId)
        if pageCtrl == None:
            time.sleep(10)
            print("try to reload "+str(currentPage+1))
            continue
        try:
            pageContent = pageCtrl.get_text()
        except Exception as err:
            print("problem on page "+str(currentPage+1))
            continue
        pageList = pageContent.split()
        currentPage = int(pageList[1].replace('of', ''))
        totalPage = int(pageList[2])
        onePgAdrsList = search_page(soup, tableId, omitNumber)
        geoedList = geocoding(onePgAdrsList)        
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
        if currentPage == totalPage:
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


#def info_catch_pts(item):
    #global PROVINCE
    #itemList = item.split()
    #etAdrs = ''
    #etPost = []
    #j = 0
    #length = len(itemList)
    #while j < length:
        #if itemList[j] != ',':
            #etAdrs += (' '+itemList[j])
        #else:
            #for k in range (1,3):
                #etPost.append(itemList[j+k])
            #break
        #j += 1
    #if PROVINCE == '' or PROVINCE == etPost[0]:
        #return [None, etAdrs, etPost[0], etPost[1]]
    #else:
        #return None


#def info_catch_bft(item):
    #global PROVINCE
    #itemList = item.split()
    #for i in range(2):
        #itemList.pop(0)
    #etAdrs = ''
    #etPost = []
    #j = 0
    #length = len(itemList)
    #while j < length:
        #if itemList[j] != ',':
            #etAdrs += (' '+itemList[j])
        #else:
            #for k in range (1,3):
                #etPost.append(itemList[j+k])
            #break
        #j += 1
    #if PROVINCE == '' or PROVINCE == etPost[0]:
        #return [None, etAdrs, etPost[0], etPost[1]]
    #else:
        #return None
    
    
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
        
    
if __name__ == '__main__':
    saveFileName = "nra"
    crawlUrl = 'http://findnra.nra.org/'
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(crawlUrl)
    open_url_by_se(driver)
    driver.close()
    print('all finish! ')