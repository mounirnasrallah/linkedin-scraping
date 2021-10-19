import geckodriver_autoinstaller
from selenium import webdriver
import certifi
import urllib3
from urllib.parse import urlencode
import argparse

SEARCH_URL="https://www.linkedin.com/search/results/all/"

driver = None

class LinkedInScraping:

    driver = None

    def search_profiles(args):
        encoded_args = urlencode(args)
        driver.get(SEARCH_URL + en)

    def setup():
        geckodriver_autoinstaller.install()
        driver = webdriver.Firefox()

    def close():
        driver.close()



def main():

    parser = argparse.ArgumentParser(description='LinkedIn Scraping', prog="linkedin-scraping")

    group_company = parser.add_mutually_exclusive_group()
    group_company.add_argument('--company', metavar='COMPANY_NAME', type=str, nargs='?',
                    help='Current company')

    group_company.add_argument('--companyFile', metavar='COMPANY_FILE', nargs='?', type=argparse.FileType('r'), help="File to read for companies name")

    parser.add_argument('--firstName', metavar='FIRST_NAME', type=str, nargs='?',
                        help='First Name')

    parser.add_argument('--lastName', metavar='LAST_NAME', type=str, nargs='?',
                    help='Last Name')

    group_school = parser.add_mutually_exclusive_group()
    group_school.add_argument('--schoolName', metavar='SCHOOL_NAME',type=str, nargs='?',
                    help='School name')

    group_school.add_argument('--schoolFile', metavar='SCHOOL_FILE', nargs='?', type=argparse.FileType('r'), help="File to read for schools name")

    group_title = parser.add_mutually_exclusive_group()
    group_title.add_argument('--title', metavar='TITLE', type=str, nargs='?',
                    help='Title')

    group_title.add_argument('--titleFile', metavar='TITLE_FILE', nargs='?', type=argparse.FileType('r'), help="File to read for titles")

    parser.add_argument('--connections', type=int, choices=range(1, 4), nargs='?', action='append',
                    help='Connections between 1 and 3')

    parser.add_argument('--outputFile', metavar='OUTPUT_FILE', nargs='?', type=argparse.FileType('r'), help="Output file")

    args = parser.parse_args()

    parser.print_help()

main()
