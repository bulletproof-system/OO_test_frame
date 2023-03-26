'''
Author: ltt
Date: 2023-03-26 09:37:52
LastEditors: ltt
LastEditTime: 2023-03-26 09:54:27
FilePath: data_2.py
'''
import subprocess, os, sys

(path, _) = os.path.split(sys.argv[0])
subprocess.run(os.path.join(path, "data_2", "data.exe"), timeout=20, shell=False, cwd=os.path.join(path, "data_2"))

with open(os.path.join(path, "data_2", "stdin.txt"), "r") as f:
    print(''.join(f.readlines()))