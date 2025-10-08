# -*- coding = utf-8 -*-
# @TIME : 2025/10/08 21:12
# @Author : Grace
# @File : ui_components.py
# @Software : PyCharm Professional 2025.1.2
# Introduction： PyQt6的GUI界面定义模块，负责所有UI控件的创建、布局和样式。

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QRadioButton,
    QPlainTextEdit, QFileDialog, QTableWidget, QAbstractItemView, QHeaderView,
    QMessageBox, QFormLayout, QTableWidgetItem, QSplitter
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
import sys


def resource_path(relative_path):
    """ 获取资源的绝对路径，无论是开发环境还是打包后的环境 """
    try:
        # PyInstaller 创建一个临时文件夹，并把路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包状态，就使用常规的路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# --- 主题样式表 ---
LIGHT_THEME = """
    QWidget {
        background-color: #f0f0f0; color: #000000; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt;
    }
    QMainWindow { border: 1px solid #c0c0c0; }
    QGroupBox { border: 1px solid #c0c0c0; border-radius: 5px; margin-top: 1ex; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; background-color: #f0f0f0; }
    QLineEdit, QComboBox, QPlainTextEdit, QTableWidget { background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 3px; padding: 4px; color: #000000; }
    QLineEdit:focus, QComboBox:focus { border-color: #0078d7; }
    QPushButton { background-color: #0078d7; color: white; border: none; padding: 5px 15px; border-radius: 3px; }
    QPushButton:hover { background-color: #108ee9; }
    QPushButton:pressed { background-color: #006ac1; }
    QPushButton:disabled { background-color: #d3d3d3; color: #808080; }
    QPlainTextEdit { font-family: 'Consolas', 'Courier New', monospace; }
    QHeaderView::section { background-color: #e8e8e8; padding: 4px; border: 1px solid #c0c0c0; }
"""

DARK_THEME = """
    QWidget { background-color: #2e2e2e; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
    QGroupBox { border: 1px solid #444; border-radius: 5px; margin-top: 1ex; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; }
    QLineEdit, QComboBox, QPlainTextEdit, QTableWidget { background-color: #3c3c3c; border: 1px solid #555; border-radius: 3px; padding: 4px; color: #e0e0e0; }
    QLineEdit:focus, QComboBox:focus { border-color: #0078d7; }
    QPushButton { background-color: #0078d7; color: white; border: none; padding: 5px 15px; border-radius: 3px; }
    QPushButton:hover { background-color: #108ee9; }
    QPushButton:pressed { background-color: #006ac1; }
    QPushButton:disabled { background-color: #404040; color: #888; }
    QPlainTextEdit { font-family: 'Consolas', 'Courier New', monospace; background-color: #252525; }
    QHeaderView::section { background-color: #3c3c3c; padding: 4px; border: 1px solid #555; }
"""


class PyInstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyInstaller GUI Pro")
        self.setMinimumSize(1200, 750)
        # self.setWindowIcon(QIcon(self.style().standardIcon(
        #     self.style().StandardPixmap.SP_CommandLink
        # )))
        # self.setWindowIcon(QIcon("resources/icon.ico"))
        app_icon_path = resource_path("resources/icon.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        else:
            # 如果找不到自定义图标，就使用系统默认图标作为备用
            self.setWindowIcon(QIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_CommandLink
            )))

        self.python_executable = None
        self.output_path = None

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(self.splitter)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([500, 700])

        self.update_command_preview()

    def _create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        appearance_group = QGroupBox("外观")
        appearance_layout = QHBoxLayout()
        self.dark_mode_check = QCheckBox("黑暗模式")
        appearance_layout.addWidget(self.dark_mode_check)
        appearance_group.setLayout(appearance_layout)

        main_settings_group = QGroupBox("主要设置")
        main_settings_layout = QFormLayout()
        self.script_path_edit = QLineEdit()
        browse_script_btn = QPushButton("浏览...")
        browse_script_btn.clicked.connect(self.browse_script)
        script_container = self._create_line_edit_with_button(self.script_path_edit, browse_script_btn)
        main_settings_layout.addRow("Python 脚本:", script_container)
        self.conda_env_combo = QComboBox()
        main_settings_layout.addRow("Conda 环境:", self.conda_env_combo)
        main_settings_group.setLayout(main_settings_layout)

        general_group = QGroupBox("常规选项")
        general_layout = QFormLayout()
        self.app_name_edit = QLineEdit()
        general_layout.addRow("程序名称 (--name):", self.app_name_edit)
        self.icon_path_edit = QLineEdit()
        browse_icon_btn = QPushButton("浏览...")
        browse_icon_btn.clicked.connect(self.browse_icon)
        icon_container = self._create_line_edit_with_button(self.icon_path_edit, browse_icon_btn)
        general_layout.addRow("图标 (--icon):", icon_container)
        self.noconsole_check = QCheckBox("隐藏控制台窗口 (--noconsole)")
        self.noconsole_check.setChecked(True)
        self.clean_check = QCheckBox("构建前清理 (--clean)")
        self.clean_check.setChecked(True)
        general_layout.addRow(self.noconsole_check)
        general_layout.addRow(self.clean_check)
        general_group.setLayout(general_layout)

        mode_group = QGroupBox("打包模式")
        self.onefile_radio = QRadioButton("单文件 (-F)")
        self.onedir_radio = QRadioButton("单目录 (-D)")
        self.onefile_radio.setChecked(True)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.onefile_radio)
        mode_layout.addWidget(self.onedir_radio)
        mode_group.setLayout(mode_layout)

        advanced_group = QGroupBox("高级打包选项")
        advanced_layout = QFormLayout()
        self.hidden_imports_edit = QLineEdit()
        self.hidden_imports_edit.setPlaceholderText("例如: my_package, another_module.sub")
        advanced_layout.addRow("隐藏导入:", self.hidden_imports_edit)
        self.paths_edit = QLineEdit()
        self.paths_edit.setPlaceholderText("从Conda环境自动检测")
        advanced_layout.addRow("模块路径:", self.paths_edit)
        self.data_table = self._create_table(["源文件/目录", "在程序中的相对路径"])
        data_buttons = self._create_table_buttons(self.data_table)
        advanced_layout.addRow("附加数据:", self.data_table)
        advanced_layout.addRow(data_buttons)
        advanced_group.setLayout(advanced_layout)

        layout.addWidget(appearance_group)
        layout.addWidget(main_settings_group)
        layout.addWidget(general_group)
        layout.addWidget(mode_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        return panel

    def _create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        cmd_group = QGroupBox("最终命令预览")
        cmd_layout = QVBoxLayout()
        self.command_preview_label = QLabel("...")
        self.command_preview_label.setFont(QFont("Courier New", 10))
        self.command_preview_label.setWordWrap(True)
        self.command_preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cmd_layout.addWidget(self.command_preview_label)
        cmd_group.setLayout(cmd_layout)

        output_group = QGroupBox("构建日志")
        output_layout = QVBoxLayout()
        self.output_console = QPlainTextEdit()
        self.output_console.setReadOnly(True)
        output_layout.addWidget(self.output_console)
        output_group.setLayout(output_layout)

        button_layout = QHBoxLayout()
        self.build_button = QPushButton("开始构建")
        self.build_button.setFixedHeight(35)
        self.cancel_button = QPushButton("取消构建")
        self.cancel_button.setFixedHeight(35)
        self.cancel_button.setEnabled(False)
        self.open_output_dir_button = QPushButton("打开输出目录")
        self.open_output_dir_button.setFixedHeight(35)
        self.open_output_dir_button.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.build_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.open_output_dir_button)

        layout.addWidget(cmd_group)
        layout.addWidget(output_group)
        layout.addLayout(button_layout)
        return panel

    def _create_line_edit_with_button(self, line_edit, button):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return container

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setMinimumHeight(150)
        return table

    def _create_table_buttons(self, table):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        add_file_btn = QPushButton("添加文件")
        add_dir_btn = QPushButton("添加目录")
        remove_btn = QPushButton("移除选中")
        add_file_btn.clicked.connect(lambda: self.add_table_row(table, 'file'))
        add_dir_btn.clicked.connect(lambda: self.add_table_row(table, 'dir'))
        remove_btn.clicked.connect(lambda: self.remove_table_row(table))
        layout.addStretch()
        layout.addWidget(add_file_btn)
        layout.addWidget(add_dir_btn)
        layout.addWidget(remove_btn)
        return container

    def apply_theme(self, is_dark):
        self.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)

    def browse_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择Python脚本", "", "Python Files (*.py *.pyw)")
        if path:
            self.script_path_edit.setText(path)
            if not self.app_name_edit.text():
                app_name = os.path.splitext(os.path.basename(path))[0]
                self.app_name_edit.setText(app_name)

    def browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图标", "", "Icon Files (*.ico)")
        if path:
            self.icon_path_edit.setText(path)

    def add_table_row(self, table, mode='file'):
        if mode == 'file':
            source_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件")
        else:
            source_path = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if source_path:
            dest_path = os.path.basename(source_path)
            row_count = table.rowCount()
            table.insertRow(row_count)
            table.setItem(row_count, 0, QTableWidgetItem(source_path))
            table.setItem(row_count, 1, QTableWidgetItem(dest_path))

    def remove_table_row(self, table):
        selected_rows = table.selectionModel().selectedRows()
        for row in sorted([r.row() for r in selected_rows], reverse=True):
            table.removeRow(row)

    def populate_conda_envs(self, envs):
        self.conda_env_combo.addItems([""] + list(envs.keys()))

    def update_paths_from_env(self, env_path):
        self.python_executable = os.path.join(env_path, "python.exe")
        site_packages = os.path.join(env_path, "Lib", "site-packages")
        self.paths_edit.setText(site_packages if os.path.isdir(site_packages) else "")

    def log_to_console(self, text, color=None):
        if color:
            html_text = f'<font color="{color}">{text.strip()}</font>'
            self.output_console.appendHtml(html_text)
        else:
            self.output_console.appendPlainText(text.strip())
        self.output_console.verticalScrollBar().setValue(self.output_console.verticalScrollBar().maximum())

    def show_message(self, title, text, level="info"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        icon_map = {
            "info": QMessageBox.Icon.Information, "error": QMessageBox.Icon.Critical,
            "warning": QMessageBox.Icon.Warning, "question": QMessageBox.Icon.Question
        }
        msg_box.setIcon(icon_map.get(level, QMessageBox.Icon.NoIcon))
        if level == "question":
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            return msg_box.exec()
        msg_box.exec()

    def set_build_state(self, is_building):
        self.build_button.setEnabled(not is_building)
        self.cancel_button.setEnabled(is_building)
        self.splitter.widget(0).setEnabled(not is_building)
        if is_building:
            self.open_output_dir_button.setEnabled(False)

    def get_pyinstaller_command(self):
        # --- FIX START ---
        # 确保所有return语句都返回两个值
        if not self.python_executable or not os.path.exists(self.python_executable):
            return None, "无效的Python解释器。请选择一个有效的Conda环境。"

        script = self.script_path_edit.text()
        if not script:
            return None, "未选择主Python脚本。"
        # --- FIX END ---

        base_output_dir = os.path.join(os.path.dirname(script), "output")
        dist_path = os.path.join(base_output_dir, "dist")
        build_path = os.path.join(base_output_dir, "build")
        spec_path = base_output_dir

        self.output_path = dist_path

        command = [f'"{self.python_executable}"', "-m", "PyInstaller", f'"{script}"']

        command.extend([
            f'--distpath="{dist_path}"',
            f'--workpath="{build_path}"',
            f'--specpath="{spec_path}"'
        ])

        command.append("-F" if self.onefile_radio.isChecked() else "-D")
        if self.app_name_edit.text():
            command.extend(["--name", f'"{self.app_name_edit.text()}"'])
        if self.noconsole_check.isChecked():
            command.append("--noconsole")
        if self.clean_check.isChecked():
            command.append("--clean")
        if self.icon_path_edit.text():
            command.extend(["--icon", f'"{self.icon_path_edit.text()}"'])
        if self.paths_edit.text():
            command.extend(["--paths", f'"{self.paths_edit.text()}"'])
        for row in range(self.data_table.rowCount()):
            source = self.data_table.item(row, 0).text()
            dest = self.data_table.item(row, 1).text()
            command.extend(["--add-data", f'"{source}{os.pathsep}{dest}"'])
        if self.hidden_imports_edit.text():
            imports = [i.strip() for i in self.hidden_imports_edit.text().split(',') if i.strip()]
            for imp in imports:
                command.extend(["--hidden-import", imp])

        return " ".join(command), None

    def update_command_preview(self):
        command, error = self.get_pyinstaller_command()
        self.command_preview_label.setText(f"<错误: {error}>" if error else command)
