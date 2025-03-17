from typing import Optional
from typing import List
from unittest import expectedFailure
from fastapi import FastAPI, Form , Request, status, Depends , HTTPException,File, UploadFile
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import secrets
from selenium import webdriver
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pandas as pd
import requests
import json
import urllib.parse
import gspread
import pandas as pd
from re import sub,finditer
import sys
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
from bs4 import BeautifulSoup
import openpyxl
from time import sleep
import emoji
import ast

import sys
import traceback
import os
import json
#from google.api_core.client_options import ClientOptions
#from google.cloud import automl_v1

from pathlib import Path
import shutil
import time
import phonenumbers


def inline_text_payload(file_path):
    with open(file_path, 'rb') as ff:
        content = ff.read()
    return {'text_snippet': {'content': content, 'mime_type': 'text/plain'} }

def pdf_payload(file_path):
    return {'document': {'input_config': {'gcs_source': {'input_uris': [file_path] } } } }


class filter(BaseModel):
    column: Optional[str] = None
    rec: Optional[str] = None


app = FastAPI()
security = HTTPBasic()


WHITELISTED_IPS = []

@app.middleware('http')
async def validate_ip(request: Request, call_next):
    # Get client IP
    ip = str(request.client.host)
    
    # Check if IP is allowed
    if ip not in WHITELISTED_IPS:
        data = {
            'message': f'IP {ip} is not allowed to access from this server'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Proceed if IP is allowed
    return await call_next(request)
    

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "")
    correct_password = secrets.compare_digest(credentials.password, "")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/lembaran/{spreadsheet}/{sheet}")
async def create_item(spreadsheet,sheet, filter: Optional[List[filter]]= None,username= Depends(get_current_username) ):
    gc = gspread.service_account(filename='app/')
    #sh = gc.open("Task Database")
    sh = gc.open_by_key(spreadsheet)
    allPreData=pd.DataFrame(sh.worksheet(sheet).get_all_values())
    data=pd.DataFrame(allPreData)
    data_on_to_go=data
    if filter:
        column=[]
        rec=[]
        for r in filter:
            column.append(r.column)
            rec.append(r.rec)
        collection_filter=pd.DataFrame(list(zip(column, rec)),
                columns =['column', 'rec'])
        l=0
        while l < collection_filter.shape[0]:
            header=data.loc[0][data.loc[0]==collection_filter["column"][l]].index.values[0]
            print(header)
            data_on_to_go=data_on_to_go[data_on_to_go[header]==str(collection_filter["rec"][l])]
            l+=1
        data_on_to_go.columns=data.loc[0].to_list()
        data_on_to_go=data_on_to_go.reset_index(drop=True)
        data_on_to_go=data_on_to_go.to_json(orient='records')
        p=json.loads('{"' +"".join(sheet.split())+'":' +data_on_to_go +'}')
        return p
    else:
        data_on_to_go=data_on_to_go.tail(1000)
        lits=[]
        for kat in data.loc[0].to_list():
            if ' ' in kat:
                kat = sub(r"(_|-)+", " ", kat).title().replace(" ", "")
                kat = ''.join([kat[0].lower(), kat[1:]])
            lits.append(kat)
        data_on_to_go.columns=lits
        data_on_to_go.reset_index(inplace=True)
        data_on_to_go=data_on_to_go.to_json(orient='records')
        p=json.loads('{"' +"".join(sheet.split())+'":' +data_on_to_go +'}')
        return p

@app.get("/")
async def test():
    return RedirectResponse("https://youtu.be/dQw4w9WgXcQ?t=0")


