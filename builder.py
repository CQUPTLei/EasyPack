# -*- coding = utf-8 -*-
# @TIME : 2025/10/08 21:12
# @Author : Grace
# @File : builder.py
# @Software : PyCharm Professional 2025.1.2
# Introduction： 后台构建工作模块，在独立线程中执行PyInstaller命令以防UI冻结。

import os
import re
import shlex
import subprocess
import sys
from PyQt6.QtCore import QObject, pyqtSignal


class BuildWorker(QObject):
    """
    处理PyInstaller构建过程的所有后端逻辑。
    在单独的线程中运行，以保持UI响应。
    """
    # 发送实时输出到UI的信号
    progress_updated = pyqtSignal(str)
    # 报告完成状态（返回码）的信号
    finished = pyqtSignal(int)

    def __init__(self, command, python_executable):
        super().__init__()
        self.command = command
        self.python_executable = python_executable
        self.is_cancelled = False  # 用于标记用户是否取消了构建

    def run(self):
        """在线程中执行的主方法"""
        try:
            self.progress_updated.emit(f"执行命令:\n{self.command}\n\n")
            command_list = shlex.split(self.command)

            # 在Windows上运行时隐藏子进程的控制台窗口
            creation_flags = 0
            if sys.platform == 'win32':
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True,
                creationflags=creation_flags
            )

            # 实时读取和报告输出
            for line in iter(process.stdout.readline, ''):
                if self.is_cancelled:
                    process.terminate()  # 终止进程
                    self.progress_updated.emit("\n--- 用户已取消构建 ---\n")
                    break
                self.progress_updated.emit(line)

            process.wait()  # 等待进程完成
            self.finished.emit(process.returncode)  # 发送完成信号和返回码

        except FileNotFoundError:
            self.progress_updated.emit(f"错误: 命令未找到。 '{self.python_executable}' 是一个有效的Python解释器吗?\n")
            self.finished.emit(-1)
        except Exception as e:
            self.progress_updated.emit(f"\n--- 发生意外错误: ---\n{str(e)}\n")
            self.finished.emit(-1)

    def cancel(self):
        """向工作线程发送取消信号"""
        self.is_cancelled = True


def get_conda_envs():
    """获取系统中所有Conda环境的字典 {名称: 路径}"""
    envs = {}
    try:
        creation_flags = 0
        if sys.platform == 'win32':
            creation_flags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            ["conda", "env", "list"],
            capture_output=True, text=True, check=True, encoding='utf-8',
            creationflags=creation_flags
        )
        # 正则表达式用于匹配环境名称和路径
        env_pattern = re.compile(r"^(\S+)\s+\*?\s+(.+)$")
        for line in proc.stdout.splitlines():
            if not line.startswith('#') and line.strip():
                match = env_pattern.match(line)
                if match:
                    name, path = match.groups()
                    envs[name.strip()] = os.path.normpath(path.strip())
        return envs
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果conda命令失败，返回空字典
        return {}