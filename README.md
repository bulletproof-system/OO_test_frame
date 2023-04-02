# OO_test_frame

- OO homework 评测机框架
- 支持 `windows`、`linux`

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
- `log` 目录下，记录每次评测输出，对应关系可以从控制台的输出找到

## 数据生成器

### 内置

- `generators/dataMaker*.py`  made by hhl

### 自定义

1. 支持 `.py`、`.jar` 以及 `window` 和 `linux` 下的可执行文件(`.exe`，` ` )

2. 数据输出至标准输出，即 `stdout`

3. 单行数据匹配正则表达式 

   `^\[ *(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$`

   `^\[ *(?P<time>\d+\.\d+)\]ADD-Elevator-(?P<id>\d+)-(?P<initial_floor>\d+)-(?P<capacity>\d+)-(?P<move_time>\d+\.\d+)$`

   `^\[ *(?P<time>\d+\.\d+)\]MAINTAIN-Elevator-(?P<id>\d+)$`

4. 将路径添加至 `settings.json` 配置文件的 `generators`，相对路径、绝对路径均可

## 配置文件

- `default.json` 为模板配置文件，真正使用的是 `settings.json` 文件，需要自行创建

```json
{
	// JAVA_HOME 路径
	"java_home" : "your\\java_home",
	// 暂时不用
	"project_path" : "",
	// 单个测试点最大时限
	"timeout" : 100,
	// 同时评测线程数
	"threads" : 50,
	// 最大计时同步性误差
	"max_time_sync_error_second" : 1,
	"display" : {
		// 仅保存非 AC log 文件
		"brief" : true
	},
	// 项目
	"jars" : [
		"path\\to\\your\\project"
	],
	// 数据生成器
	"generators" : [
		"generators\\dataMaker-3.py"
	],
	// 电梯配置
	"elevators": {
		"default" : {
			"initial_floor" : 1,
			"capacity" : 6,
			"floors" : [1,2,3,4,5,6,7,8,9,10,11],
			"move_time" : 0.4,
			"open_time" : 0.2,
			"close_time" : 0.2
		},
		"1" : {},
		"2" : {},
		"3" : {},
		"4" : {},
		"5" : {},
		"6" : {}
	}
}
```

## 依赖

- 使用命令 `pip install -r requirements.txt` 安装所需依赖模块
