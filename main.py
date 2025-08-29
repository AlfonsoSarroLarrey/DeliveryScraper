import json
import csv
from seleniumbase import Driver
from deliveroo import scrapeDeliveroo
from justeat import scrapeJustEat


INITIAL_RECONNECT_TIME = 6
SCROLL_PAUSE_TIME = 0.0001

finalData = []

#Read csv with all postcodes
with open('PostalCodes.csv', 'r') as csvfile:
    csvReader = csv.reader(csvfile)

    # Every line has the name of the postcode and the list of postcodes
    for line in csvReader:
        # We get the list of postcodes
        postcodeList = line[1].split(',')

        for postcode in postcodeList:
            print(postcode)
            driverJustEat = Driver(uc=True, headless=False)
            driverDeliveroo = Driver(uc=True, headless=False)

            finalData.append(scrapeJustEat(driverJustEat, postcode, INITIAL_RECONNECT_TIME, SCROLL_PAUSE_TIME))
            finalData.append(scrapeDeliveroo(driverDeliveroo, postcode, INITIAL_RECONNECT_TIME, SCROLL_PAUSE_TIME))

        









with open('output.json', 'w') as file:
    json.dump(finalData, file, indent=4)