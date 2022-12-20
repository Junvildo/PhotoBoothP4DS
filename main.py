import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk
import datetime
import os

from PIL import ImageTk, Image
from notifypy import Notify
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation


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
    def __init__(self, window, window_title, video_source=0, output_path="./"):
        # App Variables
        self.window = window
        self.window.title(window_title)

        self.segmentor = SelfiSegmentation()
        self.is_segment = 0
        self.wallpaper_list = ["Capybara-4K.jpg", "flower.jpg", "wall1.jpg"]
        self.imgBG = cv2.imread("./wallpapers/" + self.wallpaper_list[0])

        self.feed_state = "Default"

        self.video_source = video_source

        self.imgBG = cv2.resize(self.imgBG,
                                (
                                    640,
                                    480
                                ),
                                interpolation=cv2.INTER_LINEAR)
        self.imgBG = cv2.cvtColor(self.imgBG, cv2.COLOR_BGR2RGB)

        self.output_path = output_path

        # App Layout and Elements
        f11 = tk.Frame(self.window)
        f12 = tk.Frame(self.window)

        # Video Feed
        self.vid = VideoFeed(video_source)
        self.canvas = tk.Canvas(f11, width=self.vid.width, height=self.vid.height, bg="black")
        self.canvas.grid(column=0, row=0)

        # Take Picture Button
        img = cv2.imread("pic.png")
        img = cv2.resize(img, (70, 40))
        img = cv2.imwrite("pic.png", img)
        img1 = ImageTk.PhotoImage(Image.open("pic.png"))

        take_pic = tk.Button(f12, image=img1, command=self.take_photo, background="black")
        take_pic.grid(column=2, row=0)

        # Filters List
        filter_list = tk.Label(f12, text="Filters", fg="black", font="Times 13 bold")
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
        toggle_VBG = tk.Button(f12, text="Toggle Virtual Background: OFF", command=self.VBG, font="Times 13",
                               fg="white", bg="black", height=1)
        toggle_VBG.grid(column=4, row=0)

        self.selected_VBG = tk.StringVar()
        VBG = ttk.Combobox(f12, textvariable=self.selected_VBG, font="Times 14")
        VBG['values'] = self.wallpaper_list[:]
        VBG.grid(column=4, row=2)

        VBG.current(0)
        VBG['state'] = 'readonly'
        VBG.bind('<<ComboboxSelected>>', self.apply_VBG)

        # Arrange Layout
        temp1 = tk.Label(f12, text="", width=5)
        temp2 = tk.Label(f12, text="", width=5)
        temp3 = tk.Label(f12, text="", width=5)
        temp4 = tk.Label(f12, text="", width=5)

        temp1.grid(column=1, row=0)
        temp2.grid(column=3, row=0)
        temp3.grid(column=0, row=1)
        temp4.grid(column=4, row=1)

        f11.pack()
        f12.pack()

        self.delay = 1
        self.update()

        self.window.mainloop()

    def VBG(self):

        self.is_segment = 1 - self.is_segment
        if toggle_VBG['text'] == 'Toggle Virtual Background: OFF':
            toggle_VBG['text'] = 'Toggle Virtual Background: ON'
        else:
            toggle_VBG['text'] = 'Toggle Virtual Background: OFF'

    def apply_VBG(self, *args):
        self.imgBG = cv2.imread("./wallpapers/" + self.selected_VBG.get())

        self.imgBG = cv2.resize(self.imgBG,
                                (
                                    640,
                                    480
                                ),
                                interpolation=cv2.INTER_LINEAR)
        self.imgBG = cv2.cvtColor(self.imgBG, cv2.COLOR_BGR2RGB)

    def apply_filter(self, *args):
        self.feed_state = self.selected_filter.get()

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            frame = self.set_feed_state(curr_frame=frame)
            if self.is_segment != 0:
                frame = self.segmentor.removeBG(frame, self.imgBG, threshold=.5)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def take_photo(self):
        """ Take photo and save it to the file """
        ret, frame = self.vid.get_frame()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.join(self.output_path, filename)
        if ret:
            self.photo = PIL.Image.fromarray(frame)
            self.photo.save(p, "JPEG")
            self.send_noti(filename)

    def send_noti(self, filename):
        notification = Notify()

        notification.title = "PhotoBooth"
        notification.message = f"{filename} saved successfully"
        notification.send()

    def set_feed_state(self, curr_frame):
        if self.feed_state == "Black & White":
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        if self.feed_state == "Inverse":
            curr_frame == cv2.bitwise_not(curr_frame)
        else:
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2RGB)
        return curr_frame


if __name__ == "__main__":
    App(tk.Tk(), "Photo Booth", 0)
