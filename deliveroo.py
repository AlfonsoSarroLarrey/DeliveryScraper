from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from bs4 import BeautifulSoup
import time

DELIVEROO_BASE_URL = 'https://deliveroo.co.uk'
DELIVEROO_MAIN_PAGE_PART1 = '/restaurants/london/westminster?postcode='
DELIVEROO_MAIN_PAGE_PART2 = '&collection=all-restaurants'

DELIVEROO_DENY_COOKIES_BUTTON_ID =  '#onetrust-reject-all-handler'
ACCEPT_COUPON_BUTTON_CLASS = '.ccl-388f3fb1d79d6a36.ccl-6d2d597727bd7bab.ccl-59eced23a4d9e077.ccl-7be8185d0a980278'

RESTAURANT_TAG_CLASS = 'HomeFeedGrid-b0432362335be7af'
RATING_TAG_CLASS = 'css-87fssf'
HREF_TAG_CLASS = 'css-1hms87c'

############ INFO BUTTON ###############
#Classes used in the info button
INFO_BUTTON_TAG_CLASS_1 = "ccl-4704108cacc54616"
INFO_BUTTON_TAG_CLASS_2 = "ccl-4f99b5950ce94015"
INFO_BUTTON_TAG_CLASS_3 = "ccl-724e464f2f033893"

#Position of the info button in the page.
#There are 3 buttons with the same classes, 0 being "back", 1 being "info" and 2 being "deliver"
INFO_BUTTON = 1

RESTAURANT_NAME_TAG_CLASS = 'ccl-cc80f737565f5a11 ccl-de2d30f2fc9eac3e ccl-05906e3f85528c85 ccl-483b12e41c465cc7'
RESTAURANT_TELEPHONE_TAG_CLASS = 'UIContentCard-32d54d142ca96f5c'
RESTAURANT_HYGIENE_TAG_CLASS = 'UIContentCard-85df48fbc5b6a66a'
RESTAURANT_ADDRESS_TAG_CLASS = 'UILines-eb427a2507db75b3'


def getAddressPosition(restaurantInfo):
    for i in range(len(restaurantInfo) - 1, -1, -1):
        if restaurantInfo[i].find('span').find('span').text == "View map":
            i -= 1
            return i
        
    return 0



def enter_restaurant_page(url, initialReconnectTime):
    refresh = True

    restaurantInfo = {
        "name": 'None',
        "telephone": 'None',
        "hygiene": 'None',
        "address": 'None',
        "source": 'Deliveroo'
    }

    driver = Driver(uc=True, headless=False)

    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(url, reconnect_time=initialReconnectTime)

    while refresh:
    # Attempt to click the CAPTCHA checkbox if present
        driver.uc_gui_click_captcha()

        try:
            driver.execute_script('document.querySelector(\"' + DELIVEROO_DENY_COOKIES_BUTTON_ID + '\").click()')
        except:
            print('Cookies did not pop up.')
        buttons = driver.find_elements(by=By.XPATH, value="//button[contains(@class, '" + INFO_BUTTON_TAG_CLASS_1 + "') and contains(@class, '" + INFO_BUTTON_TAG_CLASS_2 + "') and contains(@class, '" + INFO_BUTTON_TAG_CLASS_3 + "')]")
        
        #We click the 2nd button found with these classes, as the 1st button found is the "back" button
        try:
            buttons[INFO_BUTTON].click()
            refresh = False
        except:
            #If we cant click the button, the pop up "Something went wrong" showed up and we need to refresh the page
            driver.refresh()
            
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    #Find the data we need
    restaurantName = soup.find('h1', class_= RESTAURANT_NAME_TAG_CLASS)
    restaurantTel = soup.find('a', class_= RESTAURANT_TELEPHONE_TAG_CLASS)
    restaurantHygieneImg = soup.find('img', class_= RESTAURANT_HYGIENE_TAG_CLASS)
    restaurantAddress = soup.find_all('div', class_= RESTAURANT_ADDRESS_TAG_CLASS)

    #Get only the text and put it into the dictionary for it to be dumped into the JSON
    restaurantInfo['name'] = restaurantName.text
    restaurantInfo['telephone'] = restaurantTel['href']
    if restaurantHygieneImg != None:
        if restaurantHygieneImg['alt'] != '':
            hygieneRatingPos = restaurantHygieneImg['src'].find('@')
            restaurantInfo['hygiene'] = restaurantHygieneImg['src'][hygieneRatingPos - 1]
    restaurantInfo['address'] = restaurantAddress[getAddressPosition(restaurantAddress)].text

    return restaurantInfo


def scrapeDeliveroo(driver, postcode, initialReconnectTime, scrollPauseTime):
    
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(DELIVEROO_BASE_URL + DELIVEROO_MAIN_PAGE_PART1 + postcode + DELIVEROO_MAIN_PAGE_PART2, reconnect_time=initialReconnectTime)
    
    # Attempt to click the CAPTCHA checkbox if present
    driver.uc_gui_click_captcha()


    screen_height = driver.execute_script('return window.screen.height;')
    #Click on deny cookies
    try:
        driver.execute_script('document.querySelector(\"' + DELIVEROO_DENY_COOKIES_BUTTON_ID + '\").click()')
    except:
        print('Cookies did not pop up.')
    #Click on accept coupon
    try:
        driver.execute_script('document.querySelector(\"' + ACCEPT_COUPON_BUTTON_CLASS + '\").click()')
    except:
        print('Coupon did not pop up.')

    #Scroll to the end of the page, this loads all available restaurants
    i = 1
    while True:
        driver.execute_script("window.scrollTo(0, {screen_height} * {i});".format(screen_height=screen_height, i = i))
        i += 1
        time.sleep(scrollPauseTime)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if screen_height * i > scroll_height:
            break


    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    data = []
    for restaurant in soup.find_all(class_ = RESTAURANT_TAG_CLASS):
        rating = restaurant.find(class_ = RATING_TAG_CLASS)

        if rating == None:
            #Skip iteration
            continue
        if rating.text == 'New on Deliveroo':
            restaurantDetail = restaurant.find('a', class_ = HREF_TAG_CLASS)
            data.append(enter_restaurant_page(DELIVEROO_BASE_URL + restaurantDetail['href']))
            time.sleep(initialReconnectTime/2)


    return data
