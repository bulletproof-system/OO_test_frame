'''
Author: ltt
Date: 2023-04-23 17:40:28
LastEditors: ltt
LastEditTime: 2023-04-23 18:11:32
FilePath: std.py
'''

import os, psutil
from core import utils
from config import settings

def calc_std(data_path):
	(_, data_name, _) = utils.split(data_path)
	path = os.path.join("std", data_name + '.std')
	commond = utils.commond(settings.std)
	try:
		with open(data_path, "r") as input:
			with open(path, "w") as std:
				p = psutil.Popen(commond, shell=False, stdin=input, stdout=std, stderr=None)
				try:
					return_code = p.wait(timeout=settings.timeout)
					if (return_code != 0):
						raise Exception()
				except:
					raise
	except:
		utils.printc("std error\n", "red", end='')
	return path


