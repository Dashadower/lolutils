import sys
from cx_Freeze import setup, Executable
build_exe_options = {"packages":["dbm"]}
setup(
    name = "LolUtils",
    version = "1.0",
    options = {"build_exe":build_exe_options},
    description = "LolUtils",
    executables = [Executable("LolUtils.py", base = "Win32GUI")])