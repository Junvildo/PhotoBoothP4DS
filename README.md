# PhotoBoothP4DS

## Lưu ý
Tránh code trên branch `main`, làm việc trên branch thể hiện nhiệm vụ của mình

vd: `FrontEnd_TenNguoiCode`

Khi commit nhớ ghi rõ nội dung

## Công việc bao gồm:
* Viết code các hàm xử lý ảnh, thực hiện chức năng nền ảo, load file, nói chung là backend.
* Viết code để tạo cửa sổ cho chương trình, frontend.
* Viết báo cáo, thuyết trình.
## Nếu có thời gian:
* Nhận diện bàn tay, nụ cười để đếm ngược chụp ảnh, (tương tự như smile shutter của các ứng dụng chụp ảnh).
* Thiết kế frontend đẹp hơn.

## Các chức năng backend cần làm:
### Người chịu trách nhiệm: 
#### Quan trọng
- [x] Khởi chạy chương trình.
- [x] Lấy dữ liệu từ webcam.
- [x] Chụp ảnh.
- [ ] Virtual Background.
- [ ] Thay đổi đường dẫn thư mục lưu ảnh/ video được ghi lại.
- [x] Đặt tên cho ảnh, video đã ghi.
#### Nếu có thời gian
- [ ] Áp dụng các bộ lọc màu cho ảnh.
- [ ] Thay đổi resolution ảnh, video.
### Các chức năng frontend cần làm: 
### Người chịu trách nhiệm: 
#### Dựa theo frontend của photo booth (cần thiết)
- [ ] Button chụp ảnh, video.
- [ ] Button chuyển giữa 2 chế độ chụp và quay video.
- [ ] Button hiện các lựa chọn virtual background.
- [ ] Subwindow hiện lịch sử các ảnh đã chụp
- [ ] Cửa sổ setting cho phép sửa đường dẫn thư mục lưu ảnh, video
#### Nếu có thêm thời gian
- [ ] Cửa sổ preview filter.
- [ ] Các tùy chọn smile shutter, countdown, resolution.
- [ ] Tùy biến các button đẹp hơn
### Thuyết trình, báo cáo:
#### Người chịu trách nhiệm: 







## Hình dung sơ qua về frontend của Photo Booth
https://youtu.be/aGDFryrgSqc

## Code ví dụ cho chương trình
```python
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os
 
class Application:
    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera
 
        self.root = tk.Tk()  # initialize root window
        self.root.title("PyImageSearch PhotoBooth")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
 
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
 
        # create a button, that when pressed, will take the current frame and save it to file
        btn = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
 
        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()
 
    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)  # call the same function after 30 milliseconds
 
    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now() # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        p = os.path.join(self.output_path, filename)  # construct output path
        self.current_image.save(p, "PNG")  # save image as png file
        print("[INFO] saved {}".format(filename))
 
    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())
 
# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()
```
