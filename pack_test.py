# -*- coding = utf-8 -*-
# @TIME : 2025/10/08 21:12
# @Author : Grace
# @File : main.py
# @Software : PyCharm Professional 2025.1.2
# Introduction： 打包测试

import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QLineEdit, QLabel
from PyQt6.QtGui import QColor


class FancyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("打包测试程序")
        self.setGeometry(100, 100, 500, 400)

        # 输入框
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("输入内容并点击添加")
        self.input_box.setGeometry(50, 50, 300, 40)

        # 添加按钮
        self.add_button = QPushButton("添加到列表", self)
        self.add_button.setGeometry(370, 50, 100, 40)
        self.add_button.clicked.connect(self.add_item)

        # 列表
        self.list_widget = QListWidget(self)
        self.list_widget.setGeometry(50, 120, 420, 200)

        # 随机颜色按钮
        self.color_button = QPushButton("随机改变列表颜色", self)
        self.color_button.setGeometry(150, 330, 200, 40)
        self.color_button.clicked.connect(self.change_colors)

        # 提示标签
        self.label = QLabel("PyQt6炫酷示例", self)
        self.label.setGeometry(180, 10, 200, 30)

    def add_item(self):
        text = self.input_box.text()
        if text:
            self.list_widget.addItem(text)
            self.input_box.clear()

    def change_colors(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            item.setBackground(QColor(r, g, b))
            item.setForeground(QColor(255 - r, 255 - g, 255 - b))  # 字体颜色对比


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FancyWindow()
    window.show()
    sys.exit(app.exec())
