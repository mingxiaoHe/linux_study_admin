#!/usr/bin/env python
# coding=utf-8

import os
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.concurrent
import tornado.escape
import tornado
import time
import json

from tornado.options import define, options
from modules.sqlhelper import SqlHelper
from modules.common import get_md5_string, turn_to_int, turn_userinfo_to_dict, turn_categoryinfo_to_dict
from modules import ui_methods
from modules.PageHelper import Pager, PageInfo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

define('port', default=8001, help='run on the given port', type=int)

DOMAIN = 'http://127.0.0.1:8000'

STATUS_SUCCESS = {"status": True}
STATUS_FAIL = {"status": False}


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.session = SqlHelper()

    def get_current_user(self):
        return self.get_secure_cookie('user_name')


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        self.render('index.html')


class UrlHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self, types, page):
        if hasattr(self, types):
            func = getattr(self, types)
            func(page)

    def admin(self, page):
        page = turn_to_int(page, 1)
        # 此分类下的所有文章
        all_admins = self.session.get_all_admins().users

        # uri的dirname
        dir_uri_name = os.path.dirname(self.request.uri)

        count = self.session.get_all_admins_count()

        # 检测页数是否合法，如果页数超过
        page_obj = PageInfo(page, count, per_item=5)
        all_page_count = page_obj.all_page_count
        if page > all_page_count:
            page = all_page_count
        elif page <= 0:
            page = 1

        page_string = Pager(page, all_page_count, dir_uri_name)

        self.render('user/admin.html',
                    admins=all_admins[page_obj.start:page_obj.end],
                    page_string=page_string,
                    )
    def ordinary(self, page):

        page = turn_to_int(page, 1)
        # 此分类下的所有文章
        all_ordinaries = self.session.get_all_ordinaries().users

        # uri的dirname
        dir_uri_name = os.path.dirname(self.request.uri)

        count = self.session.get_all_ordinaries_count()

        # 检测页数是否合法，如果页数超过
        page_obj = PageInfo(page, count, per_item=5)
        all_page_count = page_obj.all_page_count
        if page > all_page_count:
            page = all_page_count
        elif page <= 0:
            page = 1

        page_string = Pager(page, all_page_count, dir_uri_name)

        self.render('user/ordinary.html',
                    ordinaries=all_ordinaries[page_obj.start:page_obj.end],
                    page_string=page_string,
                    )

class ArticleHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, type, page):
        if type == 'info':
            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            all_articles = self.session.get_all_article()

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            count = self.session.get_articles_count()

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=5)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('article/info.html',
                        articles=all_articles[page_obj.start:page_obj.end],
                        page_string=page_string,
                        )
        elif type == 'add':
            self.render('article/add.html',
                        categories = self.session.get_all_category(),
                        )
        elif type == 'next':
            self.render('article/next.html')

    def post(self, type, page):
        if type == 'add':
            title = self.get_argument('title')
            content = self.get_argument('content')
            description = self.get_argument('description')
            tag = self.get_argument('tag').split()
            category = self.get_argument('category')
            status = self.session.add_article(title, description, category, tag, content, super().get_current_user())
            if status:
                self.redirect('/article/next.html')
            else:
                print(222)

class ArticleEditHandler(BaseHandler):
    def get(self, id):
        self.render('article/add.html',
                    article_info=self.session.get_article_byid(id),
                    categories=self.session.get_all_category(),
                    )
    def post(self, id):
        title = self.get_argument('title')
        content = self.get_argument('content')
        description = self.get_argument('description')
        tag = self.get_argument('tag').split()
        category = self.get_argument('category')
        status = self.session.update_article(id, title, description, category, tag, content)
        if status:
            self.redirect('/article/next.html')
        else:
            print(222)


class CategoryHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, type, page):
        if type == 'info':
            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            all_category = self.session.category()
            print(all_category[0].name)

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            count = self.session.get_category_count()

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=5)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('category/info.html',
                        categories=all_category[page_obj.start:page_obj.end],
                        page_string=page_string,
                        category = self.session.get_category_info_by_basename(type),
                        )
        else:
            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            cate_articles = self.session.get_category_articles_by_basename(type).articles

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            # 此分类信息的信息
            category = self.session.get_category_info_by_basename(type)

            # 根据此分类的id查找文章并计算count
            count = self.session.get_category_articles_count(category.id)

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=5)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('category/cate.html',
                        cate_articles=cate_articles[page_obj.start:page_obj.end],
                        page_string=page_string,
                        category=self.session.get_category_info_by_basename(type),
                        )


class TagHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, type, page):
        if type == 'info':
            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            all_tag = self.session.get_tag_list()

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            count = self.session.get_tag_count()

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=5)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('tag/info.html',
                        tags=all_tag[page_obj.start:page_obj.end],
                        page_string=page_string,
                        )
        else:
            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            tag_articles = self.session.get_tag_articles_by_tagname(type).articles

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            # 此分类信息的信息
            tag = self.session.get_tag_info_by_tagname(type)

            # 根据此分类的id查找文章并计算count
            count = self.session.get_tag_articles_count(tag.id)

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=1)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('tag/cate.html', tag=tag,
                        tag_articles=tag_articles[page_obj.start:page_obj.end],
                        page_string=page_string,
                        )

class LinksHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, type, page):
        if type == 'info':

            page = turn_to_int(page, 1)
            # 此分类下的所有文章
            all_links = self.session.get_all_links()

            # uri的dirname
            dir_uri_name = os.path.dirname(self.request.uri)

            count = self.session.get_links_count()

            # 检测页数是否合法，如果页数超过
            page_obj = PageInfo(page, count, per_item=3)
            all_page_count = page_obj.all_page_count
            if page > all_page_count:
                page = all_page_count
            elif page <= 0:
                page = 1

            page_string = Pager(page, all_page_count, dir_uri_name)

            self.render('links/info.html',
                        links=all_links[page_obj.start:page_obj.end],
                        page_string=page_string,
                        )

    def post(self, type):
        pass

class DescriptionHandler(BaseHandler):
    def get(self, type):
        if type == 'info':
            self.render('desc/info.html',
                        descs=self.session.get_description(),
                        )

class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        if self.get_secure_cookie('username'):
            self.redirect('/')
        else:
            self.render('login.html')

    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        user_obj = self.session.get_user_info(username)

        if username == user_obj.username and get_md5_string(password) == user_obj.password:
            self.set_secure_cookie('user_name', self.get_argument('username'), expires_days=None)
            self.redirect('/')
        else:
            self.redirect('/user/error')

class LogoutHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.clear_cookie('username')
        self.redirect('/login')

class MultiDeleteHandler(BaseHandler):
    @tornado.web.asynchronous
    def post(self, types):
        if hasattr(self, types):
            func = getattr(self, types)
            func()

    def user(self):
        id_list = self.get_arguments('user_id')
        status = self.session.delete_users(id_list)
        if status:
            self.render('user/admin.html',
                        admins=self.session.get_admins_info().users,
                        )

    def category(self):
        category_id_list = self.get_arguments('category_id')
        status = self.session.delete_categories(category_id_list)
        if status:
            self.redirect('/category/info/1.html')


    def cate_article(self):
        articles_id_list = self.get_arguments('article_id')
        basename = self.session.get_article_byid(articles_id_list[0]).category.basename
        status = self.session.delete_articles(articles_id_list)
        if status:
            self.redirect('/category/%s/1.html' % basename)

    def article(self):
        articles_id_list = self.get_arguments('article_id')
        status = self.session.delete_articles(articles_id_list)
        if status:
            self.redirect('/article/info/1.html')

    def tag_article(self):
        articles_id_list = self.get_arguments('article_id')
        tagname = self.get_argument('tagname')
        status = self.session.delete_articles(articles_id_list)
        if status:
            self.redirect('/tag/%s/1.html' % tagname)

    def tag(self):
        tag_id_list = self.get_arguments('tag_id')
        status = self.session.delete_tags(tag_id_list)
        if status:
            self.redirect('/tag/info/1.html')



class AjaxHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @tornado.web.asynchronous
    def post(self, types):
        if hasattr(self, types):
            func = getattr(self, types)
            func()

    def get(self, types):
        if hasattr(self, types):
            func = getattr(self, types)
            func()

    def get_category(self):
        category_list = self.session.category()
        ret = [{"name": category_obj.name, "basename": category_obj.basename} for category_obj in category_list]
        self.write(tornado.escape.json_encode(ret))
        self.finish()

    def get_tag(self):
        tag_list = self.session.get_tag_list()
        ret = [ tag.name for tag in tag_list]
        self.write(tornado.escape.json_encode(ret))
        self.finish()

    def change_user(self):
        id = self.get_argument('id')
        username = self.get_argument('username')
        role = self.get_argument('role')
        email = self.get_argument('email')
        result = self.session.set_user_info(id, username, role, email)
        user_info = SqlHelper().get_user_info_byid(id)
        user = turn_userinfo_to_dict(user_info)
        if result:
            self.write(tornado.escape.json_encode(user))
            self.finish()
        else:
            self.write(tornado.escape.json_encode(STATUS_FAIL))
            self.finish()
    def change_pass(self):
        id = self.get_argument('id')
        password = self.get_argument('password')
        repassword = self.get_argument('repassword')
        if password == repassword:
            status = self.session.change_user_passwd_byid(id, get_md5_string(password))
            if status:
                self.write(tornado.escape.json_encode(STATUS_SUCCESS))
                self.finish()
            else:
                self.write(tornado.escape.json_encode(STATUS_FAIL))
                self.finish()
    def delete_user(self):
        id = self.get_argument('id')
        status = self.session.delete_user_byid(id)
        if status:
            self.write(tornado.escape.json_encode({"id": id}))
            self.finish()
        else:
            self.write(tornado.escape.json_encode(STATUS_FAIL))
            self.finish()


    def change_category(self):
        id = self.get_argument('id')
        category_name = self.get_argument('categoryName')
        category_basename = self.get_argument('categoryBasename')

        status = self.session.change_category(id, category_name, category_basename)
        if status:
            category_info = self.session.get_category_info_byid(id)
            category = turn_categoryinfo_to_dict(category_info)
            self.write(category)
            self.finish()
        else:
            self.write(tornado.escape.json_encode(STATUS_FAIL))
            self.finish()






try:
    import simplejson as json
except ImportError:
    import json
import os
import re
import base64
import datetime
import uuid

# /* 前后端通信相关的配置,注释只允许使用多行方式 */

ueditor_config = {
    # /* 上传图片配置项 */
    "imageActionName": "uploadimage",  # /* 执行上传图片的action名称 */
    "imageFieldName": "upfile",  # /* 提交的图片表单名称 */
    "imageMaxSize": 2048000,  # /* 上传大小限制，单位B */
    "imageAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # /* 上传图片格式显示 */
    "imageCompressEnable": True,  # /* 是否压缩图片,默认是true */
    "imageCompressBorder": 1600,  # /* 图片压缩最长边限制 */
    "imageInsertAlign": "center",  # /* 插入的图片浮动方式 */
    "imageUrlPrefix": "/upload/image/",  # /* 图片访问路径前缀 */
    "imagePathFormat": "upload/image/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    # /* {filename} 会替换成原文件名,配置这项需要注意中文乱码问题 */
    # /* {rand:6} 会替换成随机数,后面的数字是随机数的位数 */
    # /* {time} 会替换成时间戳 */
    # /* {yyyy} 会替换成四位年份 */
    # /* {yy} 会替换成两位年份 */
    # /* {mm} 会替换成两位月份 */
    # /* {dd} 会替换成两位日期 */
    # /* {hh} 会替换成两位小时 */
    # /* {ii} 会替换成两位分钟 */
    # /* {ss} 会替换成两位秒 */
    # /* 非法字符 \ : * ? " < > | */
    # /* 具请体看线上文档: fex.baidu.com/ueditor/#use-format_upload_filename */

    # /* 涂鸦图片上传配置项 */
    "scrawlActionName": "uploadscrawl",  # /* 执行上传涂鸦的action名称 */
    "scrawlFieldName": "upfile",  # /* 提交的图片表单名称 */
    "scrawlPathFormat": "upload/image/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    "scrawlMaxSize": 2048000,  # /* 上传大小限制，单位B */
    "scrawlUrlPrefix": "/upload/image/",  # /* 图片访问路径前缀 */
    "scrawlInsertAlign": "center",

    # /* 截图工具上传 */
    "snapscreenActionName": "uploadimage",  # /* 执行上传截图的action名称 */
    "snapscreenPathFormat": "upload/image/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    "snapscreenUrlPrefix": "/upload/image/",  # /* 图片访问路径前缀 */
    "snapscreenInsertAlign": "center",  # /* 插入的图片浮动方式 */

    # /* 抓取远程图片配置 */
    "catcherLocalDomain": ["127.0.0.1", "localhost", "img.baidu.com"],
    "catcherActionName": "catchimage",  # /* 执行抓取远程图片的action名称 */
    "catcherFieldName": "source",  # /* 提交的图片列表表单名称 */
    "catcherPathFormat": "upload/image/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    "catcherUrlPrefix": "/upload/image/",  # /* 图片访问路径前缀 */
    "catcherMaxSize": 2048000,  # /* 上传大小限制，单位B */
    "catcherAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # /* 抓取图片格式显示 */

    # /* 上传视频配置 */
    "videoActionName": "uploadvideo",  # /* 执行上传视频的action名称 */
    "videoFieldName": "upfile",  # /* 提交的视频表单名称 */
    "videoPathFormat": "upload/video/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    "videoUrlPrefix": "/upload/video/",  # /* 视频访问路径前缀 */
    "videoMaxSize": 102400000,  # /* 上传大小限制，单位B，默认100MB */
    "videoAllowFiles": [
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid"],  # /* 上传视频格式显示 */

    # /* 上传文件配置 */
    "fileActionName": "uploadfile",  # /* controller里,执行上传视频的action名称 */
    "fileFieldName": "upfile",  # /* 提交的文件表单名称 */
    "filePathFormat": "upload/file/",  # /* 上传保存路径,可以自定义保存路径和文件名格式 */
    "fileUrlPrefix": "/upload/file/",  # /* 文件访问路径前缀 */
    "fileMaxSize": 51200000,  # /* 上传大小限制，单位B，默认50MB */
    "fileAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp",
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml"
    ],  # /* 上传文件格式显示 */

    # /* 列出指定目录下的图片 */
    "imageManagerActionName": "listimage",  # /* 执行图片管理的action名称 */
    "imageManagerListPath": "upload/image/",  # /* 指定要列出图片的目录 */
    "imageManagerListSize": 20,  # /* 每次列出文件数量 */
    "imageManagerUrlPrefix": "/upload/image/",  # /* 图片访问路径前缀 */
    "imageManagerInsertAlign": "center",  # /* 插入的图片浮动方式 */
    "imageManagerAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # /* 列出的文件类型 */

    # /* 列出指定目录下的文件 */
    "fileManagerActionName": "listfile",  # /* 执行文件管理的action名称 */
    "fileManagerListPath": "upload/file/",  # /* 指定要列出文件的目录 */
    "fileManagerUrlPrefix": "/upload/file/",  # /* 文件访问路径前缀 */
    "fileManagerListSize": 20,  # /* 每次列出文件数量 */
    "fileManagerAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp",
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml"
    ]  # /* 列出的文件类型 */
}


