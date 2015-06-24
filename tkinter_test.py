import tkinter
import tkinter.ttk
import queue
import threading
import time

class ThreadedTask(threading.Thread):
    def __init__(self, out_q, in_q):
        threading.Thread.__init__(self)
        self.in_q = in_q
        self.out_q = out_q
    def run(self):
        i = 0
        while True:
            self.out_q.put("%d -- WOO" % i)
            time.sleep(5)
            i += 1

in_q = queue.Queue()
out_q = queue.Queue()

def process_q():
    global in_q
    global status
    global root
    global captcha_entry
    while True:
        try:
            msg = in_q.get(0)
            print("HOLA: %s" % msg)
            if msg == "CAPTCHA":
                captcha_entry.configure(state='enabled')
                captcha_entry.focus()
            else:
                status.set(msg)
        except queue.Empty:
            root.after(100, process_q)
            break

root = tkinter.Tk()
root.title("Captcha!")

mainframe = tkinter.ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

captcha = tkinter.StringVar()
status = tkinter.StringVar()

image = tkinter.PhotoImage(file='captcha.gif')
image_view = tkinter.ttk.Label(mainframe, image=image)
image_view.grid(column=1, row=2, sticky=(tkinter.W, tkinter.E, tkinter.N))

captcha_entry = tkinter.ttk.Entry(mainframe, width=7, textvariable=captcha)
captcha_entry.grid(column=1, row=3, sticky=(tkinter.W, tkinter.E))

status_label = tkinter.ttk.Label(mainframe, textvariable=status)
status_label.grid(column=1, row=1, sticky=(tkinter.W, tkinter.E))

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

captcha_entry.configure(state='disabled')
# root.bind('<Return>', calculate)

process_q()
ThreadedTask(in_q, out_q).start()

root.mainloop()
