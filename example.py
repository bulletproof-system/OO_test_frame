from core import *

tasks = []
Program().start()
for _ in range(10):
	# task = Task(data_paths=["input\\data-114.in", "input\\data-514.in"])
	task = Task(50)
	tasks.append(task)
	task.start()
for task in tasks:
	task.join()
Program().stop()