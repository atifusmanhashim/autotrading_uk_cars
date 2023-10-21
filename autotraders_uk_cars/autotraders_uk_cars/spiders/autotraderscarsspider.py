import re
import csv
import scrapy
import base64
import logging
import requests
import json
import time
import math
import xml
import os
import traceback
import random
import autotraders_uk_cars.constants as constants

from six import iteritems

from autotraders_uk_cars.items import AutotradersUkCarsItem
from autotraders_uk_cars.functions import (current_date_time, 
                                        current_date,
                                        write_log_file, 
                                        find_str,
                                        write_log_file)

#Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from webdriver_manager.chrome import ChromeDriverManager

#For Getting Path of chromedriver
from pathlib import Path
from bs4 import BeautifulSoup

from urllib.parse import urlparse,urlsplit,urljoin,urlencode, parse_qs

class AutotraderscarsspiderSpider(scrapy.Spider):
    name = "autotraderscarsspider"
    # allowed_domains = ["www.autotrader.co.uk"]
    start_urls = ["https://www.google.com/"]

    page_incr=1

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    BASE_DIR=BASE_DIR = Path(__file__).resolve().parent.parent
    chrome_driver_path=os.path.join(BASE_DIR, 'chromedriver')

    def __init__(self, name=None, **kwargs):
        super(AutotraderscarsspiderSpider, self).__init__(name, **kwargs)
        

        # Chrome Browser Options
        options = Options()
        
        # options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument("--start-maximized")
        # options.add_argument('user-agent={agent}'.format(agent=self.user_agent))
        options.add_argument("--disable-extensions")
        
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        options.add_argument("disable-infobars")
        
        #provide location where chrome stores profiles
        # options.add_argument(r"--user-data-dir=/home/atifusman/.config/google-chrome")

        # #provide the profile name with which we want to open browser
        # options.add_argument(r'--profile-directory=Profile 5')
        options.add_argument('--remote-debugging-port=9222')
        
        #Initialize Driver
        # self.driver=webdriver.Chrome(options=options)
        self.driver = webdriver.Chrome(self.chrome_driver_path,options=options)

    # Start of Scraping
    def start_requests(self):
        for url in self.start_urls: 
            yield scrapy.Request(url=url, callback=self.car_search_parse,headers=self.HEADERS)


    def resolve_verification_challenge(self):
        result=True
        # Resolving Verification Challenge of Cloudfare
        try:
            # Verification iframe
            verification_challenges=self.driver.find_elements(By.ID,'challenge-stage')
            if len(verification_challenges)>=1:
                verification_challenge=verification_challenges[0]
                verification_challenge_iframes=verification_challenge.find_elements(By.TAG_NAME,"iframe")
                if len(verification_challenge_iframes)>=1:
                    verification_challenge_iframe=verification_challenge_iframes[0]
                    self.driver.switch_to.frame(verification_challenge_iframe)
                    iframe_chkboxes=self.driver.find_elements(By.CSS_SELECTOR,"#challenge-stage > div > label > input[type=checkbox]")
                    if len(iframe_chkboxes)>=1:
                        iframe_chkbox=iframe_chkboxes[0]
                        iframe_chkbox.click()
                        time.sleep(40)
            return True

        except:
            time.sleep(20)
            return False

    def car_search_parse(self, response):
        try:

            total_cars_search_count=0
            total_pages=0

            car_collections=[]
            car_scraped_list=[]

            sel_url="https://www.autotrader.co.uk/car-search?advertising-location=at_cars&include-delivery-option=on&make=Volkswagen&model=Caddy%20Maxi%20Life&page=1&postcode=SW1W%200NY&refresh=true"

            self.driver.get(sel_url)

            time.sleep(20)

            self.resolve_verification_challenge()


            # wait = WebDriverWait(self.driver, 10)
            # wait.until(visibility_of_element_located((By.CSS_SELECTOR,'p[data-testid="pagination-show"]')))


            # Current URL
            current_url=self.driver.current_url

            print("Current Car Search URL: "+current_url)
            
            parse_result = urlparse(current_url)

            # Current URL Query Parameters
            current_query_params = parse_qs(parse_result.query)

            # Printing Query Parameters
            print(current_query_params)

            current_page_cnt=current_query_params['page'][0]

            print("Current Page: "+str(current_page_cnt))

            
            # Total Cars Search Count
            total_cars_search_count_elements=self.driver.find_elements(By.CSS_SELECTOR,'h1[data-testid="search-desktop-result-count"]')
            if len(total_cars_search_count_elements)>=1:
                total_cars_search_count_element=total_cars_search_count_elements[0]
                total_cars_search_count=total_cars_search_count_element.text.removesuffix("cars found").strip()

                if str(total_cars_search_count).isnumeric():
                    total_cars_search_count=int(total_cars_search_count)
                
                else:
                    total_cars_search_count=0

                print("Total Cars Found: "+str(total_cars_search_count))

            else:
                total_cars_search_count=0
                print('Nil')

           

            # Total Pages
            total_pages_elements=self.driver.find_elements(By.CSS_SELECTOR,'p[data-testid="pagination-show"]')
            if len(total_pages_elements)>=1:
                total_pages_element=total_pages_elements[0]
                total_pages_element=total_pages_element.text
                req_pattern=r'\d+'
                page_numbers=re.findall(req_pattern, total_pages_element)
                if len(page_numbers) >= 2:
                    total_pages = int(page_numbers[1])
                    print(f"Total pages: {total_pages}")
            else:
                total_pages=0


            
            if total_pages>=1 and total_cars_search_count>=1:
                print("Found")
                while self.page_incr<=total_pages:
                    
                    # Getting Current Page
                    current_page=int(parse_qs(urlparse(self.driver.current_url).query)['page'][0])
                    print("Current Page: "+str(current_page))

                    # Gettings Car Details Links
                    cars_list_ul_chk=self.driver.find_elements(By.CSS_SELECTOR,'ul[data-testid="desktop-search"]')
                    if len(cars_list_ul_chk)==1:
                        cars_list_ul=cars_list_ul_chk[0]
                        cars_list_li_chk=cars_list_ul.find_elements(By.CSS_SELECTOR,"li.sc-fbKhjd.jxKUBR > section[data-testid='trader-seller-listing']")
                        if len(cars_list_li_chk)>=1:
                            i=0
                            for sel_car_div in cars_list_li_chk:
                                try:
                                    print(i)
                                    car_details_link=sel_car_div.find_element(By.CSS_SELECTOR,'a[data-testid="search-listing-title"]').get_attribute('href')
                                    print(car_details_link)
                                    car_name=sel_car_div.find_element(By.CSS_SELECTOR,'a[data-testid="search-listing-title"] > h3').text
                                    print(car_name)
                                    car_data={
                                            'car_name':car_name,
                                            'car_link':car_details_link
                                        }
                                    car_collections.append(car_data)
                                    i+=1
                                except:
                                    print('Break at '+str(i))
                                    break


                    
                    if self.page_incr<total_pages:
                        next_page_result=self.driver.find_elements(By.CSS_SELECTOR,"a[data-testid='pagination-next']")
                        if len(next_page_result)>=1:
                            next_page_element=next_page_result[0]
                            next_page_element.click()
                            time.sleep(10)
                            self.page_incr+=1
                            print(self.page_incr)
                        else:
                            break
                    else:
                        break


                        
            # Navigating to each Car Details Page for getting Car Details and saving into List
            if len(car_collections)>=1:
                for sel_car_data in car_collections:
                    car_link=sel_car_data['car_link']
                    car_details_data=self.get_car_details(car_link)
                    if car_details_data is not None:
                        if len(car_details_data)>=1:
                            car_data=car_details_data
                            car_scraped_list.append(car_data)

            
            # Getting all Car Details in one Go
            if len(car_scraped_list)>=1:
                for car in car_scraped_list:
                    yield car


            
        # Exception   
        except Exception as e:
            message=("Error Date/Time:{current_time}\nError:{current_error}\n\{tb}".format(
                    current_time=current_date_time(),
                    current_error=repr(e),
                    tb=traceback.format_exc()
            ))

            print(message)
            error_data={
                'error_message':message
            }
            yield error_data



    # Getting Car Details using URL
    def get_car_details(self,sel_car_detail_url):
        car_details={}
        try:
            car_details={}

            car_images_lst={}

            self.driver.get(sel_car_detail_url)

            time.sleep(20)

            if sel_car_detail_url==self.driver.current_url:
                car_layout_div_chk=self.driver.find_elements(By.ID,"layout-desktop")
                if len(car_layout_div_chk)>=1:
                    car_layout_div=car_layout_div_chk[0]
                    car_price=car_layout_div.find_element(By.CSS_SELECTOR,"h2[data-testid='advert-price']").text
                    print(car_price)
                    car_name=car_layout_div.find_element(By.CSS_SELECTOR,"p[data-testid='advert-title']").text
                    
                    car_images_chk=car_layout_div.find_elements(By.CSS_SELECTOR,".sc-bXCLTC.jlnCeq.atds-image")
                    if len(car_images_chk)>=1:
                        img_i=0
                        for img in car_images_chk:
                            img_i+=1
                            if img_i not in car_images_lst:
                                car_images_lst.update({"image"+str(img_i):img.get_attribute('src')})

                        if len(car_images_lst)>=1:
                            car_images_list=list(car_images_lst.values())
                            car_images=", ".join(car_images_list)
                        else:
                            car_images=""
                    else:
                        car_images=""

                    section_features_elements=self.driver.find_elements(By.CSS_SELECTOR,"#layout-desktop > article > section.sc-crvIOg.iTqnRU")
                    if len(section_features_elements)>=1:
                        section_features_element=section_features_elements[0]
                        car_mileage=section_features_element.find_element(By.CSS_SELECTOR,'ul > li:nth-child(1) > span > p').text
                        car_mileage_above_average=section_features_element.find_element(By.CSS_SELECTOR,"ul > li:nth-child(1) > span > div.sc-fYXIxC.iLQRZa > p > span > span:nth-child(1)").text
                        car_registration_model=section_features_element.find_element(By.CSS_SELECTOR,"ul > li:nth-child(2) > span > p").text
                        car_fuel_type=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(1) > div:nth-child(1) > dd").text
                        car_body_type=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(1) > div:nth-child(2) > dd").text
                        car_engine=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(1) > div:nth-child(3) > dd").text
                        car_seat_capacity=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(2) > div:nth-child(2) > dd").text

                        try:
                            car_emission_class=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(2) > div:nth-child(3) > dd > span > span").text
                        except:
                            car_emission_class=section_features_element.find_element(By.CSS_SELECTOR,"section > dl:nth-child(2) > div:nth-child(4) > dd > span > span").text
                        
                        car_details={
                            'car_name':car_name,
                            'car_details_url':sel_car_detail_url,
                            'car_price':car_price,
                            'car_mileage':car_mileage + " (Above Average: "+car_mileage_above_average+")",
                            'car_registration_model':car_registration_model,
                            'car_emission_class':car_emission_class,
                            'car_body_type':car_body_type,
                            'car_seating_capacity':car_seat_capacity,
                            'car_engine_type':car_engine,
                            'car_fuel_type':car_fuel_type,
                            'car_images':car_images
                        }
                        print(car_details)

                        return car_details
                else:
                    car_details={}
                    return car_details

            else:
                car_details={}
                return car_details
        except Exception as e:
            message=("Error Date/Time:{current_time}\nError:{current_error}\n\{tb}".format(
                    current_time=current_date_time(),
                    current_error=repr(e),
                    tb=traceback.format_exc()
            ))

            print(message)
            error_data={
                'error_message':message
            }
        return car_details
