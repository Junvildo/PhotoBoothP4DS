import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk
import datetime
import os

from PIL import ImageTk, Image
from notifypy import Notify
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import json


class VideoFeed:
    def __init__(self, video_source):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = cv2.resize(frame, (640, 480))
            if ret:
                return (ret, frame)
            else:
                return (ret, None)


class App:
    def __init__(self, window, window_title, video_source=0, output_path="./", BG_path="./"):
        # App Variables
        self.window = window
        self.window.title(window_title)

        self.feed_state = "Default"

        self.video_source = video_source

        self.imgBG = (0, 0, 0)
        self.curr_state = None

        self.segmentor = SelfiSegmentation()
        self.is_segment = 0

        self.output_path = output_path
        self.BG_path = BG_path
        
        self.settings = {}
        # App background
        #bg = tk.PhotoImage(file="bg.png")
        #bg1 = tk.Label(self.window, image=bg)
        #bg1.place(x=0, y=0)

        # App Layout and Elements
        f11 = tk.Frame(self.window, borderwidth=2, relief="solid")
        f12 = tk.Frame(f11)
        f11.pack()
        f12.grid(column=0, row=1)

        # Video Feed
        self.vid = VideoFeed(video_source)
        self.canvas = tk.Canvas(f11, width=self.vid.width, height=self.vid.height, borderwidth=2, relief="solid")
        self.canvas.grid(column=0, row=0)

        # Take Picture Button
        take_pic_icon_path = "pic.png"
        img = cv2.imread(take_pic_icon_path)
        img = cv2.resize(img, (80, 50))
        img = cv2.imwrite(take_pic_icon_path, img)
        img1 = ImageTk.PhotoImage(Image.open(take_pic_icon_path))

        take_pic = tk.Button(f12, image=img1, command=self.take_photo, background="black")
        take_pic["border"] = "0"
        take_pic.grid(column=2, row=0)

        # Filters List
        filter_list = tk.Label(f12, text="Filters", fg="black", font="Times 15 bold")
        filter_list.grid(column=0, row=0)

        self.selected_filter = tk.StringVar()
        filters = ttk.Combobox(f12, textvariable=self.selected_filter, font="Times 14")
        filters['values'] = ("Default", "Black & White", "Inverse")
        filters.grid(column=0, row=2)

        filters.current(0)
        filters['state'] = 'readonly'
        filters.bind('<<ComboboxSelected>>', self.apply_filter)

        # Virtual Background
        global toggle_VBG
        font_UI = "Times 13 bold"
        toggle_VBG = tk.Button(f12, text="Virtual Background: OFF", command=self.VBG, font=font_UI,
                               fg="white", bg="black", height=1)
        toggle_VBG.grid(column=4, row=0)

        # Select VBG
        button_explore = tk.Button(f12, text="Choose background image!", command=self.browseFiles, font=font_UI,
                                   fg="black", bg="white", relief="solid")
        button_explore.grid(column=4, row=2)

        # Select save location
        button_output_path = tk.Button(f12, text="Change save location!", command=self.chooseOutputPath, font=font_UI,
                                       fg="white", bg="black")
        button_output_path.grid(column=2, row=2)

        # Arrange Layout
        temp1 = tk.Label(f12, text="", width=5)
        temp2 = tk.Label(f12, text="", width=5)
        temp3 = tk.Label(f12, text="", width=5)
        temp4 = tk.Label(f12, text="", width=5)

        temp1.grid(column=1, row=0)
        temp2.grid(column=3, row=0)
        temp3.grid(column=0, row=1)
        temp4.grid(column=4, row=1)

        self.delay = 1
        self.update()
        self.window.mainloop()

    def chooseOutputPath(self):
        '''Open file explorer for chosing place to save images'''
        self.output_path = tkinter.filedialog.askdirectory(initialdir=self.output_path,
                                                           title="Choose a folder to save your images")
        return self.save_settings(self.output_path, self.BG_path)

    def browseFiles(self):
        '''Open file explorer for chosing picture for virtual background'''
        self.BG_path = tkinter.filedialog.askopenfilename(initialdir=self.BG_path,
                                                      title="Select a File",
                                                      filetypes=(("Image files",
                                                                  ["*.jpg*", "*.png*"]),
                                                                 ("all files",
                                                                  "*.*")))
        self.imgBG = cv2.imread(self.BG_path)

        self.imgBG = cv2.resize(self.imgBG,
                                (
                                    640,
                                    480
                                ),
                                interpolation=cv2.INTER_LINEAR)
        self.imgBG = cv2.cvtColor(self.imgBG, cv2.COLOR_BGR2RGB)
        return self.save_settings(BG_path=self.BG_path, output_path=None)

    def VBG(self):
        '''Change Virtual Background button state'''
        self.is_segment = 1 - self.is_segment
        if toggle_VBG['text'] == 'Virtual Background: OFF':
            toggle_VBG['text'] = 'Virtual Background: ON'
        else:
            toggle_VBG['text'] = 'Virtual Background: OFF'

    def apply_filter(self, *args):
        '''Get filter from dropdown'''
        self.feed_state = self.selected_filter.get()

    def update(self):
        '''Update the video feed'''
        ret, frame = self.vid.get_frame()
        if ret:
            frame = self.set_feed_state(curr_frame=frame)
            if self.is_segment != 0:
                frame = self.segmentor.removeBG(frame, self.imgBG, threshold=.4)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.curr_state = frame
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def take_photo(self):
        """ Take photo and save it to the file """
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.join(self.output_path, filename)
        self.photo = PIL.Image.fromarray(self.curr_state)
        self.photo.save(p, "JPEG")
        self.send_noti(filename)

    def send_noti(self, filename):
        '''Send system notification'''
        notification = Notify()

        notification.title = "PhotoBooth"
        notification.message = f"{filename} saved successfully"
        notification.send()

    def set_feed_state(self, curr_frame):
        '''Set filter for video feed'''
        if self.feed_state == "Black & White":
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        if self.feed_state == "Inverse":
            curr_frame == cv2.bitwise_not(curr_frame)
        else:
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2RGB)
        return curr_frame
    
    def save_settings(self, output_path, BG_path):
        if output_path != None:
            self.settings["output_path"] = output_path
        if BG_path != None:
            self.settings["BG_path"] = os.path.dirname(BG_path)
        with open("config.json", "w") as f:
            json.dump(self.settings, f, indent=4)


if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    App(tk.Tk(), "Photo Booth", 0, output_path=config["output_path"], BG_path=config["BG_path"])
    

