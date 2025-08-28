import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from bs4 import BeautifulSoup

finalData = []

JUST_EAT_URL_PART1 = 'http://www.just-eat.co.uk/area/'
JUST_EAT_URL_PART2 = '?filter=new'


#Close not currently accepting orders ccl-364e2ed6a76f91e9

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

def scrapeJustEat(driver, postcode, initialReconnectTime, scrollPauseTime):
    # Open URL using UC mode with 6 second reconnect time to bypass initial detection
    driver.uc_open_with_reconnect(JUST_EAT_URL_PART1 + postcode + JUST_EAT_URL_PART2, reconnect_time=initialReconnectTime)
    
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
        time.sleep(scrollPauseTime)
        try:
            driver.find_element(By.TAG_NAME, 'footer')
        except:
            #If no footer found, continue scrolling
            continue
        
        #If footer found, stop scrolling
        break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #driver.quit()

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