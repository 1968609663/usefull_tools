# coding:utf-8
"""
author: allen
summary: 用于背单词或者命令等
email: 1902901293@qq.com
python version: python3.x
运行：
    cmd命令行输入： python recite_words.py
"""
import argparse
import configparser
from configparser import ConfigParser, BasicInterpolation, RawConfigParser
import os
import random
from itertools import chain



class Conf(ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=defaults, strict=False)

    # 这里重写了optionxform方法，直接返回选项名
    def optionxform(self, optionstr):
        return optionstr

class ReciteWords(object):
    def __init__(self):
        self.dir_p = os.path.dirname(os.path.abspath(__file__))
        self.err_info = {}
        self.args = self.parse_command()
        self.filename = self.check_path(self.args.filename)
        self.out = self.check_path(self.args.output)

    def check_path(self, fn):
        res = None
        if os.path.isabs(fn):
            res = fn
        else:
            res = os.path.join(self.dir_p, os.path.basename(fn))
        if not os.path.exists(res):
            print(u"文件路径指定不准确: {}".format(res))
        return res

    def save(self):
        wd = []
        err_seq = list(self.err_info.items())
        print(err_seq)
        err_seq.sort(key=lambda x: x[1], reverse=True)
        for k, v in err_seq:
            wd.append(u"{} >>> {}:{}    错误次数: {}".format(k[0], k[1], v[1], v[0]))
        res = '\n'.join(wd)
        print(u'=' * 10, u'需要复习如下如下', u'=' * 10)
        print(res)
        with open(self.out, 'w', encoding='utf-8') as fp:
            fp.write(res)
        print(u'错误记录已经保存在文件: {}'.format(self.out))

    def run(self):
        data = self.parse_conf()
        w_infos = {k: self.args.weight for k, _ in data.items()}
        print("输入 ‘p’ 为跳过该词")
        while 1:
            seq = list(chain(*[[k] * w_infos[k] for k, _ in data.items()]))
            if not seq:
                raise KeyboardInterrupt
            key = random.choice(seq)
            notice = random.choice(data[key])
            u = input(u"{s}  :  '{n}'  对应>>>".format(s=key[0], n=notice))
            if u.lower() == "quit!":
                raise KeyboardInterrupt
            
            if u.strip() == 'p':
                w_infos[key] = 0
            elif u.strip() != key[1]:
                print(u"正确关系: '{c}'<<-->>'{n}'".format(c=key[1], n=notice))
                w_infos[key] += 1
                if key not in self.err_info:
                    self.err_info[key] = [0, None]
                    self.err_info[key][0] = 0
                    self.err_info[key][1] = notice
                self.err_info[key][0] += 1
            elif w_infos[key] >= 1:
                w_infos[key] -= 1
            print()

    def parse_conf(self):
        """
        解析词库文件
        :return:
        """
        data = {}
        #conf = configparser.ConfigParser()
        conf = Conf()
        try:
            conf.read(self.filename, encoding='gbk')
        except UnicodeDecodeError:
            conf.read(self.filename, encoding='utf-8')
        sec = conf.sections()
        print("当前配置的部分有：", ', '.join(sec))
        user_choice = input("请输入需要复习的部分（用逗号分割，直接回车为所有）>>>")
        if user_choice.strip() == '':
            c_sec = sec
        else:
            c_sec = list(filter(lambda x:x.strip() in sec, user_choice.split(',')))
        for se in c_sec:
            data.update({(se, k): v.split(',') for k, v in conf[se].items()})
        return data

    def parse_command(self):
        """
        解析命令行参数
        :return:
        """
        parser = argparse.ArgumentParser(description="自定义单词或者命令复习,词典文件的词条可以用 '#' 注释，配置值的分隔符为 ',' run: python recite_words.py ")
        parser.add_argument('--filename', help=u'指定自定义词典文件的路径,默认为脚本所在同级目录,默认为: words.ini',
                            default='words.ini')
        parser.add_argument('--output', help=u'输出本次运行过程中出现错误的记录，默认文件为: need_enhance_words.txt',
                            default='need_enhance_words.txt')
        parser.add_argument('--weight', help="自定义词的初始权重,为整数，当回答正确的会被减1，否则加1，每个词对应权重，当权重为0时，该词不会再出现",
                            default=2, type=int)
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    work = ReciteWords()
    try:
        work.run()
    except (KeyboardInterrupt, KeyboardInterrupt, Exception) as e:
        print(e)
        print("退出程序")
    work.save()
