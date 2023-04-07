# OO_test_frame

- OO homework 评测机框架
- 支持 `windows`、`linux`
- **特点**
  - 可一次性对多个 jar 包进行测试（采用多线程）
  - 可记录异常信息，且不作为代码正确与否的判断依据
  - 可对生成的数据进行**请求密集度，是否保留初始电梯（用于测试强测），是否生成 MAINTAIN 或 ADD 请求等**的调整
- **现在是叠甲时间**
  - 若出现未知错误烦请联系，**红豆泥阿里嘎多**
    - 评测机：ltt
      - 返回结果若为 **UE** ，则多半为评测机问题
    - 数据生成器：hhl
      - 如出现数据不合理
  - 记录所得的 `Runtime` 是根据输出的最后一项的时间戳决定的，**可能存在误差**
  - 记录所得的 `CPU time` **多少带点问题** XD

## 使用方式

- 你可能需要一点 `python` 的基础知识
- 参考 `example.py`

### 启动评测机

```python
from core import *

Program().start() # 启动评测机
```

### 任务创建，启动，等待结束

```python
task = Task(100) # 100 组随机数据
task = Task(data_paths=[r"path\to\your\data", ...]) # 使用给定的数据路径测试
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

- 生成的数据会保存在 `input` 目录下
  - **注意：** `data` 的编号与 `log` 文件的编号不相关，若想找出对应关系，请查看 `log` 文件
- 评测机只检测数据是否匹配正则表达式，不对数据的正确性进行检测

### 内置

- `generators/dataMaker*.py`  made by hhl
- `generators/dataMaker-hw7.py`  **为第七次作业对应的数据生成器**
- 本数据生成器可在一定程度上调整参数，具体**可参照代码文件中的注释**，根据需求进行更改

### 自定义

1. 支持 `.py`、`.jar` 以及 `window` 和 `linux` 下的可执行文件(`.exe`，` ` )

2. 数据输出至标准输出，即 `stdout`

3. 单行数据匹配正则表达式 

   `^\[ *(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$`

   `^\[ *(?P<time>\d+\.\d+)\]ADD-Elevator-(?P<id>\d+)-(?P<initial_floor>\d+)-(?P<capacity>\d+)-(?P<move_time>\d+\.\d+)-(?P<access>\d+)$`

   `^\[ *(?P<time>\d+\.\d+)\]MAINTAIN-Elevator-(?P<id>\d+)$`

4. 将路径添加至 `settings.json` 配置文件的 `generators`，相对路径、绝对路径均可

## 配置文件

- `default.json` 为模板配置文件
- 真正使用的是 `settings.json` 文件，**需要自行复制并重命名，创建**
- **若遗漏参数，评测机会炸**

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
    "max_time_sync_error_second" : 5,
    "display" : {
        // 仅保存非 AC log 文件
        "brief" : true
    },
    // 项目
    "jars" : [
        "path\\to\\your\\project1",
        "path\\to\\your\\project2"
    ],
    // 数据生成器
    "generators" : [
        "generators\\dataMaker-hw7.py"
    ],
    // 楼层限制
    "Mx" : 4,
    "Nx" : 2,
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

- 注意 `windows` 和 `linux` 下的路径分隔符不同
- 当数据投喂时间明显滞后时考虑减少评测线程数或增大最大计时同步性误差

## 依赖

- 使用命令 `pip install -r requirements.txt` 安装所需依赖模块

### 已知问题

- cpu 时间测量不准，项目使用 `psutil` 模块对 cpu 时间进行测量，只有在用 `jconsole` 连接对应进程时测量的时间才是准确的。~~就离谱~~

## update

#### 2023-4-6

- 更新至 `homework_7`，`homework_6` 评测机位于 `hw6` 分支
- 增添数据生成器注释，更新`README.md`

#### 2023-3-19

- 更新至 `homework_6`，`homework_5` 评测机位于 `hw5` 分支