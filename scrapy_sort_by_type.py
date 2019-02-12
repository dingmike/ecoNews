# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import requests
import os
import json
from commFun import mkdir

'''
使用爬虫获取经济学人期刊文章,自动保存成markdown格式,可以使用MWeb等markdown工具编辑方便阅读或者转换成word,pdf格式,对出版杂志进行分类存储,并生成目录json,方便转换成电子书
2018-02-22
blog.qzcool.com
pic_quality :图片质量 2018-02-03
    9: 200w
    8: 300w
    7: 400w
    6: 640w
    5: 800w
    4: 1000w
    3: 1200w
    2: 1280w
    1: 1600w
    :return:
by fredliu
'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}


def get_article_content(article_url, save_dir, pic_quality=1):
    '''
    获取单篇文章内容
    :param artical_url: 文章路径
    :param save_dir: 保存路径
    :param pic_quality :图片质量 2018-02-03
        9: 200w
        8: 300w
        7: 400w
        6: 640w
        5: 800w
        4: 1000w
        3: 1200w
        2: 1280w
        1: 1600w
    :return:
    '''

    r = requests.get(article_url, headers=headers)

    # print(r.status_code)
    # print(r.text)

    html_doc = r.text

    soup = BeautifulSoup(html_doc, 'html.parser')

    # print(soup.prettify())
    # flytitle-and-title__flytitle 小标题获取 20180209
    flytitle_and_title__flytitle = soup.find("span", class_="flytitle-and-title__flytitle")

    # flytitle-and-title__title 标题
    flytitle_and_title_title = soup.find("span", class_="flytitle-and-title__title")

    # 保存的文件路径
    file_path = '{}/{}.md'.format(save_dir, flytitle_and_title_title.get_text())

    file_name = flytitle_and_title_title.get_text()

    f = open(file_path, 'w')

    f.write("###### {}\n\r".format(flytitle_and_title__flytitle.get_text()))

    f.write("# {} \n\r".format(flytitle_and_title_title.get_text()))

    print("开始下载文章:{}".format(flytitle_and_title_title.get_text()))

    # blog-post__rubric 子标题
    post_rubric = soup.find("p", class_="blog-post__rubric")

    if post_rubric != None:
        f.write("##### {} \n\r".format(post_rubric.get_text()))

    # 获取图片
    component_image_img = soup.find("img", class_="component-image__img blog-post__image-block")
    # 文件保存路径
    image_save_path = ''
    image_names = []
    if component_image_img != None:
        # print(component_image_img.get('src'))
        # jpg_src = component_image_img.get('src')
        # url_path, img_name = os.path.split(jpg_src)
        # 修改成获取不同分辨率的图片
        image_value = component_image_img.get('srcset').split(',')[-pic_quality]
        # print(image_value)
        image_inline_url = "{}{}".format("https://www.economist.com",
                                         image_value.split(' ')[0].replace('\n', '').replace('\r', ''))
        # print(image_inline_url)
        url_path, img_name = os.path.split(image_inline_url)
        # print(url_path)
        # print(img_name)
        # print('{}/images/{}'.format(save_dir,img_name))

        image_save_path = '{}/images/{}'.format(save_dir, img_name)
        image_names.append(img_name)

        with open(image_save_path, 'wb') as file:
            file.write(requests.get(image_inline_url).content)

        f.write("![image](images/{}) \n\r".format(img_name))

    # blog-post__section-link 文章分类
    blog_post__section_link = soup.find("a", class_="blog-post__section-link")

    # blog-post__datetime 时间
    blog_post__datetime = soup.find("time", class_="blog-post__datetime")

    if blog_post__section_link != None and blog_post__datetime != None:

        f.write("> {} | {} \n\r".format(blog_post__section_link.get_text().replace('print-edition icon ', ''),
                                        blog_post__datetime.get_text()))


    elif blog_post__section_link != None:

        f.write("> {} \n\r".format(blog_post__section_link.get_text().replace('print-edition icon ', '')))


    elif blog_post__datetime != None:
        f.write("> {} \n\r".format(blog_post__datetime.get_text()))

    # 获取文章内容
    blog_post_text = soup.find("div", class_="blog-post__text")

    # 清除订阅邮箱信息
    inbox_newsletter = blog_post_text.find('div', class_='newsletter-form newsletter-form--inline')
    if inbox_newsletter != None:
        inbox_newsletter.decompose()

    # 新增获取文章内部图片
    for children in blog_post_text.children:

        # print(children.name)
        # print(children.attrs)
        if children.name == 'p':

            if children.get('class') == ['xhead']:  # 20190209 添加内容中子标题
                f.write("##### {} \n\r".format(children.get_text()))

            elif children.get('class') == None:
                f.write("{} \n\r".format(children.get_text()))

        if children.name == 'figure':
            # 下载文章内部图片
            image_inline = children.find('img')
            if image_inline is not None:
                image_value = image_inline.get('srcset').split(',')[-pic_quality]
                image_inline_url = "{}{}".format("https://www.economist.com",
                                                 image_value.split(' ')[0].replace('\n', '').replace('\r', ''))
                # print(image_inline_url)

                url_path, img_name = os.path.split(image_inline_url)

                image_save_path = '{}/images/{}'.format(save_dir, img_name)
                image_names.append(img_name)

                with open(image_save_path, 'wb') as file:
                    file.write(requests.get(image_inline_url).content)

                f.write("![image](images/{}) \n\r".format(img_name))

    # 读取文章
    # for p in blog_post_text.find_all('p'):
    #
    #     if p.get('class') == ['xhead']:  # 20190209 添加内容中子标题
    #         f.write("##### {}".format(p.get_text()))
    #         f.write("\n\r")
    #     elif p.get('class') == None:
    #         f.write(p.get_text())
    #         f.write("\n\r")

    # f.write("Power by Fredliu (http://blog.qzcool.com)")
    # f.write("\n\r")

    f.close()

    print("文章下载完成")

    return file_name, image_names


def get_print_edition(edition_number, save_path, pic_quality=1, neterr_retry=10):
    '''
    获取期刊内容
    :param edition_number: 刊物版本日期 2018-02-03
    :param save_path: 保存路径
    :param neterr_retry: 网络错误重试次数
    :param pic_quality :图片质量 2018-02-03
    9: 200w
    8: 300w
    7: 400w
    6: 640w
    5: 800w
    4: 1000w
    3: 1200w
    2: 1280w
    1: 1600w
    :return:
    '''

    url = 'https://www.economist.com/ap/printedition/{}'.format(edition_number)
    print(url)
    r = requests.get(url, headers=headers)

    print(r.status_code)

    html_doc = r.text

    soup = BeautifulSoup(html_doc, 'html.parser')

    # print(soup.prettify())

    # 创建文件目录
    # 保存文章的路径
    article_dir = "{}/{}".format(save_path, edition_number)
    # 保存图片的目录
    image_dir = "{}/{}/images".format(save_path, edition_number)

    mkdir(article_dir)
    mkdir(image_dir)

    # 获取封面标题 20181029
    edition_main_title = soup.find("span", class_="print-edition__main-title-header__edition").get_text()
    # 获取封面图片
    print_edition__cover_widget__image = soup.find("img",
                                                   class_="component-image__img print-edition__cover-widget__image ")
    # print(print_edition__cover_widget__image.get('srcset'))
    cover_widget__images = print_edition__cover_widget__image.get('srcset').split(',')[-pic_quality]
    # print(cover_widget__images.split(' ')[0])
    cover_widget__image_url = "{}{}".format("https://www.economist.com",
                                            cover_widget__images.split(' ')[0].replace('\n', '').replace('\r', ''))
    # print(cover_widget__image_url)

    with open('{}/{}'.format(article_dir, "cover.jpg"), 'wb') as file:
        file.write(requests.get(cover_widget__image_url).content)

    # return

    # 保存文章路径信息
    json_articale = {}
    json_articale['main_title'] = edition_main_title
    json_articale['cover_img'] = "cover.jpg"
    json_articale['edition'] = edition_number

    json_articale['list'] = []

    for list__item in soup.find_all("li", class_="list__item"):
        # print(list__item)
        # 主题标题
        list__title = list__item.find("div", class_="list__title")

        if list__title != None:
            print(list__title.get_text())
        else:
            break

        article_dir_list_title = "{}/{}/{}".format(save_path, edition_number, list__title.get_text())
        image_dir_list_title = "{}/{}/{}/images".format(save_path, edition_number, list__title.get_text())
        mkdir(article_dir_list_title)
        mkdir(image_dir_list_title)

        json_list__item = {}
        json_list__item['list__title'] = list__title.get_text()
        json_list__item['list__item'] = []

        for article_link in list__item.find_all("a", class_="link-button list__link"):
            print("正在下载文章{}".format(article_link.get('href')))
            # 新增副标题采集 2018-11-12
            flytitle = article_link.find("span", class_="print-edition__link-flytitle")
            link_title = article_link.find("span", class_="print-edition__link-title")
            link_title_sub = article_link.find("span", class_="print-edition__link-title-sub")

            if flytitle is not None:
                flytitle = flytitle.get_text()
                link_title = link_title.get_text()
                print("flytitle:{}".format(flytitle))
                print("link_title:{}".format(link_title))
            if link_title_sub is not None:
                link_title_sub = link_title_sub.get_text()
                print("link_title_sub:{}".format(link_title_sub))

            while neterr_retry > 0:
                # 错误重试
                try:
                    file_name, image_names = get_article_content(
                        'https://www.economist.com{}'.format(article_link.get('href')),
                        article_dir_list_title, pic_quality)
                    break
                except Exception as ex:
                    print(str(ex))
                    neterr_retry -= 1

            # print(file_path)
            # print(image_save_path)
            # html = markdownTohtml(file_path)
            # print(html)

            list__link = {'flytitle': flytitle,
                          'link_title': link_title,
                          'link_title_sub': link_title_sub,
                          'list__link': file_name,
                          "articale_image": image_names
                          }
            json_list__item['list__item'].append(list__link)

            # break
        #
        json_articale['list'].append(json_list__item)

    # 保存json信息
    with open('{}/{}'.format(article_dir, "economist.json"), 'wb') as file:
        file.write(json.dumps(json_articale).encode())


def setProxy():
    """
    设置代理访问
    :return:
    """
    import socket
    import socks

    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
    socket.socket = socks.socksocket


if __name__ == '__main__':
    #
    # 设置代理连接访问
    setProxy()
    # 设置保存目录
    save_path = os.getcwd() + '/printedition/Markdown'  # 当前目录下
    # 抓取数据
    get_print_edition('2018-11-03', save_path, pic_quality=6)

    # artical_url = 'https://www.economist.com/news/china/21737447-countrys-politics-have-taken-another-turn-worse-chinas-leader-xi-jinping-will-be'
    # get_article_content(artical_url, '/Users/fred/PycharmProjects/economist')