@app.post("/v1/application")
async def aeon(applicant_title:str=Form(...),applicant_name:str=Form(...),applicant_email:str=Form(None),applicant_phone_code:str=Form(...),applicant_phone_number:int=Form(...),is_aeon_membership:str=Form(...),is_aeon_card_holder:str=Form(...),nric_no:str=Form(...),type_other_identification_no:Optional[str]=Form(None),other_identification_no:Optional[str]=Form(None),applicant_gender:str=Form(...),applicant_race:str=Form(...),applicant_race_other:Optional[str]=Form(None),citizenship_status:str=Form(...),marital_status:str=Form(...),dependents:Optional[int]=Form(None),identityAuth:str=Form('NO'),permanent_address1:str=Form(...),permanent_address2:Optional[str]=Form('-'),permanent_address3:Optional[str]=Form('-'),permanent_postcode:int=Form(...),is_same_permanentaddress:str=Form(...),residential_address1:Optional[str]=Form(''),residential_address2:Optional[str]=Form(''),residential_address3:Optional[str]=Form(''),residential_postcode:int=Form(None),residency_status:str=Form(...),residency_status_other:Optional[str]=Form(None),residentialPhoneCode:Optional[str]=Form(None),residential_phone_number:int=Form(None),longResidence:int=Form(...),longResidenceMonth:int=Form(...),emergency_title:str=Form(...),emergency_name:str=Form(...),emergency_applicant_relationship:str=Form(...),emergency_address1:str=Form(...),emergency_address2:Optional[str]=Form('-'),emergency_address3:Optional[str]=Form('-'),emergency_postcode:int=Form(...),emergency_phone_number:str=Form(...),occupation_type:str=Form(...),employment_type:str=Form(...),position:str=Form(...),position_other:Optional[str]=Form(None),department:str=Form(...),department_other:Optional[str]=Form(None),business_nature:str=Form(...),business_nature_other:Optional[str]=Form(None),year_work:int=Form(...),months_work:int=Form(...),employer_name:str=Form(...),employer_address1:str=Form(...),employer_address2:Optional[str]=Form('-'),employer_address3:Optional[str]=Form('-'),employer_postcode:int=Form(...),employer_phone_code:str=Form(...),employer_phone_number:int=Form(...),ext_number:Optional[str]=Form(0),gross_salary:float=Form(...),net_salary:float=Form(...),day_receive_salary:int=Form(...),is_other_income:Optional[str]=Form(None),other_income_amount:int=Form(None),source_other_income:Optional[str]=Form(None),source_other_income__other:Optional[str]=Form(None),existing_loans_non_bank:str=Form(...),monthly_repayment:str=Form(0),repayment_source:Optional[str]=Form('-'),isWithJointApplicant:str=Form(...),product_price:int=Form(...),down_payment:float=Form(...),promotionVoucherAmount:int=Form(None),tenure:int=Form(...),promotion_code:Optional[str]=Form(None),initial_payment:str=Form(...),mailing_address:str=Form(...),payment_details:str=Form(...),payment_method:str=Form(...),is_salary_account:Optional[str]=Form(None),bank:str=Form(...),account_number:int=Form(...),account_holder_name:str=Form(...),nric_document:UploadFile = File(None),income_document:UploadFile = File(None),other_document:UploadFile = File(None),application_remarks:Optional[str]=Form(...),product_interest_rate:float=Form(...),username: str = Depends(get_current_username)):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.set_capability('unhandledPromptBehavior', 'accept')
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Remote(command_executor='http://chrome:4444/wd/hub',options=options, keep_alive=True)
    try:
        driver.get('')
        username = driver.find_element_by_id("")
        username.send_keys('')
        password = driver.find_element_by_id("")
        password.send_keys('')
        password.send_keys(Keys.ENTER)

        #BAHGAIAN NAVIGATION
        driver.get('')
        wait = WebDriverWait(driver, 50)
        driver.find_elements_by_css_selector('#agreeNo')[0].click()
        time.sleep(10)
        driver.switch_to.window(driver.window_handles[1])

        name_of_productCategory=driver.find_element_by_name('lens_FC_SNS_PROD_CAT_EP') #Cari ID untuk jenis barang
        id_of_productCategory = name_of_productCategory.get_attribute("data-select-id")
        select_productCategory='#select-options-'+id_of_productCategory+' > li:nth-child(2) > span'
        driver.find_element_by_css_selector('#PROD_CTGY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(9) > div > div > input').click()
        wait = WebDriverWait(driver, 10)
        input_productCategory = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_productCategory)))
        input_productCategory.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        aggree = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#TNCF-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(8) > div > div > div > div > label")))
        aggree.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(13) > div:nth-child(1) > div > input')))
        name_of_title=driver.find_element_by_name('lens_FC_SNS_TITLE') #Cari ID untuk gelaran
        id_of_title = name_of_title.get_attribute("data-select-id")
        if applicant_title == 'MR':
            select_title='#select-options-'+id_of_title+' > li:nth-child(2) > span'
        elif applicant_title == 'MS':
            select_title='#select-options-'+id_of_title+' > li:nth-child(3) > span'
        elif applicant_title == 'MADAM':
            select_title='#select-options-'+id_of_title+' > li:nth-child(4) > span'
        elif applicant_title == 'MRS':
            select_title='#select-options-'+id_of_title+' > li:nth-child(5) > span'
        elif applicant_title == 'DR':
            select_title='#select-options-'+id_of_title+' > li:nth-child(6) > span'
        elif applicant_title == 'DATIN':
            select_title='#select-options-'+id_of_title+' > li:nth-child(7) > span'
        elif applicant_title == 'DATO':
            select_title='#select-options-'+id_of_title+' > li:nth-child(8) > span'
        elif applicant_title == 'YB':
            select_title='#select-options-'+id_of_title+' > li:nth-child(9) > span'
        elif applicant_title == 'TAN SRI':
            select_title='#select-options-'+id_of_title+' > li:nth-child(10) > span'
        driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(13) > div:nth-child(1) > div > input').click()
        wait = WebDriverWait(driver, 10)
        input_title = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_title)))
        input_title.click()
        driver.find_element_by_css_selector('#lens_FC_SNS_NAME').send_keys(applicant_name) #Nama
        driver.find_element_by_css_selector('#lens_FC_SNS_EMAIL').send_keys(applicant_email) #Emel
        name_of_phoneCode=driver.find_element_by_name('lens_FC_SNS_PH_NO_CCODE') #Cari ID untuk kod phone
        id_of_phoneCode = name_of_phoneCode.get_attribute("data-select-id")
        if applicant_phone_code == '60-MY':
            select_phoneCode='#select-options-'+id_of_phoneCode+' > li:nth-child(2) > span'
        elif applicant_phone_code == '65-SG':
            select_phoneCode='#select-options-'+id_of_phoneCode+' > li:nth-child(3) > span'
        print(select_phoneCode)
        driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div.input-container.row.country-code__wrapper > div.input-field.col-xs-12.col-md-6.country-code__container > div > div > input').click()
        wait = WebDriverWait(driver, 10)
        input_phoneCode = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_phoneCode)))
        input_phoneCode.click()
        driver.find_element_by_css_selector('#lens_FN_SNS_PH_NO').send_keys(applicant_phone_number)
        if is_aeon_membership =='YES':
            driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div > div > div > div:nth-child(1) > label').click()
        elif is_aeon_membership =='NO':
            driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div > div > div > div:nth-child(2) > label').click()
        if is_aeon_card_holder =='YES':
            driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div > div > div > div:nth-child(1) > label').click()
        elif is_aeon_card_holder =='NO':
            driver.find_element_by_css_selector('#CNTT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div > div > div > div:nth-child(2) > label').click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#lens_FC_SNS_NRIC')))
        driver.find_element_by_css_selector('#lens_FC_SNS_NRIC').send_keys(nric_no)
        org3=driver.find_element_by_name('lens_FC_SNS_OTH_IC') #Cari ID IC LAIN
        val3 = org3.get_attribute("data-select-id")
        try:
            if type_other_identification_no[0]:
                if type_other_identification_no =='OLD IC':
                    cariID3='#select-options-'+val3+' > li:nth-child(2) > span'
                elif type_other_identification_no =='PASSPORT NUMBER':
                    cariID3='#select-options-'+val3+' > li:nth-child(3) > span'
                elif type_other_identification_no =='POLICE/MILITARY ID':
                    cariID3='#select-options-'+val3+' > li:nth-child(4) > span'
        except:
            cariID3=None
        if cariID3:
            driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(14) > div:nth-child(1) > div > input').click()
            wait = WebDriverWait(driver, 10)
            cl3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID3)))
            cl3.click()
            driver.find_element_by_css_selector('#lens_FC_SNS_OLD_IC_NO').send_keys(other_identification_no)
        org4=driver.find_element_by_name('lens_FC_SNS_GENDER') #Cari Jantina
        val4 = org4.get_attribute("data-select-id")
        if applicant_gender =='MALE':
            cariID4='#select-options-'+val4+' > li:nth-child(2) > span'
        elif applicant_gender =='FEMALE':
            cariID4='#select-options-'+val4+' > li:nth-child(3) > span'
        driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div > div > input').click()
        wait = WebDriverWait(driver, 10)
        cl4 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID4)))
        cl4.click()
        org5=driver.find_element_by_name('lens_FC_SNS_RACE') #Cari Bangsa
        val5 = org5.get_attribute("data-select-id")
        if applicant_race =='MALAY':
            cariID5='#select-options-'+val5+' > li:nth-child(2) > span'
        elif applicant_race =='CHINESE':
            cariID5='#select-options-'+val5+' > li:nth-child(3) > span'
        elif applicant_race =='INDIAN':
            cariID5='#select-options-'+val5+' > li:nth-child(4) > span'
        elif applicant_race =='OTHERS':
            cariID5='#select-options-'+val5+' > li:nth-child(5) > span'
        driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div:nth-child(1) > div > input').click()
        wait = WebDriverWait(driver, 10)
        cl5 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID5)))
        cl5.click()
        if applicant_race=='OTHERS':
            driver.find_element_by_css_selector('#lens_FC_SNS_RACE_OTH').send_keys(applicant_race_other)          
        if citizenship_status =='BUMIPUTERA':
            driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(18) > div > div > div > div:nth-child(1) > label ').click()
        elif citizenship_status =='NON-BUMIPUTERA':
            driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(18) > div > div > div > div:nth-child(2) > label').click()
        org6=driver.find_element_by_name('lens_FC_SNS_MARITAL') #Cari status perkahwinan
        val6 = org6.get_attribute("data-select-id")
        if marital_status =='MARRIED':
            cariID6='#select-options-'+val6+' > li:nth-child(2) > span'
        elif marital_status =='SINGLE':
            cariID6='#select-options-'+val6+' > li:nth-child(3) > span'
        elif marital_status =='DIVORCED':
            cariID6='#select-options-'+val6+' > li:nth-child(4) > span'
        elif marital_status =='WIDOWED':
            cariID6='#select-options-'+val6+' > li:nth-child(5) > span'
        driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(19) > div:nth-child(1) > div > input').click()
        wait = WebDriverWait(driver, 10)
        cl6 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID6)))
        cl6.click()
        time.sleep(8)
        if not marital_status=='SINGLE':
            org7=driver.find_element_by_name('lens_FN_SNS_DEPEND_NO') #Cari bilangan tanggungan
            val7 = org7.get_attribute("data-select-id")
            if dependents ==0:
                cariID7='#select-options-'+val7+' > li:nth-child(2) > span'
            elif dependents ==1:
                cariID7='#select-options-'+val7+' > li:nth-child(3) > span'
            elif dependents ==2:
                cariID7='#select-options-'+val7+' > li:nth-child(4) > span'
            elif dependents ==3:
                cariID7='#select-options-'+val7+' > li:nth-child(5) > span'
            elif dependents ==4:
                cariID7='#select-options-'+val7+' > li:nth-child(6) > span'
            elif dependents ==5:
                cariID7='#select-options-'+val7+' > li:nth-child(7) > span'
            elif dependents ==6:
                cariID7='#select-options-'+val7+' > li:nth-child(8) > span'
            elif dependents ==7:
                cariID7='#select-options-'+val7+' > li:nth-child(9) > span'
            elif dependents ==8:
                cariID7='#select-options-'+val7+' > li:nth-child(10) > span'
            driver.find_element_by_css_selector('#PRSL_DTLS_MY-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(19) > div:nth-child(3) > div > input').click()
            wait = WebDriverWait(driver, 10)
            cl7 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID7)))
            cl7.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#EKYC_QUE-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(9) > div > div > div > div:nth-child(1) > label')))
        if identityAuth =='YES':
            driver.find_element_by_css_selector('#EKYC_QUE-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(9) > div > div > div > div:nth-child(1) > label').click()
        elif identityAuth =='NO':
            driver.find_element_by_css_selector('#EKYC_QUE-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(9) > div > div > div > div:nth-child(2) > label').click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#lens_FC_SNS_PADDR1')))
        print("personal details selesai")
        driver.find_element_by_css_selector('#lens_FC_SNS_PADDR1').send_keys(permanent_address1)
        driver.find_element_by_css_selector('#lens_FC_SNS_PADDR2').send_keys(permanent_address2)
        driver.find_element_by_css_selector('#lens_FC_SNS_PADDR3').send_keys(permanent_address3)
        poscode_ = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#PRMT_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span')))
        poscode_.click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        wait = WebDriverWait(driver, 10)
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(permanent_postcode)
        postcodeEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        postcodeEnter.send_keys(Keys.ENTER)
        time.sleep(3)
        if is_same_permanentaddress=='YES':
            driver.find_element_by_css_selector('#PRMT_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div > div > div > div:nth-child(1) > label').click()
        elif is_same_permanentaddress=='NO':
            driver.find_element_by_css_selector('#PRMT_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div > div > div > div:nth-child(2) > label').click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#lens_FC_SNS_RADDR1')))
        print("permanent address selesai")
        if is_same_permanentaddress=='NO':
            driver.find_element_by_css_selector('#lens_FC_SNS_RADDR1').send_keys(residential_address1)
            driver.find_element_by_css_selector('#lens_FC_SNS_RADDR2').send_keys(residential_address2)
            driver.find_element_by_css_selector('#lens_FC_SNS_RADDR3').send_keys(residential_address3)
            wait = WebDriverWait(driver, 10)
            poscode_1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span')))
            #driver.find_element_by_css_selector(cariID1).click()
            poscode_1.click()
            #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
            driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
            driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(residential_postcode)
            postcodeEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
            postcodeEnter.send_keys(Keys.ENTER)   
            time.sleep(3)
        org8=driver.find_element_by_name('lens_FC_SNS_ROWNERSHIP') #Cari status residensi
        val8 = org8.get_attribute("data-select-id")
        if residency_status =='EMPLOYER\'S QUARTERS':
            cariID8='#select-options-'+val8+' > li:nth-child(2) > span'
        elif residency_status =='FAMILY HOME':
            cariID8='#select-options-'+val8+' > li:nth-child(3) > span'
        elif residency_status =='LIVE WITH PARENTS/RELATIVES':
            cariID8='#select-options-'+val8+' > li:nth-child(4) > span'
        elif residency_status =='OWN MORTGAGED':
            cariID8='#select-options-'+val8+' > li:nth-child(5) > span'
        elif residency_status =='OWN NOT MORTGAGED':
            cariID8='#select-options-'+val8+' > li:nth-child(6) > span'
        elif residency_status =='RENTED':
            cariID8='#select-options-'+val8+' > li:nth-child(7) > span'
        elif residency_status =='OTHERS':
            cariID8='#select-options-'+val8+' > li:nth-child(8) > span'
        driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div:nth-child(1) > div > input').click()
        wait = WebDriverWait(driver, 10)
        cl8 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID8)))
        cl8.click()
        if residency_status =='OTHERS':
            driver.find_element_by_css_selector('#lens_FC_SNS_ROWNERSHIP_OTH').send_keys(residency_status_other)
        if residentialPhoneCode:
            org9=driver.find_element_by_name('lens_FC_SNS_TEL_HOME_CCODE') #Cari ID untuk kod phone
            val9 = org9.get_attribute("data-select-id")
            if residentialPhoneCode == 'MY':
                cariID9='#select-options-'+val9+' > li:nth-child(2) > span'
            elif residentialPhoneCode == 'SG':
                cariID9='#select-options-'+val9+' > li:nth-child(3) > span'
            driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div.input-container.row.country-code__wrapper > div.input-field.col-xs-12.col-md-6.country-code__container > div > div > input').click()
            wait = WebDriverWait(driver, 10)
            cl9 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID9)))
            cl9.click()
            driver.find_element_by_css_selector('#lens_FN_SNS_TEL_HOME').send_keys(residential_phone_number)
        driver.find_element_by_css_selector('#lens_FN_SNS_LENGTH_STAY_YR').send_keys(longResidence)

        org10=driver.find_element_by_name('lens_FN_SNS_LENGTH_STAY_MTH') #Cari ID untuk berapa lama bulan tinggal
        val10 = org10.get_attribute("data-select-id")
        if longResidenceMonth ==0:
            cariID10='#select-options-'+val10+' > li:nth-child(2) > span'
        elif longResidenceMonth ==1:
            cariID10='#select-options-'+val10+' > li:nth-child(3) > span'
        elif longResidenceMonth ==2:
            cariID10='#select-options-'+val10+' > li:nth-child(4) > span'
        elif longResidenceMonth ==3:
            cariID10='#select-options-'+val10+' > li:nth-child(5) > span'
        elif longResidenceMonth ==4:
            cariID10='#select-options-'+val10+' > li:nth-child(6) > span'
        elif longResidenceMonth ==5:
            cariID10='#select-options-'+val10+' > li:nth-child(7) > span'
        elif longResidenceMonth ==6:
            cariID10='#select-options-'+val10+' > li:nth-child(8) > span'
        elif longResidenceMonth ==7:
            cariID10='#select-options-'+val10+' > li:nth-child(9) > span'
        elif longResidenceMonth ==8:
            cariID10='#select-options-'+val10+' > li:nth-child(10) > span'
        elif longResidenceMonth ==9:
            cariID10='#select-options-'+val10+' > li:nth-child(11) > span'
        elif longResidenceMonth ==10:
            cariID10='#select-options-'+val10+' > li:nth-child(12) > span'
        elif longResidenceMonth ==11:
            cariID10='#select-options-'+val10+' > li:nth-child(13) > span'
        driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(19) > div:nth-child(3) > div > input').click()
        wait = WebDriverWait(driver, 10)
        cl10 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID10)))
        cl10.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        #time.sleep(10)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMRY_CNTS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(14) > div:nth-child(1) > div > input')))
        print("residential address selesai")
        org11=driver.find_element_by_name('lens_FC_SNS_EMER_TITLE') #Cari ID untuk gelaran
        val11 = org11.get_attribute("data-select-id")
        if emergency_title == 'MR':
            cariID11='#select-options-'+val11+' > li:nth-child(2) > span'
        elif emergency_title == 'MS':
            cariID11='#select-options-'+val11+' > li:nth-child(3) > span'
        elif emergency_title == 'MADAM':
            cariID11='#select-options-'+val11+' > li:nth-child(4) > span'
        elif emergency_title == 'MRS':
            cariID11='#select-options-'+val11+' > li:nth-child(5) > span'
        elif emergency_title == 'DR':
            cariID11='#select-options-'+val11+' > li:nth-child(6) > span'
        elif emergency_title == 'DATIN':
            cariID11='#select-options-'+val11+' > li:nth-child(7) > span'
        elif emergency_title == 'DATO':
            cariID11='#select-options-'+val11+' > li:nth-child(8) > span'
        elif emergency_title == 'YB':
            cariID11='#select-options-'+val11+' > li:nth-child(9) > span'
        elif emergency_title == 'TAN SRI':
            cariID11='#select-options-'+val11+' > li:nth-child(10) > span'
        driver.find_element_by_css_selector('#EMRY_CNTS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(14) > div:nth-child(1) > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl11 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID11)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl11.click()
        driver.find_element_by_css_selector('#lens_FC_SNS_EMER_NAME').send_keys(emergency_name)
        org12=driver.find_element_by_name('lens_FC_SNS_EMER_RELATION') #Cari ID untuk perkaitan kontak
        val12 = org12.get_attribute("data-select-id")
        if emergency_applicant_relationship == 'FATHER/MOTHER':
            cariID12='#select-options-'+val12+' > li:nth-child(2) > span'
        elif emergency_applicant_relationship == 'HUSBAND/WIFE':
            cariID12='#select-options-'+val12+' > li:nth-child(3) > span'
        elif emergency_applicant_relationship == 'BROTHER/SISTER':
            cariID12='#select-options-'+val12+' > li:nth-child(4) > span'
        elif emergency_applicant_relationship == 'CHILD':
            cariID12='#select-options-'+val12+' > li:nth-child(5) > span'
        elif emergency_applicant_relationship == 'RELATIVE':
            cariID12='#select-options-'+val12+' > li:nth-child(6) > span'
        elif emergency_applicant_relationship == 'FRIEND':
            cariID12='#select-options-'+val12+' > li:nth-child(7) > span'
        driver.find_element_by_css_selector('#EMRY_CNTS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl12 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID12)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl12.click()
        driver.find_element_by_css_selector('#lens_FC_SNS_EMER_ADDR1').send_keys(emergency_address1)
        driver.find_element_by_css_selector('#lens_FC_SNS_EMER_ADDR2').send_keys(emergency_address2)
        driver.find_element_by_css_selector('#lens_FC_SNS_EMER_ADDR3').send_keys(emergency_address3)
        wait = WebDriverWait(driver, 10)
        poscode_2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMRY_CNTS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(19) > div > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        poscode_2.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(emergency_postcode)
        postcodeEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        postcodeEnter.send_keys(Keys.ENTER)
        time.sleep(3)
        driver.find_element_by_css_selector('#lens_FN_SNS_EMER_MOBILE_NO').send_keys(emergency_phone_number)
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(1) > div > input')))
        org13=driver.find_element_by_name('lens_FC_SNS_OCC_TYPE') #Cari ID untuk gelaran
        val13 = org13.get_attribute("data-select-id")
        if occupation_type == 'EMPLOYED':
            cariID13='#select-options-'+val13+' > li:nth-child(2) > span'
        elif occupation_type == 'SELF-EMPLOYED':
            cariID13='#select-options-'+val13+' > li:nth-child(3) > span'
        driver.find_element_by_css_selector('#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(1) > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl13 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID13)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl13.click()
        time.sleep(8)
        print("emergency contact selesai")
        if occupation_type == 'EMPLOYED':
            org13_1=driver.find_element_by_name('lens_FC_SNS_EMPSTATUS') #Cari ID untuk employed
            val13_1 = org13_1.get_attribute("data-select-id")
            print(val13_1)
            #employementType='PRIVATE SECTOR EMPLOYEE'
            if employment_type == 'GOVERNMENT EMPLOYEE':
                cariID13_1='#select-options-'+val13_1+' > li:nth-child(2) > span'
            elif employment_type == 'PRIVATE SECTOR EMPLOYEE':
                cariID13_1='#select-options-'+val13_1+' > li:nth-child(3) > span'
            elif employment_type == 'REPORTING ENTITY (RE) EMPLOYEE':
                cariID13_1='#select-options-'+val13_1+' > li:nth-child(4) > span'
            print(cariID13_1)
            driver.find_element_by_css_selector('#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(3) > div > input').click()
            #time.sleep(3)
            wait = WebDriverWait(driver, 10)
            cl13_1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID13_1)))
            #driver.find_element_by_css_selector(cariID1).click()
            cl13_1.click()

        if occupation_type == 'SELF-EMPLOYED':
            org13_2=driver.find_element_by_name('lens_FC_SNS_EMPSTATUS') #Cari ID untuk employed
            val13_2 = org13_2.get_attribute("data-select-id")
            print(val13_2)
            employment_type='SELF-EMPLOYED'
            if employment_type == 'SELF-EMPLOYED':
                cariID13_2='#select-options-'+val13_2+' > li:nth-child(2) > span'
            elif employment_type == 'FREELANCE':
                cariID13_2='#select-options-'+val13_2+' > li:nth-child(3) > span'
            elif employment_type == 'OUTSIDE LABOUR FORCE':
                cariID13_2='#select-options-'+val13_2+' > li:nth-child(4) > span'
            print(cariID13_2)
            #EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(3) > div > input
            #EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(3) > div > input
            driver.find_element_by_css_selector('#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div:nth-child(3) > div > input').click()
            #time.sleep(3)
            wait = WebDriverWait(driver, 10)
            cl13_2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID13_2)))
            #driver.find_element_by_css_selector(cariID1).click()
            cl13_2.click()
        wait = WebDriverWait(driver, 10)
        position_css = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div:nth-child(1) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        position_css.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(position)
        positionEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        positionEnter.send_keys(Keys.ENTER)
        if position=='OTHERS':
            driver.find_element_by_css_selector('#lens_FC_SNS_POSITION_OTH').send_keys(position_other)
        wait = WebDriverWait(driver, 10)
        department_css = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div:nth-child(1) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        department_css.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(department)
        departmentEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        departmentEnter.send_keys(Keys.ENTER)
        if department=='OTHERS':
            driver.find_element_by_css_selector('#lens_FC_SNS_DEPARTMENT_OTH').send_keys(department_other)
        wait = WebDriverWait(driver, 10)
        businessNature_css = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(18) > div:nth-child(1) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        businessNature_css.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(business_nature)
        businessNatureEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        businessNatureEnter.send_keys(Keys.ENTER)
        if business_nature=='OTHERS':
            driver.find_element_by_css_selector('#lens_FC_SNS_BIZ_NATURE_OTH').send_keys(business_nature_other)
        driver.find_element_by_css_selector('#lens_FI_SNS_SVC_YRS_NO').send_keys(year_work)
        org14=driver.find_element_by_name('lens_FN_SNS_SVC_MTH_NO') #Cari ID untuk bulan bekerja
        val14 = org14.get_attribute("data-select-id")
        if months_work ==0:
            cariID14='#select-options-'+val14+' > li:nth-child(2) > span'
        elif months_work ==1:
            cariID14='#select-options-'+val14+' > li:nth-child(3) > span'
        elif months_work ==2:
            cariID14='#select-options-'+val14+' > li:nth-child(4) > span'
        elif months_work ==3:
            cariID14='#select-options-'+val14+' > li:nth-child(5) > span'
        elif months_work ==4:
            cariID14='#select-options-'+val14+' > li:nth-child(6) > span'
        elif months_work ==5:
            cariID14='#select-options-'+val14+' > li:nth-child(7) > span'
        elif months_work ==6:
            cariID14='#select-options-'+val14+' > li:nth-child(8) > span'
        elif months_work ==7:
            cariID14='#select-options-'+val14+' > li:nth-child(9) > span'
        elif months_work ==8:
            cariID14='#select-options-'+val14+' > li:nth-child(10) > span'
        elif months_work ==9:
            cariID14='#select-options-'+val14+' > li:nth-child(11) > span'
        elif months_work ==10:
            cariID14='#select-options-'+val14+' > li:nth-child(12) > span'
        elif months_work ==11:
            cariID14='#select-options-'+val14+' > li:nth-child(13) > span'
        driver.find_element_by_css_selector('#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(19) > div:nth-child(3) > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl14= wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID14)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl14.click()
        driver.find_element_by_css_selector('#lens_FC_SNS_EMPLOYER').send_keys(employer_name)
        driver.find_element_by_css_selector('#lens_FC_SNS_EMPADDR1').send_keys(employer_address1)
        driver.find_element_by_css_selector('#lens_FC_SNS_EMPADDR2').send_keys(employer_address2)
        driver.find_element_by_css_selector('#lens_FC_SNS_EMPADDR3').send_keys(employer_address3)
        wait = WebDriverWait(driver, 10)
        poscode_3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(24) > div > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        poscode_3.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys(employer_postcode)
        postcodeEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        postcodeEnter.send_keys(Keys.ENTER)
        time.sleep(3)
        org15=driver.find_element_by_name('lens_FC_SNS_EMPTEL_CCODE') #Cari ID untuk kod phone
        val15 = org15.get_attribute("data-select-id")
        if employer_phone_code == '673-BR':
            cariID15='#select-options-'+val15+' > li:nth-child(2) > span'
        elif employer_phone_code == '60-MY':
            cariID15='#select-options-'+val15+' > li:nth-child(3) > span'
        elif employer_phone_code == '65-SG':
            cariID15='#select-options-'+val15+' > li:nth-child(4) > span'
        elif employer_phone_code == '81-JP':
            cariID15='#select-options-'+val15+' > li:nth-child(5) > span'
        driver.find_element_by_css_selector('#EMPT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div.input-container.row.country-code__wrapper > div.input-field.col-xs-12.col-md-6.country-code__container > div > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl15 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID15)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl15.click()
        driver.find_element_by_css_selector('#lens_FN_SNS_EMPTEL').send_keys(employer_phone_number)
        driver.find_element_by_css_selector('#lens_FN_SNS_EMPTEL_EXT').send_keys(ext_number)
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        print("employement details selesai")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#lens_FY_SNS_GROSS_MTH_SALARY')))
        driver.find_element_by_css_selector('#lens_FY_SNS_GROSS_MTH_SALARY').click()
        driver.find_element_by_css_selector('#lens_FY_SNS_GROSS_MTH_SALARY').send_keys(gross_salary)
        driver.find_element_by_css_selector('#lens_FY_SNS_NET_MTH_SALARY').click()
        driver.find_element_by_css_selector('#lens_FY_SNS_NET_MTH_SALARY').send_keys(net_salary)
        driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input').click()
        driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input').send_keys(day_receive_salary)
        click=driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input')
        click.send_keys(Keys.ENTER)
        if is_other_income=='YES':
            org16=driver.find_element_by_name('lens_FC_SNS_OTH_INCOME_SRC') #Cari ID untuk OTHER INCOME SOURCE
            val16 = org16.get_attribute("data-select-id")
            print(val16)
            source_other_income='INSURANCE'
            if source_other_income == 'INSURANCE':
                cariID16='#select-options-'+val16+' > li:nth-child(2) > span'
            elif source_other_income == 'DIRECT SELLING':
                cariID16='#select-options-'+val16+' > li:nth-child(3) > span'
            elif source_other_income == 'BUSINESS':
                cariID16='#select-options-'+val16+' > li:nth-child(4) > span'
            elif source_other_income == 'OTHER':
                cariID16='#select-options-'+val16+' > li:nth-child(5) > span'
            print(cariID16)
            driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div:nth-child(1) > div > input').click()
            #time.sleep(3)
            wait = WebDriverWait(driver, 10)
            cl16 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID16)))
            #driver.find_element_by_css_selector(cariID1).click()
            cl16.click()
            if source_other_income == 'OTHER':
                #source_other_income__other='eat'
                driver.find_element_by_css_selector('#lens_FC_SNS_OTH_INCOME_SRC_DESC').send_keys(source_other_income__other)
            driver.find_element_by_css_selector('#lens_FY_SNS_OTHER_INCOME').click()
            driver.find_element_by_css_selector('#lens_FY_SNS_OTHER_INCOME').send_keys(other_income_amount)
        if existing_loans_non_bank=='YES':
            driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(18) > div > div > div > div:nth-child(1) > label').click()
        elif existing_loans_non_bank=='NO':
            driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(18) > div > div > div > div:nth-child(2) > label').click()
        if existing_loans_non_bank=='YES':
            #lens_FY_SNS_REPAY_AMT_NB
            driver.find_element_by_css_selector('#lens_FY_SNS_REPAY_AMT_NB').click()
            driver.find_element_by_css_selector('#lens_FY_SNS_REPAY_AMT_NB').send_keys(monthly_repayment)
            #lens_FC_SNS_REPAY_SOURCE_NB
            driver.find_element_by_css_selector('#lens_FC_SNS_REPAY_SOURCE_NB').click()
            driver.find_element_by_css_selector('#lens_FC_SNS_REPAY_SOURCE_NB').send_keys(repayment_source)
        org17=driver.find_element_by_name('lens_FC_SNS_JOINT_INCOME') #Cari ID untuk OTHER INCOME SOURCE
        val17 = org17.get_attribute("data-select-id")
        if isWithJointApplicant == 'YES':
            cariID17='#select-options-'+val17+' > li:nth-child(2) > span'
        elif isWithJointApplicant == 'NO':
            cariID17='#select-options-'+val17+' > li:nth-child(3) > span'
        driver.find_element_by_css_selector('#INCE_CMMT-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(20) > div > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl17 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID17)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl17.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        print("financial details selesai")
        brand = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#row_1 > div:nth-child(1) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        brand.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys('AMD')
        brandEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        brandEnter.send_keys(Keys.ENTER)
        wait = WebDriverWait(driver, 10)
        category = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#row_1 > div:nth-child(2) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        category.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys('COMPUTER & LAPTOP')
        categoryEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        categoryEnter.send_keys(Keys.ENTER)
        
        wait = WebDriverWait(driver, 10)
        category = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#row_1 > div:nth-child(3) > span > span.selection > span')))
        #driver.find_element_by_css_selector(cariID1).click()
        category.click()
        #driver.find_element_by_css_selector('#RSDL_ADDS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > span > span.selection > span').click()
        driver.find_element_by_css_selector('body > span > span > span.select2-search.select2-search--dropdown').click()
        driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys('COMPUTER PARTS ANY MODEL')
        categoryEnter=driver.find_element_by_xpath('/html/body/span/span/span[1]/input')
        categoryEnter.send_keys(Keys.ENTER)
        driver.find_element_by_css_selector('#lens_apm_prodrec_price_1').click()
        driver.find_element_by_css_selector('#lens_apm_prodrec_price_1').send_keys(product_price)
        org18=driver.find_element_by_name('lens_FC_SNS_OF_ZERO_FIN') #Cari ID untuk OTHER INCOME SOURCE
        val18 = org18.get_attribute("data-select-id")
        cariID18='#select-options-'+val18+' > li:nth-child(2) > span'
        driver.find_element_by_css_selector('#FNNG_DTLS_OF-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div.input-field.col-xs-12.col-md-6.section-group-newapp_nsLOAN_AEON_FNNG_DTLS_OF__1 > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        cl18 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cariID18)))
        #driver.find_element_by_css_selector(cariID1).click()
        cl18.click()
        driver.find_element_by_css_selector('#lens_FY_SNS_OF_DOWN_PAY').click()
        driver.find_element_by_css_selector('#lens_FY_SNS_OF_DOWN_PAY').send_keys(down_payment) 
        driver.find_element_by_css_selector('#lens_FN_SNS_OF_INT_RATE').send_keys(product_interest_rate)
        '''
        if product_price == 2999 or product_price < 2999:
            driver.find_element_by_css_selector('#lens_FN_SNS_OF_INT_RATE').send_keys('1.25')
            print("Interest")
            print("1")
        elif product_price == 3000 or product_price<9999 or product_price==9999:
            driver.find_element_by_css_selector('#lens_FN_SNS_OF_INT_RATE').send_keys('1.10')
            print("Interest")
            print("2")
        elif product_price > 9999:
            driver.find_element_by_css_selector('#lens_FN_SNS_OF_INT_RATE').send_keys('0.850')
            print("Interest")
            print("3")
          
        if promotionVoucherAmount:
            driver.find_element_by_css_selector('#lens_FY_SNS_OF_PROMO_VO').click()
            driver.find_element_by_css_selector('#lens_FY_SNS_OF_PROMO_VO').send_keys(promotionVoucherAmount)
        else:
            driver.find_element_by_css_selector('#lens_FY_SNS_OF_PROMO_VO').click()
            driver.find_element_by_css_selector('#lens_FY_SNS_OF_PROMO_VO').send_keys(0)
        '''
        time.sleep(8)
        driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/input').click()
        time.sleep(5)
        driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/input').click()
        te_pilih=driver.find_element_by_css_selector('#FNNG_DTLS_OF-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div.input-container.row.section-group-newapp_nsLOAN_AEON_FNNG_DTLS_OF__1.before-line-begin.to-the-left > div > div > input')
        if tenure ==6:
            print(driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[2]/span').text)
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[2]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[2]/span')))
            click.click()
        elif tenure ==12:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[3]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[3]/span')))
            click.click()
        elif tenure ==18:
            #time.sleep(2)
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[4]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[4]/span')))
            click.click()
        elif tenure ==24:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[5]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[5]/span')))
            click.click()
        elif tenure ==30:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[6]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[6]/span')))
            click.click()
        elif tenure ==36:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[7]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[7]/span')))
            click.click()
        elif tenure ==42:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[8]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[8]/span')))
            click.click()
        elif tenure ==48:
            #driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[9]/span').click()
            wait = WebDriverWait(driver, 50)
            click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[5]/div/div[2]/div/form/div[6]/div/div/ul/li[9]/span')))
            click.click()
        if promotion_code:
            driver.find_element_by_css_selector('#lens_FC_SNS_AFMF_PROM_CD').send_keys(promotion_code)
        name_of_field_initialPayment=driver.find_element_by_name('lens_FC_SNS_OF_INIT_PAY') #Cari ID untuk Initial payment
        id_of_field_initialPayment = name_of_field_initialPayment.get_attribute("data-select-id")
        if initial_payment == 'YES':
            select_initialPayment='#select-options-'+id_of_field_initialPayment+' > li:nth-child(2) > span'
        elif initial_payment == 'NO':
            select_initialPayment='#select-options-'+id_of_field_initialPayment+' > li:nth-child(3) > span'
        driver.find_element_by_css_selector('#FNNG_DTLS_OF-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(22) > div.input-field.col-xs-12.col-md-6.section-group-newapp_nsLOAN_AEON_FNNG_DTLS_OF__1 > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        input_initialPayment = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_initialPayment)))
        #driver.find_element_by_css_selector(cariID1).click()
        input_initialPayment.click()
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        wait = WebDriverWait(driver, 10)
        print("product details selesai")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(13) > div > div > div > div:nth-child(1) > label')))
        if mailing_address =='RESIDENTIAL HOUSE':
            driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(13) > div > div > div > div:nth-child(1) > label').click()
        elif mailing_address =='OFFICE':
            driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(13) > div > div > div > div:nth-child(2) > label').click()
        name_of_paymentDetails=driver.find_element_by_name('lens_FC_SNS_PROVIDE_FIN') #Cari ID untuk payment details
        id_of_paymentDetails = name_of_paymentDetails.get_attribute("data-select-id")
        if payment_details == 'YES':
            select_paymentDetails='#select-options-'+id_of_paymentDetails+' > li:nth-child(2) > span'
        elif payment_details == 'NO':
            select_paymentDetails='#select-options-'+id_of_paymentDetails+' > li:nth-child(3) > span'
        driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(14) > div > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        input_paymentDetails = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_paymentDetails)))
        #driver.find_element_by_css_selector(cariID1).click()
        input_paymentDetails.click()
        time.sleep(8)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input')))
        name_of_paymentMethod=driver.find_element_by_name('lens_FC_SNS_MTH_PAY') #Cari ID untuk payment method
        id_of_paymentMethod = name_of_paymentMethod.get_attribute("data-select-id")
        if payment_method == 'AUTODEBIT':
            select_paymentMethod='#select-options-'+id_of_paymentMethod+' > li:nth-child(2) > span'
        elif payment_method == 'POSTDATED CHEQUE':
            select_paymentMethod='#select-options-'+id_of_paymentMethod+' > li:nth-child(3) > span'
        wait = WebDriverWait(driver, 10)
        press = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input')))
        press.click()
        #driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(15) > div > div > input').click()
        #time.sleep(3)
        wait = WebDriverWait(driver, 10)
        input_paymentMethod = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_paymentMethod)))
        #driver.find_element_by_css_selector(cariID1).click()
        input_paymentMethod.click()
        if is_salary_account =='YES':
            driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div > div > div > div:nth-child(1) > label').click()
        elif is_salary_account =='NO':
            driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(16) > div > div > div > div:nth-child(2) > label').click()
        time.sleep(6)
        name_of_bank=driver.find_element_by_name('lens_FC_SNS_BANK') #Cari ID untuk BANK
        id_of_bank = name_of_bank.get_attribute("data-select-id")
        if bank =='ALLIANCE BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(2) > span'
        elif bank =='AMBANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(3) > span'
        elif bank =='BANK SIMPANAN NASIONAL':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(4) > span'
        elif bank =='CIMB BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(5) > span'
        elif bank =='MAY BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(6) > span'
        elif bank =='MUAMALAT BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(7) > span'
        elif bank =='PUBLIC BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(8) > span'
        elif bank =='RHB BANK':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(9) > span'
        elif bank =='STANDARD CHARTERED':
            select_bank='#select-options-'+id_of_bank+' > li:nth-child(10) > span'
        print(select_bank)
        driver.find_element_by_css_selector('#PYMT_DTLS-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(17) > div > div > input').click()
        wait = WebDriverWait(driver, 50)
        input_bank = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, select_bank)))
        #driver.find_element_by_css_selector(cariID1).click()
        input_bank.click()
        driver.find_element_by_css_selector('#lens_FC_SNS_ACC_NO').send_keys(account_number)
        driver.find_element_by_css_selector('#lens_FC_SNS_ACC_HOLD_NAME').send_keys(account_holder_name)
        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
        #wait = WebDriverWait(driver, 10)
        #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#DCMT_SBMN-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(10) > div > div.module-checklistlist > div:nth-child(1) > div')))
        #upload_ic_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#DCMT_SBMN-A-newapp_ns > div.hpanel.hred.animated-panel.fadeInUp.applet > div > form > div:nth-child(10) > div > div.module-checklistlist > div:nth-child(1) > div')))
        #upload_ic_button.click()
        time.sleep(5)
        #/html/body/input[1]
        #body > input:nth-child(33)
        print("payment details selesai")
        x = datetime.datetime.now()
        nama_directory=applicant_name+'_'+x.strftime("%d-%B-%Y-%I:%M:%S")
        os.mkdir(nama_directory)
        path_nric_prod="//gambar//"+nama_directory+"//"+nric_document.filename
        path_income_prod="//gambar//"+nama_directory+"//"+income_document.filename
        
        #path_income_dev="D:\AEONRACUNTECH\\gambar\\" +nama_directory+r"\\"+income_document.filename
        #path_nric_prod="/"+ nama_directory+"//" +isi.filename 
        shutil.copytree( nama_directory,'gambar/'+ nama_directory)
        with open(path_nric_prod,'wb+') as f:
            f.write(nric_document.file.read())
            f.close()
        print(path_nric_prod)
        time.sleep(5)
        driver.find_element_by_xpath('/html/body/input[3]').send_keys(path_nric_prod)
        with open(path_income_prod,'wb+') as f:
            f.write(income_document.file.read())
            f.close()
        print(path_income_prod)
        time.sleep(5)
        driver.find_element_by_xpath('/html/body/input[1]').send_keys(path_income_prod)
        if other_document:
            path_doc_prod="//gambar//"+nama_directory+"//"+other_document.filename
            with open(path_doc_prod,'wb+') as f:
                f.write(other_document.file.read())
                f.close()
            print(path_doc_prod)
            time.sleep(5)
            driver.find_element_by_xpath('/html/body/input[1]').send_keys(path_doc_prod)
        #/html/body/input[2]

        #driver.find_element_by_xpath('/html/body/input[1]').send_keys('D:\EvT0XT-VgAIwDey.jfif')
        
        driver.find_element_by_css_selector('#newapp_nsLOAN_AEON_DCMT_SBMNlens_FX_SNS_DOC_REMARKS').send_keys(application_remarks)

        driver.find_element_by_css_selector('#view > div > div.col-main.col-sm-12 > div.advent-buttons > div.button-groups > a.button.button--primary.button--next').click()
    except Exception as e:
        driver.quit()
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(traceback.format_exc()))

    driver.quit()
    return {"applicantTitle":applicant_title,"applicantName":applicant_name,"applicantEmail":applicant_email,"applicantPhoneNumber":applicant_phone_number,"isMembership":is_aeon_membership,"isAEONCardHolder":is_aeon_card_holder}
    

