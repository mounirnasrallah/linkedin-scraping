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

LOGIN_URL="https://www.linkedin.com/login"
SEARCH_URL="https://www.linkedin.com/search/results/people/?"

driver = None

class LinkedInScraping:

    def __init__(self, args):
        self.args = args
        self.page = 1
        self.depth = 0

    def search_profiles_page(self, arguments):
        encoded_args = urlencode(arguments)
        self.driver.get(SEARCH_URL + encoded_args)

    def browse_results(self):
        results_profiles = self.driver.find_elements(By.CLASS_NAME, "entity-result__item")
        for profile in results_profiles:
            nameElement = profile.find_element(By.XPATH, ".//div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]")
            name = nameElement.text
            titleElement =  profile.find_element(By.XPATH,".//div[2]/div[1]/div[2]/div/div[1]")
            title = titleElement.text
            connectButtonDivElement =  profile.find_element(By.XPATH,".//div[3]")
            connectButtonElement =  connectButtonDivElement.find_element(By.CLASS_NAME,"ember-view")

            if (self.depth < self.args.depth):
                try:
                    connectButtonElement.click()
                except ElementClickInterceptedException:
                    confirmationButton = self.driver.find_element(By.XPATH,".//button[@aria-label='Send now']")
                    confirmationButton.click()
                    print(name, " , " ,title)
                    self.depth += 1


    def search_browse_all_profiles_by_company(self):
        for company in self.listCompanies:
            while (self.depth < self.args.depth):
                arguments = {'title': self.args.title, 'company': company, 'network': json.dumps(self.args.network), 'page': self.page}
                self.search_profiles_page(arguments)
                self.browse_results()
                self.page += 1
            self.page = 1
            self.depth = 0


    def login(self):
        self.driver.get(LOGIN_URL)
        print('Enter your email:')
        mail = input()
        password = getpass()
        self.driver.find_element(By.XPATH,'//*[@id="username"]').send_keys(mail)
        self.driver.find_element(By.XPATH,'//*[@id="password"]').send_keys(password)
        self.driver.find_element(By.XPATH,'/html/body/div/main/div[3]/div[1]/form/div[3]/button').click()

    def setup(self):
        geckodriver_autoinstaller.install()
        self.driver = webdriver.Firefox()
        self.login()
        if self.args.companyFile is not None:
            self.listCompanies = xlrd.open_workbook(self.args.companyFile)
        else:
            self.listCompanies = [self.args.company]


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
    group_company.add_argument('--companyFile', metavar='COMPANY_FILE', nargs='?', type=argparse.FileType('r'), help="File to read for companies name")

    parser.add_argument('--firstName', metavar='FIRST_NAME', type=str, nargs='?',
                        help='First Name')

    parser.add_argument('--lastName', metavar='LAST_NAME', type=str, nargs='?',
                    help='Last Name')

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

    args = parser.parse_args()

    if len(sys.argv) > 1:
        scraping = LinkedInScraping(args)
        scraping.run()
    else:
        parser.print_help()

main()
