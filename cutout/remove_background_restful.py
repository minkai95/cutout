from flask import Flask, request, send_file
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


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


@app.route('/process_image', methods=['POST'])
def process_image():
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']

    # 如果用户没有选择文件，浏览器也可能会提交一个空的文件部分，所以需要检查
    if file.filename == '':
        return 'No selected file', 400

    # 保存上传的文件
    filename = secure_filename(file.filename)
    file.save(filename)

    # 处理图片并保存结果
    output_filename = "output_" + os.path.splitext(filename)[0] + ".png"
    remove_background(filename, output_filename)

    # 返回处理后的图片
    return send_file(output_filename, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