class UeditorEnv():
    walkImageCache = []
    walkFileCache = []

    def __init__(self, with_list_cache=False):
        self.config = ueditor_config
        # print(self.config)

        # build file lists as cache
        if with_list_cache:
            self.walkin(self.config['imagePathFormat'], self.walkImageCache)
            self.walkin(self.config['filePathFormat'], self.walkFileCache)
            # print json.dumps(self.config, indent=1)

    # this only for single runtime instance
    # only if you use NAS as the file backend
    # for multi runtime instance please use database for indexing
    # also ,please add your file sync implement

    def walkin(self, base_dir, cache):
        for root, dirs, files in os.walk(base_dir):
            for name in files:
                cache.append({'file': os.path.join(root.replace(base_dir, ''), name)})

    def get_list(self, start=0, count=20, is_image=True):
        ret = []
        if is_image:
            cache = self.walkImageCache
        else:
            cache = self.walkFileCache

        # fill it as possible, if overthe range, simplely go out
        try:
            for index in range(start, start + count):
                ret.append({'url': cache[index]['file']})
        except:
            pass

        return ret

    def append_file(self, filename, is_image=True):
        if is_image:
            cache = self.walkImageCache
        else:
            cache = self.walkFileCache
        cache.append({'file': filename})


u4Ts = UeditorEnv(with_list_cache=True)


