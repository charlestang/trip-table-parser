"""这是一个小工具，用于将滴滴出行、高德地图等打车记录
形成的 PDF 格式电子行程单，转换成文本，CSV 或者 Excel 等格式。"""
import os
import sys
import argparse
import tabula
import logging
import re

from codecs import BOM_UTF8
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from pdfminer.high_level import extract_text

#df = tabular.read_pdf("test.pdf", pages="all")

#tabula.convert_into("testfiles/3639.pdf", "output.csv", output_format="csv", pages='all')
#tabula.convert_into("testfiles/3255.pdf", "output.csv", output_format="csv", pages='all')


def _read_as_text(file_path):
    trip_table_file_content = extract_text(file_path)
    whole_file = [x for x in filter(lambda x: x.strip() != '', "".join(trip_table_file_content).splitlines())]
    return ''.join(whole_file)

def _parse_didi(file_path, line_count=0):
    didi_area = [266, 42.765625, 785.028125, 564.134375]
    if line_count != 0:
        didi_area[2] = 3120.003125 + 31.2375 * line_count
    dfs = tabula.read_pdf(file_path, pages="all", area=didi_area) 
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warn("more than 1 table recognized")
    return dfs[0]

def _parse_gaode(file_path, line_count=0):
    gaode_area = [173, 37.5767, 791.3437, 559.1864]
    if line_count != 0:
        gaode_area[2] = 216.9033 + line_count * 30
    dfs = tabula.read_pdf(file_path, pages="all", area=gaode_area, stream=True) 
    if 0 == len(dfs):
        logging.error("no table found")
    elif 1 < len(dfs):
        logging.warn("more than 1 table recognized")
    return dfs[0]



def _output_csv(df, output_path):
    """利用 DataFrame 自身的 API，导出到 CSV 格式"""
    # 增加 BOM 头，否则不能双击Excel 直接打开CSV
    with open(output_path, mode='wb') as output:
        output.write(BOM_UTF8)

    with open(output_path, mode='a', newline='') as output:
        df.to_csv(output)

def _output_excel(df, output_path):
    """利用 DataFrame 自身的 API，导出到 Excel 格式"""
    df.to_excel(output_path, sheet_name='Sheet1')

def _parse(file_path, platform, line_count):
    if platform == 'didi':
        df = _parse_didi(file_path, line_count)
    else: 
        df = _parse_gaode(file_path, line_count)

    return df

def main(args=None):
    parser = ArgumentParser(description=__doc__, add_help=True,
            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('file_path', metavar='<FILE>', type=str, 
            help='需要处理的行程单文件')
    parser.add_argument('--platform', '-p', metavar='<P>',  type=str, default='unknown',
            help='来源的商户，didi，gaode')
    parser.add_argument('--output', '-o', metavar='<FILE NAME>', type=str, default='output.csv',
            help='输出的文件名，默认是 output.csv，如果类型是 excel，则是 output.xlsx')
    parser.add_argument('--output_type', '-t', metavar='<TYPE>', type=str, default='csv',
            help='输出文件类型，默认是csv，也可以是excel')
    args = parser.parse_args(args)
    
    read_as_string = _read_as_text(args.file_path)

    line_count = 0
    if re.search(r'滴滴出行', read_as_string) != None :
        if args.platform == 'unknown':
            args.platform = 'didi'
        match = re.search(r'共(\d+)笔行程',read_as_string)    
        print(match)
        if match:
            line_count = int(match.group(1))

    if re.search(r'高德地图', read_as_string) != None:
        if args.platform == 'unknown':
            args.platform = 'gaode'
        match = re.search(r'共计(\d+)单行程', read_as_string)
        if match:
            line_count = int(match.group(1))

    df = _parse(args.file_path, args.platform, line_count)
    
    # 滴滴的表头行有一些多余的换行符，导致导出的 CSV 破损
    df.columns = [ name.replace('\r', ' ') for name in df.columns ]

    if args.output_type == 'csv':
        _output_csv(df, args.output)
    elif args.output_type == 'excel':
        # 如果使用默认参数的话，改一下后缀
        if args.output == 'output.csv': 
            args.output = 'output.xlsx'
        _output_excel(df, args.output)
    else:
        print("Error: 不支持的导出格式")

    print(df)

if __name__ == '__main__':
    sys.exit(main())
