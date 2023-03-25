'''
Author: ltt
Date: 2023-03-23 23:35:29
LastEditors: ltt
LastEditTime: 2023-03-25 11:24:33
FilePath: utils.py
'''
import subprocess, os

def run(command: list, desc=None, errdesc=None, timeout=None):
    """调用命令"""
    if desc is not None:
        print(desc)

    result = subprocess.run(' '.join(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, timeout=timeout)

    if result.returncode != 0:
        message = f"""{errdesc or 'Error running command'}.
Command: {' '.join(command)}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="gb2312", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="gb2312", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)
    
    return result.stdout.decode(encoding="utf8", errors="ignore")
def printc(str, color=None, end='\n'):
    if color == None:
        print(str, end=end)
    elif color == "red":
        print("\033[31m"+str+"\033[0m", end=end)
    elif color == "green":
        print("\033[32m"+str+"\033[0m", end=end)
    elif color == "yellow":
        print("\033[33m"+str+"\033[0m", end=end)
    elif color == "blue":
        print("\033[34m"+str+"\033[0m", end=end)
    else:
        print(str, end=end)
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]
    
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def split(path: str):
    (filePath, fullname) = os.path.split(path)
    (name, suffix) = os.path.splitext(fullname)
    return (filePath, name, suffix)