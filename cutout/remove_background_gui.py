import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import os
import time

def remove_background(input_image_path, output_image_path):
    # 读取输入图片，并确保图像类型是 CV_8UC3
    img = cv2.imread(input_image_path, cv2.IMREAD_COLOR)

    # 使用 GrabCut 算法分割前景和背景
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (50, 50, img.shape[1] - 50, img.shape[0] - 50)  # 初始矩形区域
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    # 创建一个掩码，将不确定的区域设置为背景
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # 将掩码应用到原始图像上
    img_cutout = img * mask2[:, :, np.newaxis]

    # 创建一个 alpha 通道，将掩码应用到 alpha 通道上
    alpha = mask2 * 255

    # 将 alpha 通道添加到图像中
    b, g, r = cv2.split(img_cutout)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)

    # 保存结果为 PNG 图片
    cv2.imwrite(output_image_path, dst)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Remove Background')
        self.root.geometry('600x600')  # Set the size of the window

        self.canvas = tk.Canvas(root, width=500, height=400)
        self.canvas.pack()

        self.upload_button = tk.Button(root, text='Upload Image', command=self.upload_image)
        self.upload_button.pack()

        # Initially, the download button is not shown.
        self.download_button = tk.Button(root, text='Download Image', command=self.download_image)
        self.download_button.pack()
        self.download_button.pack_forget()

        # Label to show the status of the processing
        self.status_label = tk.Label(root, text='')
        self.status_label.pack()

    def upload_image(self):
        self.input_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])  # Only allow image file types
        if not self.input_image_path:
            return

        # Clear the canvas and hide the download button
        self.canvas.delete('all')
        self.download_button.pack_forget()

        self.process_image()

    def process_image(self):
        self.status_label.config(text='Processing...')
        self.root.update()

        # Use threading to avoid blocking the GUI
        def task():
            remove_background(self.input_image_path, "temp.png")
            self.root.after(0, self.display_image, "temp.png")

        threading.Thread(target=task).start()

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((350, 350))
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(20, 20, anchor='nw', image=self.tk_image)
        self.status_label.config(text='')
        self.download_button.pack()

    def download_image(self):
        # Get the base name of the input image path
        base_name = os.path.basename(self.input_image_path)
        # Remove the extension
        base_name = os.path.splitext(base_name)[0]
        # Append the timestamp
        default_name = base_name + '_' + str(int(time.time()))

        output_image_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_name)
        if not output_image_path:
            return

        remove_background(self.input_image_path, output_image_path)
        messagebox.showinfo("Success", "Image saved successfully")

root = tk.Tk()
app = App(root)
root.mainloop()
