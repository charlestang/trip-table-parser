"""网约车平台 PDF 格式电子行程单解析器

滴滴出行，高德地图等当代打车软件，都会提供电子行程单导出功能，主要用于财务报销时候的凭据。
但是 PDF 格式不方便系统进行数据的分析和读取，本工具提供了一个简单的命令，用于将 PDF 格式
行程单导出成 CSV 格式或者 Excel 格式。
"""
import os
import sys
import argparse
import re
import logging
import pandas
import tabula

from codecs import BOM_UTF8
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError


def _parse_didi(file_path, line_count=0):
    """解析滴滴出行的行程单，表头行需要特别清洗"""
    didi_area = [266, 42.765625, 785.028125, 564.134375]
    if line_count != 0:
        didi_area[2] = 3120.003125 + 31.2375 * line_count
    dfs = tabula.read_pdf(file_path, pages="all", area=didi_area)
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warning("more than 1 table recognized")
    df = dfs[0]
    # 滴滴的表头行有一些多余的换行符，导致导出的 CSV 破损
    df.columns = [name.replace('\r', ' ') for name in df.columns]
    return df


def _parse_gaode(file_path, line_count=0):
    """解析高德地图的行程单"""
    gaode_area = [173, 37.5767, 791.3437, 559.1864]
    if line_count != 0:
        gaode_area[2] = 216.9033 + line_count * 30
    dfs = tabula.read_pdf(file_path, pages="all", area=gaode_area, stream=True)
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warning("more than 1 table recognized")
    return dfs[0]


def _parse_shouqi(file_path, line_count=0):
    """解析首汽约车的行程单，是最难处理的一种类型"""
    shouqi_area = [153.584375, 29.378125, 817.753125, 566.365625]
    if line_count != 0:
        shouqi_area[2] = 176.64062 + 15.95379 * line_count
    dfs = tabula.read_pdf(file_path, pages="all", area=shouqi_area, stream=True)
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warning("more than 1 table recognized")
    df = dfs[0]

    # 对识别结果进行处理
    # 表头处理
    rows = df.iloc[0].values
    df.columns = [str(x).strip() + ('' if str(y).strip() == 'nan' else str(y).strip()) for x, y in
                  zip(df.columns, rows)]

    # 数据处理
    data = df.values
    row_index = range(len(data))
    new_data = []
    for x, y in zip(row_index[1::2], row_index[2::2]):
        new_row = [str(a).strip() + ('' if str(b).strip() == 'nan' else str(b).strip()) for a, b in
                   zip(data[x], data[y])]
        new_data.append(new_row)

    new_df = pandas.DataFrame(new_data, columns=df.columns)
    return new_df


def _parse_meituan(file_path, line_count=0):
    """解析美团打车的行程单，也是比较难处理的一种类型"""
    meituan_area = [285.7275, 41.6925, 314.7975, 571.0725]
    if line_count:
        meituan_area[2] = 314.7975 + 28.305 * line_count
    dfs = tabula.read_pdf(file_path, pages='1', area=meituan_area, stream=True)
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warning("more than 1 table recognized")

    df = dfs[0]

    data = df.values
    row_index = range(len(data))
    new_data = []
    for x, y in zip(row_index[::2], row_index[1::2]):
        new_row = [('' if str(x).strip() == 'nan' else (str(x).strip() + ' ')) + str(y).strip() for x, y in
                   zip(data[x], data[y])]
        new_data.append(new_row)
    new_df = pandas.DataFrame(new_data, columns=df.columns)

    return new_df


def _parse_unknown(file_path):
    dfs = tabula.read_pdf(file_path, pages="all", stream=True)
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warning("more than 1 table recognized")
    return dfs[0]


def _output_csv(df, output_path):
    """利用 DataFrame 自身的 API，导出到 CSV 格式"""
    # 增加 BOM 头，否则不能双击Excel 直接打开CSV
    with open(output_path, mode='wb') as output:
        output.write(BOM_UTF8)

    with open(output_path, mode='a', newline='') as output:
        df.to_csv(output, index=False)


def _output_excel(df, output_path):
    """利用 DataFrame 自身的 API，导出到 Excel 格式"""
    df.to_excel(output_path, index=False, sheet_name='Sheet1')


def _output(df, file_type):
    extension = {'csv': 'csv', 'excel': 'xlsx'}
    if file_type in ['csv', 'excel']:
        exporter = getattr(sys.modules[__name__], '_output_' + file_type)
        exporter(df, 'output.' + extension[file_type])
    else:
        logging.error('不支持的导出文件类型，目前仅支持 CSV 和 Excel')


platform_pattern = {
    'didi':    {'title_like': '滴滴出行', 'line_count_like': r'共(\d+)笔行程', 'parser': _parse_didi},
    'gaode':   {'title_like': '高德地图', 'line_count_like': r'共计(\d+)单行程', 'parser': _parse_gaode},
    'shouqi':  {'title_like': '首汽约车电子行程单', 'line_count_like': r'共(\d+)个行程', 'parser': _parse_shouqi},
    'meituan': {'title_like': '美团打车', 'line_count_like': r'(\d+)笔行程', 'parser': _parse_meituan}
}


def _extract_text(file_path):
    try:
        pdf_to_text = extract_text(file_path)
        return ''.join([x for x in filter(lambda x: x.strip() != '', "".join(pdf_to_text).splitlines())])
    except PDFSyntaxError as pse:
        logging.error('文件解析错误，不是一个正确的 PDF 文件')
        raise Exception('无法解析 PDF') from pse
    return ''


def _read_meta(file_path):
    """读取行程单的信息，识别平台、行数、页数等"""
    file_content = _extract_text(file_path)
    line_count = 0
    for p, pattern in platform_pattern.items():
        if re.search(pattern['title_like'], file_content):
            match = re.search(pattern['line_count_like'], file_content)
            if match:
                line_count = int(match.group(1))
            return p, line_count, pattern['parser']
    return 'unknown', 0, _parse_unknown


def main(args=None):
    parser = ArgumentParser(description=__doc__, add_help=True,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('file_path', metavar='<FILE>', type=str,
                        help='需要处理的行程单文件')
    parser.add_argument('--output_type', '-t', metavar='<TYPE>', type=str, default='csv',
                        help='输出文件类型，默认是csv，也可以是excel')
    args = parser.parse_args(args)

    platform, line_count, parser = _read_meta(args.file_path)
    print("识别出来的平台是：%s，行程行数是：%d" % (platform, line_count))

    df = parser(args.file_path, line_count)
    _output(df, args.output_type)

    print(df)


if __name__ == '__main__':
    sys.exit(main())
