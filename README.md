# OO_test_frame
- OO homework 评测机框架

## 使用方式

### 启动评测机

```python
from core import *

Program().start() # 启动评测机
```

### 任务创建，启动，等待结束

```python
task = Task(100) # 100 组随机数据
task = Task(data_paths=["path/to/your/data", ...]) # 使用给定的数据路径测试
task.start() # 开始评测(需要先启动评测机)，不会阻塞
task.join() # 等待任务结束
```

### 停止评测机

```python
Program().stop() # 等待所有评测任务结束后关闭评测机
```

### 查看结果

- `output` 目录下，每个 `task` 生成一个 `.csv` 文件
- `temp` 目录下，记录每次评测输出，对应关系可以从控制台的输出找到

## 数据生成器

### 内置

- `generators/dataMaker.py`  made by hhl

### 引用

- `generators/data_2.py`  引用自 [讨论：评测机分享](http://oo.buaa.edu.cn/assignment/423/discussion/1354)，该生成器读取 `./data_2/data.exe` 输出到 `stdin.txt` 的数据并输出到 `stdout`，故在多 `task` 的情况下可能会导致错误。

### 自定义

1. 支持 `.py`、`.jar` 以及 `window` 和 `linux` 下的可执行文件(`.exe`，` ` )
2. 数据输出至标准输出，即 `stdout`
3. 单行数据匹配正则表达式 `^\[ *(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$`
4. 将路径添加至 `setting.json` 配置文件的 `generators`，相对路径、绝对路径均可

## 配置文件

```json
{
	// JAVA_HOME 路径
	"java_home" : "D:\\Program Files\\Java\\JDK8",
    // 暂时不用
	"project_path" : "",
	// 单个测试点最大时限
	"timeout" : 100,
	// 同时评测线程数
	"threads" : 50,
	// 项目
	"jars" : [
		"D:\\LTT\\repository\\OO\\homework_5\\homework_5.jar",
		"D:\\LTT\\repository\\OO\\homework_5\\homework_5_old.jar",
		// "D:\\LTT\\repository\\OO\\homework_5\\homework_5_wrong.jar",
		"D:\\LTT\\repository\\OO\\OO_test_frame\\projects\\hhl.jar",
		"D:\\LTT\\repository\\OO\\OO_test_frame\\projects\\hhl2.jar"
	],
	// 数据生成器
	"generators" : [
		"generators\\dataMaker.py",
		"generators\\data_2.py"
	],
	// 电梯配置
	"elevators": [
		{
			"id" : 1,
			"initial_floor" : 1,
			"capacity" : 6,
			"floors" : [1,2,3,4,5,6,7,8,9,10,11],
			"move_time" : 0.4,
			"open_time" : 0.2,
			"close_time" : 0.2
		}, // 省略
	]
}
```

