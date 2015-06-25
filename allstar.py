from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import readline
import re
import time
import sys
import tkinter as tk
import tkinter.ttk as ttk
import queue
import threading
from PIL import Image

class ThreadedTask(threading.Thread):
    def __init__(self, cont):
        threading.Thread.__init__(self)
        self.controller = cont
    def run(self):
        browser = webdriver.PhantomJS()
        browser.set_window_size(1900, 3000)
        self.controller.set_status("Loading MLB All-Star page")
        browser.get('http://www.mlb.com/mlb/events/all_star/y2015/ballot.jsp')
        self.controller.set_status("Loaded")

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

        email = self.controller.prompt_question("Email address: ")
        while True:
            dob = self.controller.prompt_question("DOB: ")
            retest = re.match(r"""(\d{1,2})/(\d{1,2})/(\d{4})""", dob)
            if retest:
                dobmonth = int(retest.group(1), base=10)
                dobday = int(retest.group(2), base=10)
                dobyear = int(retest.group(3), base=10)
                break
            else:
                self.controller.set_status("Expected format: MM/DD/YYYY")
                time.sleep(2)
        zipcode = self.controller.prompt_question("Zip: ")

        while True:
            self.controller.set_status("Voting for players")

            for p in players:
                self.controller.set_status("Voting for %s" % p)
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

            self.controller.set_status("Clicking vote")
            browser.find_element_by_id("vote-now").click()

            registration = browser.find_element_by_id("register_vote")

            # Fill in e-mail
            self.controller.set_status("Filling out form")
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
                loaded = False
                for i in range(0, 50):
                    size = full_captcha.size
                    if size['height'] == 0 or size['width'] == 0:
                        time.sleep(0.25)
                    else:
                        time.sleep(0.25)
                        loaded = True
                        break
                if loaded:
                    location = full_captcha.location
                    scrollX = int(browser.execute_script('return window.scrollX'))
                    scrollY = int(browser.execute_script('return window.scrollY'))
                    left = int(location['x']) - scrollX
                    top = int(location['y']) - scrollY
                    right = left + int(size['width'])
                    bottom = top + int(size['height'])
                    browser.save_screenshot('screenshot.png')

                    im = Image.open('screenshot.png')
                    im = im.crop((left, top, right, bottom))
                    im.save('captcha.gif')

                    res = self.controller.prompt_captcha("captcha.gif")

                    captcha.send_keys(res)
                button = browser.find_element_by_xpath('//a[contains(@id, "vote-now-button") and not(ancestor::div[contains(@style, "display: none")])]')
                browser.execute_script('window.vote_alert_text = ""; window.alert = function(t) { window.vote_alert_text = t };')
                self.controller.set_status("Voting")

                while True:
                    button.click()
                    try:
                        ensure_switched(captcha)
                    except ClickError:
                        continue
                    break

                alert_text = browser.execute_script('return window.vote_alert_text')
                voted_35 = False
                if len(alert_text) > 0:
                    print("ALERT! %s" % alert_text)
                    if re.search('voted 35 times', alert_text):
                        voted_35 = True
                    try:
                        ensure_switched(captcha)
                    except:
                        pass

                if voted_35:
                    break

            print("Voted 35 times!")
            browser.find_element_by_xpath('//a[text()[contains(.,"Clear and fill out a new ballot")]]').click()
            email = self.controller.prompt_question("Email address: ")

class Question(object):
    def __init__(self, q):
        self.q = q

class Captcha(object):
    def __init__(self, img):
        self.img = img

class Status(object):
    def __init__(self, s):
        self.s = s

class AllStarApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry('250x100')
        self.title('All-Star Voting')
        self.in_q = queue.Queue()
        self.out_q = queue.Queue()

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=tk.YES)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (CaptchaPage, StatusPage, PromptPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.in_q.put(Status("Royals All-Star Voting!"))
        self.process_queue()

    def process_queue(self):
        try:
            a = self.in_q.get_nowait()
            if type(a) is Status:
                self.show_frame(StatusPage)
                self.frames[StatusPage].set_status(a.s)
            elif type(a) is Captcha:
                self.show_frame(CaptchaPage)
                self.frames[CaptchaPage].prompt_captcha(a.img)
            elif type(a) is Question:
                self.show_frame(PromptPage)
                self.frames[PromptPage].prompt_question(a.q)
        except queue.Empty:
            pass
        self.after(250, self.process_queue)

    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()

    def prompt_question(self, q):
        self.in_q.put(Question(q))
        return self.out_q.get(block=True, timeout=None)

    def set_status(self, s):
        self.in_q.put(Status(s))

    def prompt_captcha(self, img):
        self.in_q.put(Captcha(img))
        return self.out_q.get(block=True, timeout=None)

class CaptchaPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.label = tk.Label(self)
        self.label.grid(column=0, row=0, columnspan=2, sticky="n", pady=5)
        clabel = ttk.Label(self, text="Captcha:")
        clabel.grid(column=0, row=1, sticky="nw")
        self.captcha = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.captcha)
        self.entry.grid(column=1, row=1, sticky="new")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def pressed_enter(self, event):
        self.controller.out_q.put(self.captcha.get())
        self.controller.unbind("<Return>", self.binding)
        print("Captcha was %s" % self.captcha.get())

    def prompt_captcha(self, c):
        self.captcha.set("")
        image = tk.PhotoImage(file=c)
        self.label.configure(image=image, compound="none")
        self.label.image = image
        self.binding = self.controller.bind("<Return>", self.pressed_enter)
        self.entry.focus_set()
        print("Prompting captcha (%s)..." % c)

class StatusPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.status = tk.StringVar()
        label1 = ttk.Label(self, text="Status: ")
        label2 = ttk.Label(self, textvariable=self.status)
        label1.grid(column=0, row=0, sticky="nw")
        label2.grid(column=1, row=0, sticky="nwe")
        self.status.set("This is a test")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def set_status(self, s):
        print("Status: %s" % s)
        self.status.set(s)

class PromptPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.question = tk.StringVar()
        self.answer = tk.StringVar()
        qlabel = ttk.Label(self, textvariable=self.question)
        qlabel.grid(row=0, column=0, sticky="nw")
        self.entry = ttk.Entry(self, textvariable=self.answer)
        self.entry.grid(row=0, column=1, sticky="nwe")
        self.question.set("Favorite color?")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def pressed_enter(self, event):
        self.controller.out_q.put(self.answer.get())
        self.controller.unbind("<Return>", self.binding)
        print(self.answer.get())

    def prompt_question(self, q):
        self.question.set(q)
        self.answer.set("")
        self.binding = self.controller.bind("<Return>", self.pressed_enter)
        self.entry.focus_set()
        print(q)

app = AllStarApp()

ThreadedTask(app).start()
app.mainloop()