class UploadHandler(tornado.web.RequestHandler):
    executor = tornado.concurrent.futures.ThreadPoolExecutor(100)

    @tornado.concurrent.run_on_executor()
    def save_file(self, fileobj, base_dir, filename=None, user=None, is_image=True):
        if not user:
            user = 'ueditor'

        upload_path = user + '/' + datetime.datetime.utcnow().strftime('%Y%m%d') + '/'

        # 安全过滤
        base_dir = base_dir.replace('../', '')
        base_dir = re.sub(r'^/+', '', base_dir)
        if not os.path.exists(base_dir + upload_path):
            os.makedirs(base_dir + upload_path)

        if not filename:
            uuidhex = uuid.uuid1().hex
            file_ext = os.path.splitext(fileobj['filename'])[1].lower()
            filename = uuidhex + file_ext

        if not os.path.exists(base_dir + upload_path + filename):
            with open(base_dir + upload_path + filename, 'wb') as f:
                f.write(fileobj['body'])
            result = {
                'state': 'SUCCESS',
                'url': upload_path + filename,
                'title': filename,
                'original': fileobj['filename'],
            }
            u4Ts.append_file(upload_path + filename, is_image=is_image)
            self.write(result)
            self.finish()

    @tornado.web.gen.coroutine
    def get(self):
        action = self.get_argument('action')
        if action == 'config':
            self.write(ueditor_config)
            return

        elif action == u4Ts.config['imageManagerActionName']:
            start = int(self.get_argument('start'))
            size = int(self.get_argument('size'))
            urls = u4Ts.get_list(start, size, is_image=True)
            result = {
                'state': 'SUCCESS',
                'list': urls,
                'start': start,
                'total': len(urls)
            }
            self.write(result)
            self.finish()
            return

        elif action == u4Ts.config['fileManagerActionName']:
            start = int(self.get_argument('start'))
            size = int(self.get_argument('size'))
            urls = u4Ts.get_list(start, size, is_image=False)
            result = {
                'state': 'SUCCESS',
                'list': urls,
                'start': start,
                'total': len(urls)
            }
            self.write(result)
            self.finish()
            return

        self.finish()

    @tornado.web.gen.coroutine
    def post(self):
        action = self.get_argument('action')
        if action == u4Ts.config['imageActionName']:
            for keys in self.request.files:
                for fileobj in self.request.files[keys]:
                    yield self.save_file(base_dir=u4Ts.config['imagePathFormat'], fileobj=fileobj)

        elif action == u4Ts.config['scrawlActionName']:
            # python2
            # fileobj = {'filename': 'scrawl.png', 'body': base64.decodestring(self.get_argument(u4Ts.config['scrawlFieldName']))}
            # python3
            fileobj = {'filename': 'scrawl.png',
                       'body': base64.decodebytes(self.get_argument(u4Ts.config['scrawlFieldName']).encode('utf-8'))}
            yield self.save_file(base_dir=u4Ts.config['scrawlPathFormat'], fileobj=fileobj)

        elif action == u4Ts.config['snapscreenActionName']:
            for keys in self.request.files:
                for fileobj in self.request.files[keys]:
                    yield self.save_file(base_dir=u4Ts.config['snapscreenPathFormat'], fileobj=fileobj)

        elif action == u4Ts.config['videoActionName']:
            for keys in self.request.files:
                for fileobj in self.request.files[keys]:
                    yield self.save_file(base_dir=u4Ts.config['videoPathFormat'], fileobj=fileobj)

        elif action == u4Ts.config['fileActionName']:
            for keys in self.request.files:
                for fileobj in self.request.files[keys]:
                    yield self.save_file(base_dir=u4Ts.config['filePathFormat'], fileobj=fileobj, is_image=False)




import logging
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    settings = {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'cookie_secret': 'bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=',
        # 'xsrf_cookies': False,
        'login_url': '/login',
        'debug': True,
    }
    app = tornado.web.Application(
        ui_methods=ui_methods,
        handlers=[
            (r'/', IndexHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            # (r'/user/admin', IndexHandler),
            (r'/user/(?P<types>\w+)/(?P<page>\d+).html', UrlHandler),
            (r'/article/edit/(?P<id>\d+).html', ArticleEditHandler),
            (r'/article/(?P<type>\w+)/?(?P<page>\d+)?.html', ArticleHandler),
            (r'/category/(?P<type>\w+)/?(?P<page>\d+)?.html', CategoryHandler),
            (r'/tag/(?P<type>.*)/+(?P<page>\d+)?.html', TagHandler),
            (r'/ajax/(?P<types>\w+)', AjaxHandler),
            (r'/links/(?P<type>\w+)/?(?P<page>\d+)?.html', LinksHandler),
            (r'/desc/(?P<type>\w+).html', DescriptionHandler),
            (r'/multi-delete/(?P<types>\w+).html', MultiDeleteHandler),

            # ueditor
            (r'/upload', UploadHandler),
            # (r'/ueditor', UeditorHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
            (r'/upload/(.*)', tornado.web.StaticFileHandler, {'path':'upload'}),
        ], **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
