import re
from urllib import urlencode
from getpass import getpass

import os
import pprint
import simplejson as json

import urllib2
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from jinja2 import FileSystemLoader, Environment

import argparse

######### config ############
PAGE_LOGIN = "https://jobmine.ccol.uwaterloo.ca/psp/SS/EMPLOYEE/WORK/"
PAGE_SEARCH = "https://jobmine.ccol.uwaterloo.ca/psc/SS/EMPLOYEE/WORK/c/UW_CO_STUDENTS.UW_CO_JOBSRCH"
PAGE_DETAIL = "https://jobmine.ccol.uwaterloo.ca/psp/SS_2/EMPLOYEE/WORK/c/UW_CO_STUDENTS.UW_CO_JOBDTLS.GBL?UW_CO_JOB_ID="

userid = ""
pwd = ""

SEARCH_CONSTANTS = {
    "UNSP": "ENG-(unspecified)",
    "CHEM": "ENG-Chemical",
    "CIV": "ENG-Civil",
    "COMP": "ENG-Computer",
    "ELEC": "ENG-Electrical",
    "ENV": "ENG-Environmental",
    "GEO": "ENG-Geological",
    "MAN": "ENG-Management",
    "MECH": "ENG-Mechanical",
    "TRON": "ENG-Mechatronics",
    "NANO": "ENG-Nanotechnology",
    "SOFT": "ENG-Software",
    "SYDE": "ENG-Systems Design"
}

parser = argparse.ArgumentParser(description='Search and login options for jobmine')
parser.add_argument('username', type=str,
                   help='your uwaterloo username')

parser.add_argument('-d1', '--discipline1', type=str, default="", choices=SEARCH_CONSTANTS,
                   help='discipline 1 code')

parser.add_argument('-d2', '--discipline2', type=str, default="", choices=SEARCH_CONSTANTS,
                   help='discipline 2 code')

parser.add_argument('-d3', '--discipline3', type=str, default="", choices=SEARCH_CONSTANTS,
                   help='discipline 3 code')

parser.add_argument('-t', '--title', type=str, default="",
                   help='job title search string')

parser.add_argument('-e', '--employer', type=str, default="",
                   help='employer search string')

parser.add_argument('-s', '--session', type=int, default=1149,
                   help='job session number, ex: 1149 = [1] 20[14] September[9]')

def prompt_credentials():
    print "Attempting to login as " + userid
    return getpass()
    
def lint(description):
    url = "http://joblint.org/ws"
    header = { "User-Agent" : "jobmine linter/0.1" , "Content-type": "application/json" }
    values = { "spec" : description }
    req = urllib2.Request(url, json.dumps(values), header)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def login(driver, userid, pwd):
    print "Trying to login..."
    driver.get(PAGE_LOGIN)
    time.sleep(1)
    driver.find_element_by_id("userid").send_keys(userid)
    driver.find_element_by_id("pwd").send_keys(pwd)
    driver.find_element_by_id("login").find_element_by_xpath("//input[@type='submit'][@name='submit']").submit()

    noentry = "User ID and Password are required." not in driver.page_source
    invalid = "Your User ID and/or Password are invalid." not in driver.page_source
    return noentry and invalid
    
def search(driver, options):
    driver.get(PAGE_SEARCH)
    xpath = "//select[@name='UW_CO_JOBSRCH_UW_CO_ADV_DISCP%s']/option[text()='%s']"
    driver.find_element_by_xpath(xpath % ('1', options['discp1'])).click()
    driver.find_element_by_xpath(xpath % ('2', options['discp2'])).click()
    driver.find_element_by_xpath(xpath % ('3', options['discp3'])).click()
    driver.find_element_by_id("UW_CO_JOBSRCH_UW_CO_EMPLYR_NAME").send_keys(options['employer'])
    driver.find_element_by_id("UW_CO_JOBSRCH_UW_CO_JOB_TITLE").send_keys(options['title'])
    driver.find_element_by_id("UW_CO_JOBSRCH_UW_CO_WT_SESSION").send_keys(options['session'])
    
    driver.find_element_by_id("UW_CO_JOBSRCHDW_UW_CO_DW_SRCHBTN").click() # search
    time.sleep(5)

def download_list(driver):
    driver.find_element_by_id("UW_CO_JOBRES_VW$hexcel$0").click()
    
def jobs_from_xls():
    directory = os.path.realpath(".")
    file = os.path.join(directory, "ps.xls")
    f = open(file, 'r')
    jobs = []
    for line in f:
        job_id = re.search('([0-9]{8})',  line)
        if job_id:
            jobs.append(job_id.group(1))
    f.close()
    return jobs

def progress(percent, barLen = 20):
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
    sys.stdout.flush()

def scrape(driver, job_ids):
    pp = pprint.PrettyPrinter(indent=4)
    
    jobs = {}
    interesting_jobs = {}
    count = 0
    
    for job_id in job_ids:
        driver.get(PAGE_DETAIL + job_id)
        #source = driver.page_source
        link = driver.find_element_by_id("ptifrmtgtframe").get_attribute("src")
        driver.get(link)
        
        description = driver.find_element_by_id("UW_CO_JOBDTL_VW_UW_CO_JOB_DESCR").text
        title = driver.find_element_by_id("win2divUW_CO_JOBDTL_VW_UW_CO_JOB_TITLE").text
        employer = driver.find_element_by_id('UW_CO_JOBDTL_DW_UW_CO_EMPUNITDIV').text
        location = driver.find_element_by_id('UW_CO_JOBDTL_VW_UW_CO_WORK_LOCATN').text
        
        linted_description = lint(description)
        jobs[job_id] = {'lint': linted_description, 
                        'employer': employer,
                        'title': title,
                        'detail': PAGE_DETAIL + job_id,
                        'location': location,
                        'id': job_id}

        for key, value in linted_description['failPoints'].items():
            if (key == "culture" or key == "realism") and value:
                interesting_jobs[job_id] = jobs[job_id]
                break

        progress(count/float(len(job_ids)))
        count += 1
        
    print("Found %s jobs!" % len(interesting_jobs))
    #pp.pprint(jobs)
    #pp.pprint(interesting_jobs)
    return interesting_jobs

def build_template(jobs):
    file = 'main.html'
    directory = os.path.realpath(".")
    output_file = os.path.join(directory, "jobs.html")
    template_loader = FileSystemLoader(searchpath=directory)
    env = Environment(loader=template_loader)
    template = env.get_template( file )
    template_vars = {"jobs": jobs}
    output = template.render(template_vars)
    f = open(output_file, "w")
    f.write(output)
    f.close()

if __name__ == "__main__":
    directory = os.path.realpath(".")

    args = parser.parse_args()

    profile = webdriver.firefox.firefox_profile.FirefoxProfile()
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", directory)

    driver = webdriver.Firefox(firefox_profile=profile)

    userid = args.username
    pwd = prompt_credentials()

    loggedIn = False
    while not loggedIn:
        loggedIn = login(driver, userid, pwd)
        if not loggedIn:
            "Login failed... "
            pwd = prompt_credentials()
    
    print "Logged in!"

    options = {
        "discp1": SEARCH_CONSTANTS[args.discipline1],
        "discp2": SEARCH_CONSTANTS[args.discipline2],
        "discp3": SEARCH_CONSTANTS[args.discipline3],
        "session": args.session,
        "employer": args.employer,
        "title": args.title
    }

    search(driver, options)
    download_list(driver)
    job_ids = jobs_from_xls()
    job_items = scrape(driver, job_ids)
    build_template(job_items)
    driver.close()
    print("I'm done finding your results! They are in 'jobs.html'. Take a look!")