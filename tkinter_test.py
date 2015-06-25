import tkinter as tk
import tkinter.ttk as ttk
import queue
import threading
import time

class ThreadedTask(threading.Thread):
    def __init__(self, cont):
        threading.Thread.__init__(self)
        self.controller = cont
    def run(self):
        self.controller.set_status("Test status")
        time.sleep(5)
        print(self.controller.prompt_question("What is your name?"))
        print(self.controller.prompt_captcha("captcha.gif"))

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
        self.in_q.put(Captcha('captcha.gif'))
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

    def prompt_captcha(self, c):
        self.captcha.set("")
        image = tk.PhotoImage(file=c)
        self.label.configure(image=image, compound="none")
        self.label.image = image
        self.binding = self.controller.bind("<Return>", self.pressed_enter)
        self.entry.focus_set()

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

    def prompt_question(self, q):
        self.question.set(q)
        self.answer.set("")
        self.binding = self.controller.bind("<Return>", self.pressed_enter)
        self.entry.focus_set()

app = AllStarApp()

ThreadedTask(app).start()
app.mainloop()
