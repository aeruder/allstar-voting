from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import readline
import re
import time
import sys
import tkinter
from PIL import Image

browser = webdriver.Chrome()
browser.get('http://www.mlb.com/mlb/events/all_star/y2015/ballot.jsp')

class ClickError(Exception):
    pass

def ensure_switched(captcha):
    broke = False
    for i in range(0, 50):
        try:
            time.sleep(0.25)
            captcha.click()
        except:
            broke = True
            break
    if not broke:
        raise ClickError()

players = [
    "Hosmer, E",
    "Rizzo, A",
    "Infante, O",
    "La Stella, T",
    "Escobar, A",
    "Castro, S",
    "Moustakas, M",
    "Bryant, K",
    "Perez, S",
    "Montero, M",
    "Morales, K",
    "Cain, L",
    "Gordon, A",
    "Rios, A",
    "Aoki, N",
    "Coghlan, C",
    "Fowler, D"
]
buttons = {}

email = input("Email address: ")
while True:
    dob = input("DOB: ")
    retest = re.match(r"""(\d{1,2})/(\d{1,2})/(\d{4})""", dob)
    if retest:
        dobmonth = int(retest.group(1), base=10)
        dobday = int(retest.group(2), base=10)
        dobyear = int(retest.group(3), base=10)
        break
    else:
        print("Expected format: MM/DD/YYYY")
zipcode = input("Zip: ")

while True:
    print("Voting for players")

    for p in players:
        print("Voting for %s" % p)
        xpath = '//*[text()[.="%s"]]/../../..//span[@class="selectBtn"]' % p
        voted_xpath = '//div[@class="playerSelectedInfo"]/*[text()[.="Hosmer, E"]][@class="playerName"]'
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        voting_happened = False
        while not voting_happened:
            browser.find_element_by_xpath(xpath).click()
            for i in range(0, 50):
                try:
                    browser.find_element_by_xpath(voted_xpath)
                    voting_happened = True
                    break
                except:
                    time.sleep(0.25)

    browser.find_element_by_id("vote-now").click()

    registration = browser.find_element_by_id("register_vote")

    # Fill in e-mail
    registration.find_element_by_id("e").send_keys(email)
    webdriver.support.select.Select(registration.find_element_by_id("bd_m")).select_by_value("%s" % dobmonth)
    webdriver.support.select.Select(registration.find_element_by_id("bd_d")).select_by_value("%s" % dobday)
    webdriver.support.select.Select(registration.find_element_by_id("bd_y")).select_by_value("%s" % dobyear)
    registration.find_element_by_id("z").send_keys(zipcode)
    webdriver.support.select.Select(registration.find_element_by_id("ft1")).select_by_value("kc")

    spam = registration.find_element_by_id("on")
    if spam.is_selected():
        spam.click()

    times = 0

    while True:
        xpath = '//input[contains(@id, "v2-") and @name = "v2" and not(ancestor::div[contains(@style, "display: none")])]'
        captcha_xpath = '//input[contains(@id, "v2-") and @name = "v2" and not(ancestor::div[contains(@style, "display: none")])]/../../../..//img'
        captcha = browser.find_element_by_xpath(xpath)
        captcha.click()
        full_captcha = browser.find_element_by_xpath(captcha_xpath)
        location = full_captcha.location
        size = full_captcha.size
        left = int(location['x']) - int(browser.execute_script('return window.scrollX'))
        top = int(location['y']) - int(browser.execute_script('return window.scrollY'))
        right = left + int(size['width'])
        bottom = top + int(size['height'])
        browser.save_screenshot('screenshot.png')

        im = Image.open('screenshot.png')
        im = im.crop((left, top, right, bottom))
        im.save('captcha.gif')

        res = input("Captcha: ")

        captcha.send_keys(res)
        button = browser.find_element_by_xpath('//a[contains(@id, "vote-now-button") and not(ancestor::div[contains(@style, "display: none")])]')

        while True:
            button.click()
            try:
                ensure_switched(captcha)
            except ClickError:
                continue
            break

        voted_35 = False
        try:
            alert = browser.switch_to_alert()
            if re.search('voted 35 times', alert.text):
                voted_35 = True
            alert.accept()
            ensure_switched(captcha)
        except:
            pass

        if voted_35:
            break

    print("Voted 35 times!")
    browser.find_element_by_xpath('//a[text()[contains(.,"Clear and fill out a new ballot")]]').click()
    email = input("Email address: ")
