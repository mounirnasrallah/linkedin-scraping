import geckodriver_autoinstaller
from selenium import webdriver
import certifi
import urllib3
from urllib.parse import urlencode
import argparse
import xlrd
import sys
from getpass import getpass
from selenium.webdriver.common.by import By
import json
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import time
import random
import csv

LOGIN_URL="https://www.linkedin.com/login"
SEARCH_URL="https://www.linkedin.com/search/results/people/?"

driver = None

class LinkedInScraping:

    def __init__(self, args):
        self.args = args
        self.page = 1
        self.depth = 0
        self.listCompanies = []
        self.outputFile = open(args.outputFile, 'w', newline='')
        self.owner = args.owner

    def search_profiles_page(self, arguments):
        encoded_args = urlencode(arguments)
        self.driver.get(SEARCH_URL + encoded_args)
        time.sleep(3)

    def browse_results(self, company):
        results_profiles = self.driver.find_elements(By.CLASS_NAME, "entity-result__item")
        for profile in results_profiles:
            try:
                nameElement = profile.find_element(By.XPATH, ".//div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]")
                fullName = nameElement.text
                name = fullName.split(" ", 1)
                if len(name) < 2:
                    name.append("")

                titleElement =  profile.find_element(By.XPATH,".//div[2]/div[1]/div[2]/div/div[1]")
                title = titleElement.text
                titleElement =  profile.find_element(By.XPATH,".//div[2]/div[1]/div[2]/div/div[1]")
                connectButtonDivElement = profile.find_element(By.XPATH,".//div[3]")
                connectButtonElement = profile.find_element(By.XPATH,".//button[span[text()='Connect']]")
                #print(connectButtonDivElement.get_attribute('innerHTML'))
                #connectButtonElement =  connectButtonDivElement.find_element(By.XPATH,".//button")
                #textButton = connectButtonElement.text

                print(self.depth, self.owner, name[0], name[1], company, title, ' ', 'Internet', 'Premier contact réalisé (LinkedIn)')

                print(" ------------------------- ")
                print(profile.get_attribute('innerHTML'))
                print(" ------------------------- ")

                #if textButton == "Connect":
                if (self.depth < self.args.depth):
                    added = False
                    try:
                        time.sleep(random.randrange(1,4))
                        connectButtonElement.click()
                    except ElementClickInterceptedException:
                        print ("Connect button not clickable")
                    except NoSuchElementException:
                        print("Nothing to do (already added or message).")

                    try:
                        confirmationButton = self.driver.find_element(By.XPATH,".//button[@aria-label='Send now']")
                        confirmationButton.click()
                        self.depth += 1
                        added = True
                    except NoSuchElementException:
                        try:
                            print("No simple confirmation")
                            doubleConfirmationButton = self.driver.find_element(By.XPATH,".//button[@aria-label='No']")
                            doubleConfirmationButton.click()
                            self.depth += 1
                            added = True
                        except NoSuchElementException:
                            print("No double confirmation")

                    if added is True:
                        csvWriter = csv.writer(self.outputFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        csvWriter.writerow([self.owner, name[0], name[1], company, title, ' ', 'Internet', 'Premier contact réalisé (LinkedIn)'])
                        print(self.owner,',', name[0],',', name[1],',', company,',', title,',', '',',', 'Internet',',', 'Premier contact réalisé (LinkedIn)')
                time.sleep(1)

            except NoSuchElementException:
                print("Nothing to do")



    def search_browse_all_profiles_by_company(self):
        if self.listCompanies is None:
            while (self.depth < self.args.depth):
                arguments = {'title': self.args.title, 'network': json.dumps(self.args.network), 'page': self.page}
                if self.location is not None:
                    arguments['geoUrn'] = json.dumps(self.location)
                    self.search_profiles_page(arguments)
                    self.browse_results("?")
                    time.sleep(5)
                    self.page += 1
        else:
            for company in self.listCompanies:
                while ((self.depth < self.args.depth) and (self.page < (self.args.depth / 2)) ):
                    arguments = {'title': self.args.title, 'company': company, 'network': json.dumps(self.args.network), 'page': self.page}
                    if self.location is not None:
                        arguments['geoUrn'] = json.dumps(self.location)

                    self.search_profiles_page(arguments)
                    self.browse_results(company)
                    self.page += 1
            self.page = 1
            self.depth = 0


    def login(self):
        self.driver.get(LOGIN_URL)
        print('Enter your email:')
        mail = input()
        password = getpass()
        self.driver.find_element(By.ID,'username').send_keys(mail)
        self.driver.find_element(By.ID,'password').send_keys(password)
        self.driver.find_element(By.XPATH,".//button[@aria-label='Sign in']").click()
        print("Ready to continue?")
        _ = input()

    def setup(self):
        geckodriver_autoinstaller.install()
        self.driver = webdriver.Firefox()
        self.login()
        if self.args.companyFile is not None:
            #self.listCompanies = xlrd.open_workbook(self.args.companyFile)
            with open(self.args.companyFile, "r") as csvCompanyFile:
                csvReader = csv.reader(csvCompanyFile, delimiter=',')
                for line in csvReader:
                    self.listCompanies.append(line[0])
        else:
            self.listCompanies = self.args.company
        if self.args.location is not None:
            if self.args.location == "France":
                self.location = ["105015875"]
        else:
            self.location = None

    def run(self):
        self.setup()
        self.search_browse_all_profiles_by_company()

    def close(self):
        self.driver.close()





def main():

    parser = argparse.ArgumentParser(description='LinkedIn Scraping', prog="linkedin-scraping")

    parser.add_argument('--depth', required=True, metavar='depth', type=int, nargs='?',
                    help='Depth')

    group_company = parser.add_mutually_exclusive_group()
    group_company.add_argument('--company', metavar='COMPANY_NAME', type=str, nargs='?',
                    help='Current company')
    group_company.add_argument('--companyFile', metavar='COMPANY_FILE', nargs='?', type=str, help="File to read for companies name")

    parser.add_argument('--firstName', metavar='FIRST_NAME', type=str, nargs='?',
                        help='First Name')

    parser.add_argument('--lastName', metavar='LAST_NAME', type=str, nargs='?',
                    help='Last Name')

    parser.add_argument('--location', metavar='LOCATION', type=str, nargs='?',
                        help='Location')

    group_title = parser.add_mutually_exclusive_group()
    group_title.add_argument('--title', metavar='TITLE', type=str, nargs='?',
                    help='Title')
    group_title.add_argument('--titleFile', metavar='TITLE_FILE', nargs='?', type=argparse.FileType('r'), help="File to read for titles")

    parser.add_argument('--network', type=lambda x: list(map( lambda y: "F" if y == "1" else "S" if y == "2" else "O", x.split(','))), nargs='?',
                        help='Network: values between 1 and 3', default=3)

    group_invitation_message = parser.add_mutually_exclusive_group()
    group_invitation_message.add_argument('--invitationMessage', metavar='MESSAGE', type=str, nargs='?',
                    help='Message to send')
    group_invitation_message.add_argument('--invitationMessageFile', metavar='INVITATION_MESSAGE_FILE', nargs='?', type=argparse.FileType('r'), help="File for the invitation message")

    group_message = parser.add_mutually_exclusive_group()
    group_message.add_argument('--message', metavar='MESSAGE', type=str, nargs='?',
                    help='Message to send')
    group_message.add_argument('--messageFile', metavar='MESSAGE_FILE', nargs='?', type=argparse.FileType('r'), help="File for the message")

    parser.add_argument('--owner', metavar='OWNER', nargs='?', type=str, help="Account owner")

    parser.add_argument('--outputFile', metavar='OUTPUT_FILE', nargs='?', type=str, help="File to write")

    args = parser.parse_args()

    if len(sys.argv) > 1:
        scraping = LinkedInScraping(args)
        scraping.run()
    else:
        parser.print_help()

main()
