# -*- coding = utf-8 -*-
# @TIME : 2025/10/08 21:12
# @Author : Grace
# @File : fix.py
# @Software : PyCharm Professional 2025.1.2
# Introduction： 最初使用tkinter实现的简单打包程序
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import threading
import shlex
import re


class PyInstallerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("PyInstaller GUI Packer")

        # Store conda environments: {name: path}
        self.conda_envs = {}

        self.setup_widgets()
        self.load_conda_envs()
        self.update_command()

    def setup_widgets(self):
        # Frame for options
        options_frame = ttk.LabelFrame(self.master, text="Configuration")
        options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # 1. Python Script Selection
        ttk.Label(options_frame, text="Python Script:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_file = ttk.Entry(options_frame, width=60)
        self.entry_file.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)
        self.entry_file.bind("<KeyRelease>", self.update_command)
        ttk.Button(options_frame, text="Browse...", command=self.select_file).grid(row=0, column=3, padx=5)

        # 2. Conda Environment Selection
        ttk.Label(options_frame, text="Conda Environment:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo_env = ttk.Combobox(options_frame, state="readonly", width=57)
        self.combo_env.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
        self.combo_env.bind("<<ComboboxSelected>>", self.on_env_select)

        # 3. Packaging Mode (-F or -D)
        self.var_mode = tk.StringVar(value="-F")
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="One File (-F)", variable=self.var_mode, value="-F",
                        command=self.update_command).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="One Directory (-D)", variable=self.var_mode, value="-D",
                        command=self.update_command).pack(side="left", padx=5)

        # 4. Paths for modules
        ttk.Label(options_frame, text="Module Paths (--paths):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_paths = ttk.Entry(options_frame, width=60)
        self.entry_paths.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)
        self.entry_paths.bind("<KeyRelease>", self.update_command)
        ttk.Button(options_frame, text="Browse...", command=self.select_paths).grid(row=3, column=3, padx=5)

        # 5. Python executable (auto-filled)
        ttk.Label(options_frame, text="Python Executable:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_python_exe = ttk.Entry(options_frame, width=60, state="readonly")
        self.entry_python_exe.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5)

        # 6. Console Window
        self.var_console = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Show Console Window (--console)", variable=self.var_console,
                        command=self.update_command).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # 7. Icon
        ttk.Label(options_frame, text="Icon (--icon):").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.entry_icon = ttk.Entry(options_frame, width=60)
        self.entry_icon.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5)
        self.entry_icon.bind("<KeyRelease>", self.update_command)
        ttk.Button(options_frame, text="Browse...", command=self.select_icon).grid(row=6, column=3, padx=5)

        # 8. Other Options
        ttk.Label(options_frame, text="Other Options:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.entry_custom = ttk.Entry(options_frame, width=60)
        self.entry_custom.grid(row=7, column=1, columnspan=2, sticky="ew", padx=5)
        self.entry_custom.bind("<KeyRelease>", self.update_command)

        # Command display
        command_frame = ttk.LabelFrame(self.master, text="Final Command")
        command_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.label_command = ttk.Label(command_frame, text="", wraplength=700, justify=tk.LEFT, font=("Courier", 9))
        self.label_command.pack(padx=10, pady=5, fill="x")

        # Build button
        self.build_button = ttk.Button(self.master, text="Build", command=self.build_command)
        self.build_button.grid(row=2, column=0, padx=10, pady=10)

        # Output display
        output_frame = ttk.LabelFrame(self.master, text="Build Output")
        output_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.output_text = tk.Text(output_frame, height=15, wrap=tk.WORD, bg="black", fg="white")
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)

        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select Python script to package",
                                               filetypes=[("Python files", "*.py")])
        if file_path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, file_path)
            self.update_command()

    def select_icon(self):
        icon_path = filedialog.askopenfilename(title="Select icon file", filetypes=[("Icon files", "*.ico")])
        if icon_path:
            self.entry_icon.delete(0, tk.END)
            self.entry_icon.insert(0, icon_path)
            self.update_command()

    def select_paths(self):
        paths = filedialog.askdirectory(title="Select paths for Python modules")
        if paths:
            self.entry_paths.delete(0, tk.END)
            self.entry_paths.insert(0, paths)
            self.update_command()

    def load_conda_envs(self):
        try:
            # Get Conda environment list
            proc = subprocess.run(["conda", "env", "list"], capture_output=True, text=True, check=True,
                                  encoding='utf-8')
            output = proc.stdout

            # Regex to find lines with env name and path
            # Example: my_env       *  C:\Users\user\.conda\envs\my_env
            env_pattern = re.compile(r"^(\S+)\s+\*?\s+(.+)$")

            for line in output.splitlines():
                if not line.startswith('#') and line.strip():
                    match = env_pattern.match(line)
                    if match:
                        name, path = match.groups()
                        # On Windows, path from conda list might be in a weird format.
                        # Normalizing it.
                        self.conda_envs[name.strip()] = os.path.normpath(path.strip())

            if self.conda_envs:
                self.combo_env['values'] = list(self.conda_envs.keys())
                self.combo_env.current(0)
                self.on_env_select()  # Trigger selection for the default item
            else:
                messagebox.showwarning("Warning", "No Conda environments found.")

        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Error",
                                 "Failed to execute 'conda' command. Is Conda installed and in your system's PATH?")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while fetching Conda environments: {e}")

    def on_env_select(self, event=None):
        env_name = self.combo_env.get()
        if env_name in self.conda_envs:
            env_path = self.conda_envs[env_name]

            # 5. Automatically select python directory
            python_exe_path = os.path.join(env_path, "python.exe")
            if os.path.exists(python_exe_path):
                self.entry_python_exe.config(state="normal")
                self.entry_python_exe.delete(0, tk.END)
                self.entry_python_exe.insert(0, python_exe_path)
                self.entry_python_exe.config(state="readonly")

            # 4. Automatically select paths
            site_packages_path = os.path.join(env_path, "Lib", "site-packages")
            if os.path.isdir(site_packages_path):
                self.entry_paths.delete(0, tk.END)
                self.entry_paths.insert(0, site_packages_path)

            self.update_command()

    def update_command(self, event=None):
        python_exe = self.entry_python_exe.get()
        if not python_exe:
            # Don't construct command if python exe is not determined
            self.label_command.config(text="<Select a valid Conda environment>")
            return

        # Base command is now using the selected python to run pyinstaller module
        command = [f'"{python_exe}"', "-m", "PyInstaller"]

        # Mode (-F/-D)
        command.append(self.var_mode.get())

        # Paths
        paths = self.entry_paths.get()
        if paths:
            command.extend(["--paths", f'"{paths}"'])

        # Console
        if not self.var_console.get():
            command.append("--noconsole")
        else:
            command.append("--console")  # Explicitly add --console for clarity

        # Icon
        icon = self.entry_icon.get()
        if icon:
            command.extend(["--icon", f'"{icon}"'])

        # Custom options
        custom = self.entry_custom.get()
        if custom:
            # Use shlex to correctly split custom arguments
            command.extend(shlex.split(custom))

        # Main script file
        file = self.entry_file.get()
        if file:
            command.append(f'"{file}"')

        # Display the command
        self.label_command.config(text=" ".join(command))

    def check_and_install_pyinstaller(self, python_exe):
        """Checks for PyInstaller in the target environment and asks to install if not found."""
        try:
            # Check if pyinstaller is installed in the selected environment
            subprocess.run([python_exe, "-m", "pip", "show", "pyinstaller"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            # Not found, ask to install
            install = messagebox.askyesno(
                "PyInstaller Not Found",
                f"PyInstaller is not installed in the selected environment ('{os.path.dirname(python_exe)}').\n\nDo you want to install it now?"
            )
            if install:
                self.log_output("PyInstaller not found. Attempting to install...\n")
                try:
                    # Install PyInstaller using the selected python's pip
                    process = subprocess.Popen(
                        [python_exe, "-m", "pip", "install", "pyinstaller"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    # Stream the installation output
                    for line in iter(process.stdout.readline, ''):
                        self.log_output(line)

                    process.wait()
                    if process.returncode == 0:
                        self.log_output("\nPyInstaller installed successfully.\n")
                        return True
                    else:
                        self.log_output("\nFailed to install PyInstaller.\n")
                        return False
                except Exception as e:
                    messagebox.showerror("Installation Failed", f"Failed to install PyInstaller: {e}")
                    return False
            else:
                return False

    def log_output(self, message):
        """Appends a message to the output text widget in a thread-safe way."""
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()

    def build_command(self):
        command_str = self.label_command.cget("text")
        python_exe = self.entry_python_exe.get()

        if not self.entry_file.get() or not python_exe:
            messagebox.showerror("Error", "Python Script and a valid Conda Environment are required.")
            return

        # Disable button to prevent multiple clicks
        self.build_button.config(state="disabled")

        # Clear previous output
        self.output_text.delete(1.0, tk.END)

        def run_build():
            try:
                # 1. Check for PyInstaller in the target env
                if not self.check_and_install_pyinstaller(python_exe):
                    self.log_output("\nBuild aborted: PyInstaller is not available in the target environment.\n")
                    return

                self.log_output(f"Starting build with command:\n{command_str}\n\n")

                # Use shlex.split for robust command parsing, especially with quotes
                command_list = shlex.split(command_str)

                # 2. Run the build command
                process = subprocess.Popen(
                    command_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'  # Handle potential encoding errors
                )

                # 3. Read and display output in real-time
                for line in iter(process.stdout.readline, ''):
                    self.log_output(line)

                process.wait()  # Wait for the process to complete

                # 4. Show final status
                if process.returncode == 0:
                    self.log_output("\n--- Build completed successfully! ---\n")
                    messagebox.showinfo("Success", "Build completed successfully!")
                else:
                    self.log_output(f"\n--- Build failed with exit code {process.returncode}. ---\n")
                    messagebox.showerror("Error", "Build failed. Check the output for details.")

            except Exception as e:
                self.log_output(f"\n--- An error occurred during the build process: ---\n{str(e)}\n")
                messagebox.showerror("Error", f"Build failed with an exception: {str(e)}")
            finally:
                # Re-enable the build button on the main thread
                self.master.after(0, lambda: self.build_button.config(state="normal"))

        # Run the build process in a separate thread to keep the GUI responsive
        threading.Thread(target=run_build, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()