@app.post("/unggah")
async def test(isi:UploadFile= File(...),nama:str=Form(...),username: str = Depends(get_current_username)):
    x = datetime.datetime.now()
    nama_directory=nama+'_'+x.strftime("%d-%B-%Y-%I:%M:%S")
    os.mkdir(nama_directory)
    path_nric="/"+ nama_directory+"//" +isi.filename 
    print('gambar/'+ nama_directory)
    shutil.copytree( nama_directory,'gambar/'+ nama_directory) 
    with open("gambar/"+path_nric,'wb+') as f:
        f.write(isi.file.read())
        f.close()
    os.rmdir("/"+nama_directory)
    return {"namaFail":path_nric}

@app.get("/test")
async def tests(username: str = Depends(get_current_username)):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://www.google.com/')
    result=driver.title
    driver.quit()
    return {"result":result,"dir":os.listdir(),"dalam_gambar":os.listdir("/gambar"),"dalam_gambar1":os.listdir("/gambar1")}

@app.get("/itemlines/{item}")
async def itemline(item,username: str = Depends(get_current_username)):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('')
    driver.get_screenshot_as_file("/app/screenshot.png")
    driver.find_element(By.XPATH,'/html/body/div[1]/form/p[1]/input').send_keys('system')
    driver.find_element(By.XPATH,'//*[@id="user_pass"]').send_keys('9Ty!BtegvLL7pJ^!NkBQZPzd')
    driver.find_element(By.XPATH,'/html/body/div[1]/form/p[3]/input[1]').click()
    driver.find_element_by_xpath('/html/body/div[1]/form/p[3]/input[1]').click()
    link='?post={}&action=edit'.format(item)
    driver.get(link)
    table_item=driver.find_element_by_class_name("woocommerce_order_items")
    dataframe1=pd.read_html(table_item.get_attribute('outerHTML'))[0]
    #dataframe1[dataframe1['Qty'].notnull()]
    dataframe2=dataframe1[(dataframe1['Qty'].notnull())&(dataframe1['Qty'].str.contains('Location') == False)]
    #dataframe2['Item.1'][0]
    dataframe2=dataframe2.reset_index(drop=True)
    dataframe3=dataframe2
    dataframe3=dataframe3.assign(SKU='')
    #dataframe3
    z=0
    while z<dataframe2.shape[0]:
        #print(dataframe2['Item.1'][z].split('SKU:')[0])
        dataframe3.at[z,'Item.1']=dataframe2['Item.1'][z].split('SKU:')[0]
        dataframe3.at[z,'SKU']=dataframe2['Item.1'][z].split('SKU:')[1]
        z+=1
    k=driver.find_elements(By.XPATH,"//*[@id=\"order_shipping_line_items\"]")
    list_shipping=[]
    i=0
    while i < len(k[0].find_elements(By.TAG_NAME, "tr.shipping")):
        text=k[0].find_elements(By.TAG_NAME, "tr.shipping")[i].find_element(By.TAG_NAME, "div.view").text
        charge=k[0].find_elements(By.TAG_NAME, "tr.shipping")[i].find_element(By.TAG_NAME, "span.woocommerce-Price-amount.amount").text
        storComma=[]
        s=k[0].find_elements(By.TAG_NAME, "tr.shipping")[i].find_element(By.TAG_NAME, "p").text
        for match in finditer(r"\d, ", s):
            index=match.start()
            value=match.group()
            print(index, value)
            storComma.append(index)
        ss=list(s)
        for x in storComma:
             ss[x+1]="ß"
        print(''.join(ss))
        cv=''.join(ss)
        n=cv.split("ß ")
        len_item=n       
        j=0
        list_item=[]
        if len(len_item)>1:
            while j<len(len_item):
                lim=len_item[j].index(' ×')
                bil=len_item[j][lim+1:len(len_item[j])]
                len_item[j]=len_item[j][0:lim]
                len_item[j]=len_item[j].strip()
                sku=dataframe3['SKU'][dataframe3[(dataframe3['Item.1']==len_item[j])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
                cost=dataframe3['Total'][dataframe3[(dataframe3['Item.1']==len_item[j])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
                qty=dataframe3['Qty'][dataframe3[(dataframe3['Item.1']==len_item[j])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
                list_item.append({'item_name':len_item[j],'cost':'RM'+str(float(cost.split("RM")[1].replace(',',''))/int(qty.replace('×', ''))),'qty':qty.replace('×', ''),'sku':sku[1:len(sku)]})
                j+=1
        else:
            lim=len_item[0].index(' ×')
            bil=len_item[0][lim+1:len(len_item[0])]
            len_item[0]=len_item[0][0:lim]
            len_item[0]=len_item[0].strip()
            sku=dataframe3['SKU'][dataframe3[(dataframe3['Item.1']==len_item[0])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
            cost=dataframe3['Total'][dataframe3[(dataframe3['Item.1']==len_item[0])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
            qty=dataframe3['Qty'][dataframe3[(dataframe3['Item.1']==len_item[0])&(dataframe3['Qty']==bil)].index.values.tolist()[0]]
            list_item.append({'item_name':len_item[0],'cost':'RM'+str(float(cost.split("RM")[1].replace(',',''))/int(qty.replace('×', ''))),'qty':qty.replace('×', ''),'sku':sku[1:len(sku)]})
        list_shipping.append({"shippingMethod":text,"shippingCharge":charge,"items":list_item})
        i+=1
    driver.quit()
    return list_shipping

@app.post("/getsalesorder/")
async def getsalesorder(custid: str = Form(...),date: str = Form(...),username: str = Depends(get_current_username)):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=options)
    x = datetime.datetime.now()
    print(x.strftime("%d-%B-%Y %I:%M %p"))
    print(custid)
    driver.get('')
    username = driver.find_element_by_id("username")
    username.send_keys('')
    password = driver.find_element_by_name("password")
    password.send_keys('')
    password.send_keys(Keys.ENTER)
    driver.get('')
    driver.find_elements_by_xpath('//*[@id="branchselectAllBranches"]')[0].click()
    driver.find_elements_by_xpath('//*[@id="accPkid"]')[0].send_keys(custid)
    driver.find_elements_by_xpath('//*[@id="showCustomerName_accPkid"]')[0].click()
    to=driver.find_element_by_id("dateTo")
    to.clear()
    to.send_keys(date)#date
    done=driver.find_element_by_class_name('ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all')    
    done.click()
    fromm=driver.find_element_by_id("dateFrom")
    fromm.clear()
    fromm.send_keys(date)#date
    done2=driver.find_element_by_class_name('ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all')    
    done2.click()
    driver.find_elements_by_xpath('//*[@id="tt"]/div[2]/div/div/form/table/tbody/tr[13]/td[2]/input')[0].click()
    table=driver.find_elements_by_id("dataTable")
    print(table)
    preprocessdf=pd.read_html(table[0].get_attribute('outerHTML'))
    dfs=preprocessdf[0]
    print(dfs)
    print("Sales Order")
    print(dfs["Order #"][len(dfs)-2])
    driver.quit()
    return {"salesOrder": dfs["Order #"][len(dfs)-2],"branch":dfs["Branch"][len(dfs)-2]}

@app.get("/merge/{number}")
async def merge_number(number,username: str = Depends(get_current_username)):
    url = ""
    payload = {
    "search":"",
   "filter":{
      "$and":[
         {
            "category":"contactField",
            "field":"phone",
            "operator":"isEqualTo",
            "value":"{}".format(number)
         }
      ]
   },
   "timezone":"Asia/Kuala_Lumpur"
}
    headers = {
    "Content-Type": "application/json",
    "Authorization": ""
}
    response = requests.request("POST", url, json=payload, headers=headers)
    c=response.json()['items']
    print(pd.DataFrame(c))
    raw_data=pd.DataFrame(c)
    if raw_data.shape[0]>1:
        print(raw_data['custom_fields'])
        arrayofvariables=[]
        for r in raw_data['custom_fields']:
            if r[7]['value']==None:
                vals=str(0)
                numbs=str(0)
            else:
                vals=r[8]['value']
                numbs=r[7]['value']   
            arrayofvariables.append({'number':numbs,'value':vals})
        print(arrayofvariables)
        if arrayofvariables[1]['number']!="0":
            bil=int(max(arrayofvariables,key=lambda x:x['number'])['number'])
            bay=int(float(max(arrayofvariables,key=lambda x:x['number'])['value']))
        else:
            bil=None
            bay=None   
        ids=raw_data['id'].tolist()
        print(ids)
        print('ada berapa:' +str(raw_data.shape[0]))
        i=0
        while i<raw_data.shape[0]-1:
            url = ""
            payload = {
            "contactIds": [ids.pop(0),ids.pop(-1)],
                "firstName":raw_data['firstName'][1],
                "custom_fields": [
            {
            "name": "invoice_list",
            "value": bil
            },
                    {
            "name": "purchase_value",
            "value": bay
            },
                    {
            "name": "customer_source",
            "value": "ERPNextSalesOrder"
            }
            ]
            }
            print(str(payload))
            headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": ""
            }
            #response = requests.request("POST", url, json=payload, headers=headers)
            response = requests.post(url, json=payload, headers=headers)
            print(response.json())
            #print(response.json()['contactId'])
            ids.append(response.json()['contactId'])
            time.sleep(5)
            i+=1
    return {"number":number}