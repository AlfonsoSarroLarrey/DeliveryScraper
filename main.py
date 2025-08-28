import json
from seleniumbase import Driver
from deliveroo import scrapeDeliveroo
from justeat import scrapeJustEat


# Regardless of where you are in the UK, by changing the postcode, the url will automatically change
# Because of the above, there is no need to change westminster

postcode = 'SW1A 2AA'



INITIAL_RECONNECT_TIME = 6
SCROLL_PAUSE_TIME = 0.0001

finalData = []



 

############################ MAIN ##########################################

driverDeliveroo = Driver(uc=True, headless=False)
driverJustEat = Driver(uc=True, headless=False)

scrapeDeliveroo(driverDeliveroo, postcode, INITIAL_RECONNECT_TIME, SCROLL_PAUSE_TIME)
scrapeJustEat(driverJustEat, postcode, INITIAL_RECONNECT_TIME, SCROLL_PAUSE_TIME)
  
with open('output.json', 'w') as file:
    json.dump(finalData, file, indent=4)