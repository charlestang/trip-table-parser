# 网约车 PDF 行程单解析 Trip Table Parser

## 前言

本项目实现了一个 PDF 格式行程单的解析，可以将滴滴出行、高德地图导出的 PDF 格式电子行程单，转换成 CSV 或者 Excel 格式。

鄙公司出于财务流程的需要，每次报销网约车的时候，需要逐笔录入网约车行程，通过该工具，将网约车平台导出的 PDF 行程单数据化，可以简化报销单填写的流程。

本项目另一重意义是，展示了 Python 类库在处理 PDF 文件时的能力。这里重点推荐一下 `tabula-py` 和 `pdfminer.six` 这两个类库，是我此次尝试的几个类库里比较好用的。

## 使用方法

### 环境依赖的初始化

这个项目使用 Python 3 编写，使用了 virtualenv 来管理环境依赖。

首先确保你的环境中安装了 Python 3，并对应的安装有 pip（_有些系统里会有两个 pip 命令，pip3 对应着 Python 3 的版本_）。

```shell
pip install virtualenv
```

克隆好项目的代码后，首先进入目录，然后执行命令：

```shell
virtualenv .
```

这个命令会初始化整个目录的 virtualenv 的结构，然后，进入项目根目录，执行：

```shell
source bin/activate
```

到此，项目的 virtualenv 环境初始化完成，然后，恢复包依赖：

```shell
pip install -r requirements.pip
```

这个命令会在项目的虚拟环境下，安装所有一类的软件包。如果需要退出 virtualenv 环境，直接执行：

```shell
deactivate
```

### 命令的使用方法

```shell
# 该命令将展示一个帮助说明
python trip_table_parser.py -h

# 常见用法，只给出 PDF 行程单的路径，则默认会在命令行打印出识别的结果，并导出到工作目录，导出格式默认是 CSV 格式
python trip_table_parser.py /home/jack/滴滴行程单.pdf
```

## 开发说明

作者本地开发环境：

 * MacOS 10.14.6
 * Python 3.7.6
 * Java 1.8.0_121

当前版本引用的 python 类库，全部使用 `pip` 安装：

 * chardet==3.0.4
 * distro==1.4.0
 * et-xmlfile==1.0.1
 * jdcal==1.4.1
 * numpy==1.18.1
 * openpyxl==3.0.3
 * pandas==1.0.1
 * pdfminer.six==20200124
 * pycryptodome==3.9.7
 * python-dateutil==2.8.1
 * pytz==2019.3
 * six==1.14.0
 * sortedcontainers==2.1.0
 * tabula-py==2.0.4
