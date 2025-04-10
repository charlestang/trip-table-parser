# 网约车 PDF 行程单解析 Trip Table Parser

- [网约车 PDF 行程单解析 Trip Table Parser](#网约车-pdf-行程单解析-trip-table-parser)
  - [前言](#前言)
  - [安装方法](#安装方法)
    - [安装 pipx](#安装-pipx)
    - [从源码安装](#从源码安装)
    - [环境要求](#环境要求)
  - [使用方法](#使用方法)
    - [命令的使用方法](#命令的使用方法)
  - [开发说明](#开发说明)

## 前言

本项目实现了一个 PDF 格式行程单的解析，可以将网约车平台导出的 PDF 格式电子行程单，转换成 CSV 或者 Excel 格式。目前支持的平台有：

 * 滴滴出行
 * 高德地图
 * 首汽约车
 * 美团打车
 * 花小猪打车

鄙公司出于财务流程的需要，每次报销网约车的时候，需要逐笔录入网约车行程，通过该工具，将网约车平台导出的 PDF 行程单数据化，可以简化报销单填写的流程。

本项目另一重意义是，展示了 Python 类库在处理 PDF 文件时的能力。这里重点推荐一下 `tabula-py` 和 `pdfminer.six` 这两个类库，是我此次尝试的几个类库里比较好用的。

## 安装方法

### 安装 pipx

[pipx](https://pypa.github.io/pipx/) 是一个用于安装和运行 Python 应用的工具，它可以将 Python 应用安装到独立的环境中。

安装 pipx 的步骤如下：

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

因为只是一个很小的功能，所以没有把项目发布到包管理器服务中，所以不能使用命令直接安装。

### 从源码安装

要从源码安装，可以按照以下步骤操作：

1. 克隆项目代码：
```bash
git clone https://github.com/yourusername/trip-table-parser.git
cd trip-table-parser
```

2. 安装项目：
```bash
# 以调试模式安装，安装完，修改代码可以立即生效
pipx install -e .

# 以生产模式安装，安装完，修改代码需要重新安装
pipx install .
```

### 环境要求

本工具需要以下环境：

1. Python 3.8 或更高版本
2. Java 运行时环境（JRE）8 或更高版本
   - 在 macOS 上可以使用 `brew install java` 安装
   - 在 Ubuntu/Debian 上可以使用 `sudo apt install default-jre` 安装
   - 在 Windows 上可以从 Oracle 官网下载安装

## 使用方法

### 命令的使用方法

在命令行中使用 `-h` 或者 `--help` 参数展示详细的使用方法：

```bash
trip-table-parser -h
```

最简单的方法，是直接在后面跟上需要转换的文件，其他参数都选用默认值，程序会自动猜测到底是来自哪个平台：

```bash
# 常见用法，只给出 PDF 行程单的路径，则默认会在命令行打印出识别的结果，并导出到工作目录，导出格式默认是 CSV 格式
trip-table-parser /path/to/your/trip.pdf
```

## 开发说明

作者本地开发环境：

 * MacOS 10.14.6
 * Python 3.7.6
 * **Java 1.8.0_121**（tabula-py 是对 tabula-java 的封装，所以需要依赖 Java）

当前版本引用的 python 类库，全部使用 `pipx` 安装：

 * chardet==3.0.4
 * distro==1.4.0
 * et-xmlfile==1.0.1
 * jdcal==1.4.1
 * numpy==1.18.1
 * **openpyxl**==3.0.3 （导出 Excel 格式依赖）
 * pandas==1.0.1
 * **pdfminer.six**==20200124
 * pycryptodome==3.9.7
 * python-dateutil==2.8.1
 * pytz==2019.3
 * six==1.14.0
 * sortedcontainers==2.1.0
 * **tabula-py**==2.0.4
