import tkinter as tk
from time import sleep 
import threading
import queue


threads = []

class ThreadedClient(threading.Thread):

    def __init__(self, qe, fcn):
        threading.Thread.__init__(self)
        self.qe = qe
        self.fcn = fcn

    def run(self):
        sleep(1)
        self.qe.put(self.fcn())

def spawnthread(fcn):
    thread = ThreadedClient(qe, fcn)
    thread.start()
    global threads
    threads.append(thread)
    periodiccall(thread)


def periodiccall(thread):
    if (thread.is_alive()):
        thread.After(100, lambda: periodiccall(thread))



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hey
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.quitter)
        self.quit.pack(side="bottom")
        self.button_speak = tk.Button(self, text="SPEAK", fg="red",
                              command=lambda: spawnthread(self.speak))
        self.button_speak.pack(side="bottom")


    def quitter(self):
        for thread in threads:
            thread.stop()
        self.master.destroy()


    def say_hey(self):
        print("Hey !")

    def speak(self):
        msg = "Hi there !"
        i = 0
        while 1:
            print(msg[:i])
            i = i%len(msg)+1
            sleep(0.2)


qe = queue.Queue()
root = tk.Tk()
app = Application(master=root)
app.mainloop()