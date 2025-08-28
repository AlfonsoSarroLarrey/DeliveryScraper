import json
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from bs4 import BeautifulSoup


# Regardless of where you are in the UK, by changing the postcode, the url will automatically change
# Because of the above, there is no need to change westminster

postcode = 'SW1A 2AA'
DELIVEROO_BASE_URL = f'https://deliveroo.co.uk'
DELIVEROO_MAIN_PAGE = f'/restaurants/london/westminster?postcode={postcode}&collection=all-restaurants'

JUST_EAT_URL = f'http://www.just-eat.co.uk/area/{postcode}?filter=new'

DENY_COOKIES_BUTTON_ID =  '#onetrust-reject-all-handler'
ACCEPT_COUPON_BUTTON_CLASS = '.ccl-388f3fb1d79d6a36.ccl-6d2d597727bd7bab.ccl-59eced23a4d9e077.ccl-7be8185d0a980278'

RESTAURANT_TAG_CLASS = 'HomeFeedGrid-b0432362335be7af'
RATING_TAG_CLASS = 'css-87fssf'
HREF_TAG_CLASS = 'css-1hms87c'
#Close not currently accepting orders ccl-364e2ed6a76f91e9
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

####################### JUST EAT ####################################
NECESSARY_ONLY_BUTTON_CLASS_1 = 'o-btn'
NECESSARY_ONLY_BUTTON_CLASS_2 = 'o-btn--fullWidth'
NECESSARY_ONLY_BUTTON_CLASS_3 = 'o-btn--primary'
NECESSARY_ONLY_BUTTON_CLASS_4 = 'o-btn--small-expressive'

#Position of the deny cookies button in the page.
#There are 2 buttons with the same classes, 0 being "accept" and 1 being "necessary only"
NECESSARY_ONLY_BUTTON = 1

SPAN_BUTTON_TAG_CLASS = '_9NUh1 nutrition-info-icon-style_content__wbyIS'
INFO_BUTTON_DATA_QA = 'about-us-button-action-info'

PREORDER_BUTTON_DATA_QA = 'preorder-notification-modal-header-action-close'
INITIAL_RECONNECT_TIME = 6
SCROLL_PAUSE_TIME = 0.0001

finalData = []


def getAddressPosition(restaurantInfo):
    for i in range(len(restaurantInfo) - 1, -1, -1):
        if restaurantInfo[i].find('span').find('span').text == "View map":
            i -= 1
            return i
        
    return 0



def enter_restaurant_page(url):
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
    driver.uc_open_with_reconnect(url, reconnect_time=INITIAL_RECONNECT_TIME)

    while refresh:
    # Attempt to click the CAPTCHA checkbox if present
        driver.uc_gui_click_captcha()

        try:
            driver.execute_script('document.querySelector(\"' + DENY_COOKIES_BUTTON_ID + '\").click()')
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

    finalData.append(restaurantInfo)


def scrapeDeliveroo(driver):
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(DELIVEROO_BASE_URL + DELIVEROO_MAIN_PAGE, reconnect_time=INITIAL_RECONNECT_TIME)
    
    # Attempt to click the CAPTCHA checkbox if present
    driver.uc_gui_click_captcha()


    screen_height = driver.execute_script('return window.screen.height;')
    #Click on deny cookies
    try:
        driver.execute_script('document.querySelector(\"' + DENY_COOKIES_BUTTON_ID + '\").click()')
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
        time.sleep(SCROLL_PAUSE_TIME)
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
            enter_restaurant_page(DELIVEROO_BASE_URL + restaurantDetail['href'])
            time.sleep(INITIAL_RECONNECT_TIME/2)

def scrapeJustEat(driver):
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(JUST_EAT_URL, reconnect_time=INITIAL_RECONNECT_TIME)
    
    # Attempt to click the CAPTCHA checkbox if present
    driver.uc_gui_click_captcha()
    #driver.get(JUST_EAT_URL)

    screen_height = driver.execute_script('return window.screen.height;')
    #Click on deny cookies
    #buttons = driver.find_elements(by=By.XPATH, value="//pie-button")#[contains(@class, '" + NECESSARY_ONLY_BUTTON_CLASS_1 + "')]") #and contains(@class, '" + NECESSARY_ONLY_BUTTON_CLASS_2 + "') and contains(@class, '" + NECESSARY_ONLY_BUTTON_CLASS_3 + "') and contains(@class, '" + NECESSARY_ONLY_BUTTON_CLASS_4 + "')]")

    #if buttons != None:
        #buttons[0].click()
    #else:
        #print('Cookies did not pop up.')
    page = driver.find_element(By.TAG_NAME, 'html')
    #Scroll to the end of the page, this loads all available restaurants
    i = 1
    while True:
        page.send_keys(Keys.PAGE_DOWN)
        #driver.execute_script("window.scrollTo(0, {screen_height} * {i});".format(screen_height=screen_height, i = i))
        #i += 1
        time.sleep(SCROLL_PAUSE_TIME)
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
    for restaurant in soup.find_all(class_ = RESTAURANT_TAG_CLASS):
        rating = restaurant.find(class_ = RATING_TAG_CLASS)

        if rating == None:
            #Skip iteration
            continue
        if rating.text == 'New on Deliveroo':
            restaurantDetail = restaurant.find('a', class_ = HREF_TAG_CLASS)
            enter_restaurant_page(DELIVEROO_BASE_URL + restaurantDetail['href'])
            time.sleep(INITIAL_RECONNECT_TIME/2) 

############################ MAIN ##########################################

driverDeliveroo = Driver(uc=True, headless=False)
driverJustEat = Driver(uc=True, headless=False)

scrapeDeliveroo(driverDeliveroo)
scrapeJustEat(driverJustEat)
  
with open('output.json', 'w') as file:
    json.dump(finalData, file, indent=4)