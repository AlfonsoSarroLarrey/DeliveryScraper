import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from bs4 import BeautifulSoup

JUST_EAT_BASE_URL = 'http://www.just-eat.co.uk/'
JUST_EAT_URL_PART1 = '/area/'
JUST_EAT_URL_PART2 = '?filter=new'


#Close not currently accepting orders ccl-364e2ed6a76f91e9

####################### JUST EAT ####################################


MORE_INFO_ARIA_LABEL = 'More information'
CLOSE_INFO_DATA_QA = 'restaurant-info-modal-header-action-close'
PHONE_INFO_ARIA_LABEL = 'More product information'

RESTAURANT_NAME_CLASS = '_50YZr _11kfx'
RESTAURANT_TELEPHONE_CLASS = '_3VpRA _1oYzK undefined _1zoHE'
RESTAURANT_HYGIENE_CLASS = '_1xp4W'
RESTAURANT_ADDRESS_CLASS = '_2GljJ'


def enterRestaurantPage(url, initialReconnectTime):
    restaurantInfo = {
        "name": 'None',
        "telephone": 'None',
        "hygiene": 'None',
        "address": 'None',
        "source": 'JustEat'
    }

    driver = Driver(uc=True, headless=False)
   
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(url, reconnect_time=initialReconnectTime)
    #Click more info button
    moreInfoButton = driver.find_element(by=By.XPATH, value="//span[contains(@aria-label, '" + MORE_INFO_ARIA_LABEL + "')]")
    try:
        moreInfoButton.click()
    except:
        driver.quit()
        return
    


    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Refresh and click product more info button (to get phone number)
    driver.uc_open_with_reconnect(url, reconnect_time=initialReconnectTime - 2)
    moreInfoPhoneButton = driver.find_element(by=By.XPATH, value="//span[contains(@aria-label, '" + PHONE_INFO_ARIA_LABEL + "')]")
    moreInfoPhoneButton.click()

    time.sleep(2)
    
    soupPhone = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    #Find the data we need
    restaurantName = soup.find('h1', class_= RESTAURANT_NAME_CLASS)
    restaurantTel = soupPhone.find_all('a', class_ = RESTAURANT_TELEPHONE_CLASS)
    restaurantHygieneImg = soup.find_all('img', class_= RESTAURANT_HYGIENE_CLASS)
    restaurantAddress = soup.find_all('div', class_= RESTAURANT_ADDRESS_CLASS)

    #Get only the text and put it into the dictionary for it to be dumped into the JSON
    restaurantInfo['name'] = restaurantName.text
    restaurantInfo['telephone'] = restaurantTel[len(restaurantTel) - 1].text

    hygieneRatingPos = restaurantHygieneImg[len(restaurantHygieneImg) - 1]['src'].find('_')
    restaurantInfo['hygiene'] = restaurantHygieneImg[len(restaurantHygieneImg)- 1]['src'][hygieneRatingPos + 1]

    restaurantInfo['address'] = restaurantAddress[len(restaurantAddress) - 3].text + ', ' + restaurantAddress[len(restaurantAddress) - 2].text

    return restaurantInfo

def scrapeJustEat(driver, postcode, initialReconnectTime, scrollPauseTime):
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(JUST_EAT_BASE_URL + JUST_EAT_URL_PART1 + postcode + JUST_EAT_URL_PART2, reconnect_time=initialReconnectTime)
    
    # Attempt to click the CAPTCHA checkbox if present
    driver.uc_gui_click_captcha()
    
    page = driver.find_element(By.TAG_NAME, 'html')

    #Scroll to the end of the page, this loads all available restaurants
    while True:
        page.send_keys(Keys.PAGE_DOWN)
        time.sleep(scrollPauseTime)
        try:
            driver.find_element(By.TAG_NAME, 'footer')
        except:
            #If no footer found, continue scrolling
            continue
        
        #If footer found, stop scrolling
        break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    data = []
    restaurantList = soup.find_all('a', href=re.compile('restaurants'))
    if len(restaurantList) != 1:
        for restaurant in restaurantList:
            data.append(enterRestaurantPage(JUST_EAT_BASE_URL + restaurant['href'], initialReconnectTime))

    return data