'''
Author: ltt
Date: 2023-03-24 12:00:07
LastEditors: ltt
LastEditTime: 2023-03-24 12:04:46
FilePath: main.py
'''
from core.core import Checker

if __name__ == "__main__":
    checker = Checker(1, r"D:\LTT\repository\OO\homework_5\stdin.txt", r"D:\LTT\repository\OO\homework_5\homework_5.jar")
    checker.run()
    print(checker)