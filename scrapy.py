# -*- coding: UTF-8 -*-
import os
from scrapy_sort_by_type import get_print_edition, setProxy
from epub_gen import makeEpub

if __name__ == '__main__':

    edition = '2018-11-10'
    cur_path = os.getcwd()
    src_article_path = cur_path + '/printedition/Markdown/'  # 文章保存目录下
    dest_path = cur_path + '/printedition/epub/'  # 当前目录下

    setProxy()  # 设置代理访问
    get_print_edition(edition, src_article_path)  # 抓取经济学人文章生成markdown格式文章
    makeEpub(edition, src_article_path, dest_path)  # 生成电子书
