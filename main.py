# -*- coding = utf-8 -*-
# @TIME : 2025/10/08 21:12
# @Author : Grace
# @File : main.py
# @Software : PyCharm Professional 2025.1.2
# Introduction： 程序主入口，负责创建应用、连接UI和后台逻辑。

import sys
import subprocess
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QLineEdit, QCheckBox, QRadioButton, QComboBox
from PyQt6.QtCore import QThread

from ui_components import PyInstallerGUI
from builder import BuildWorker, get_conda_envs


class MainAppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = PyInstallerGUI()
        # 默认启动时使用亮色主题
        self.view.apply_theme(is_dark=False)

        self.conda_envs = {}
        self.build_thread = None
        self.build_worker = None

        self._connect_signals()
        self._load_initial_data()

    def run(self):
        """启动并显示GUI"""
        self.view.show()
        sys.exit(self.app.exec())

    def _connect_signals(self):
        """连接所有UI控件的信号到对应的处理函数(槽)"""
        # 连接特定操作的信号
        self.view.conda_env_combo.currentIndexChanged.connect(self.on_env_changed)
        self.view.build_button.clicked.connect(self.start_build)
        self.view.cancel_button.clicked.connect(self.cancel_build)
        self.view.dark_mode_check.toggled.connect(self.view.apply_theme)
        self.view.open_output_dir_button.clicked.connect(self.open_output_directory)

        # 连接所有输入控件，使其在内容变化时能实时更新命令预览
        widgets_to_connect = self.view.findChildren(
            (QLineEdit, QCheckBox, QRadioButton, QComboBox)
        )
        for widget in widgets_to_connect:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._safe_update_command_preview)
            elif isinstance(widget, (QCheckBox, QRadioButton)):
                widget.toggled.connect(self._safe_update_command_preview)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._safe_update_command_preview)

        # 连接表格数据变化的信号 - 使用安全的更新方法
        self.view.data_table.model().rowsInserted.connect(self._safe_update_command_preview)
        self.view.data_table.model().rowsRemoved.connect(self._safe_update_command_preview)

    def _safe_update_command_preview(self):
        """安全地更新命令预览，捕获可能的异常"""
        try:
            self.view.update_command_preview()
        except Exception as e:
            # 静默处理异常，避免程序崩溃
            print(f"更新命令预览时出错: {e}")

    def _load_initial_data(self):
        """加载初始数据，例如获取Conda环境列表"""
        self.conda_envs = get_conda_envs()
        if not self.conda_envs:
            self.view.show_message("警告", "未能找到任何Conda环境。", "warning")
        else:
            self.view.populate_conda_envs(self.conda_envs)

    def on_env_changed(self, index):
        """当Conda环境下拉框选项改变时被调用"""
        env_name = self.view.conda_env_combo.itemText(index)
        if env_name in self.conda_envs:
            self.view.update_paths_from_env(self.conda_envs[env_name])
        else:  # 处理空选项
            self.view.python_executable = None
            self.view.paths_edit.clear()

    def start_build(self):
        """开始构建过程"""
        command, error = self.view.get_pyinstaller_command()
        if error:
            self.view.show_message("配置错误", error, "error")
            return

        python_exe = self.view.python_executable
        try:
            # 检查目标环境中是否已安装PyInstaller
            subprocess.check_output([python_exe, "-m", "pip", "show", "pyinstaller"], stderr=subprocess.STDOUT,
                                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        except (subprocess.CalledProcessError, FileNotFoundError):
            reply = self.view.show_message(
                "未找到PyInstaller",
                f"在所选环境中未找到PyInstaller。\n\n是否立即安装?",
                level="question"
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.install_pyinstaller(python_exe)
            return

        self.view.output_console.clear()
        self.view.set_build_state(is_building=True)

        # 设置工作线程
        self.build_thread = QThread()
        self.build_worker = BuildWorker(command, python_exe)
        self.build_worker.moveToThread(self.build_thread)

        # 连接工作线程的信号
        self.build_worker.progress_updated.connect(self.view.log_to_console)
        self.build_worker.finished.connect(self.on_build_finished)
        self.build_thread.started.connect(self.build_worker.run)
        self.build_thread.finished.connect(self.build_thread.deleteLater)
        self.build_worker.finished.connect(self.build_thread.quit)

        self.build_thread.start()

    def install_pyinstaller(self, python_exe):
        """在选定的环境中安装PyInstaller"""
        self.view.log_to_console(f"正在尝试安装PyInstaller...")
        self.view.set_build_state(is_building=True)
        self.app.processEvents()  # 强制UI刷新

        try:
            result = subprocess.check_output(
                [python_exe, "-m", "pip", "install", "pyinstaller"],
                stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace'
            )
            self.view.log_to_console(result)
            self.view.log_to_console("\nPyInstaller 安装成功! 现在可以开始构建了。")
        except subprocess.CalledProcessError as e:
            self.view.log_to_console("--- 安装失败 ---\n" + e.output, color='red')
            self.view.show_message("错误", "PyInstaller安装失败。", "error")
        finally:
            self.view.set_build_state(is_building=False)

    def cancel_build(self):
        """取消正在进行的构建"""
        if self.build_worker:
            self.build_worker.cancel()
            self.view.log_to_console("\n正在取消构建...", color='orange')

    def on_build_finished(self, return_code):
        """当构建完成时被调用"""
        if return_code == 0 and not self.build_worker.is_cancelled:
            # 构建成功
            self.view.log_to_console("\n--- 构建成功! ---", color="green")
            # 激活"打开目录"按钮
            self.view.open_output_dir_button.setEnabled(True)
        elif not self.build_worker.is_cancelled:
            # 构建失败
            self.view.log_to_console(f"\n--- 构建失败，退出代码: {return_code}. ---", color="red")
            self.view.show_message("构建失败", "构建过程失败，请检查日志输出获取错误详情。", "error")

        self.view.set_build_state(is_building=False)

    def open_output_directory(self):
        """打开包含最终可执行文件的输出目录"""
        if self.view.output_path and os.path.exists(self.view.output_path):
            if sys.platform == 'win32':
                os.startfile(self.view.output_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.view.output_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.view.output_path])
        else:
            self.view.show_message("错误", "输出目录不存在。", "error")


if __name__ == "__main__":
    controller = MainAppController()
    controller.run()