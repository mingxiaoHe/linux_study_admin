#!

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_, or_
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from conf.settings import SQLALCHEMY_DATABASE_URI
from modules.models import Category, Links, User, Role, Article, Description, Tag
from modules.common import turn_bytes_to_str, get_datetime


class SqlHelper(object):
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.session = Session()

    def category(self):
        """
        返回所有分类的列表，类似 ['shell', 'mysql', 'python']
        :return: 返回分类
        """
        return self.session.query(Category).all()
        # return self.session.query(Category.name).all()

    def get_category_info_byid(self, id):
        return self.session.query(Category).filter(Category.id == id).first()

    def get_link_info_byid(self, id):
        return self.session.query(Links).filter(Links.id == id).first()

    def get_tag_info_byid(self, id):
        return self.session.query(Tag).filter(Tag.id == id).first()

    def get_description_byid(self, id):
        return self.session.query(Description).filter(Description.id == id).first()

    def get_category_count(self):
        return self.session.query(Category).count()

    def get_tag_count(self):
        return self.session.query(Tag).count()

    def get_description(self):
        return self.session.query(Description.content).order_by(Description.pub_date.asc()).all()

    def get_all_links(self):
        return self.session.query(Links).all()

    def get_links_count(self):
        return self.session.query(Links).count()

    def regist(self, username, password, email, role='ordinary'):
        """
        注册用户，从首页注册的都是普通用户，后台注册可以指定是什么用户
        :return:
        """
        try:
            user = User(username=username, password=password, email=email, create_date=get_datetime())
            role_obj = self.session.query(Role).filter(Role.name == role).first()
            role_list = []
            if role_obj is not None:
                role = role_obj
                role_list.append(role)
            else:
                role = Role()
                role.name = role
                role_list.append(role)
                self.session.add(role)
                self.session.commit()


            user.roles = role_list
            self.session.add(user)
            self.session.commit()
            return True
        except Exception as e:
            return False


    def change_user_email(self, username, email):
        try:
            self.session.query(User).filter(User.username == username).update({"email": email})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_user_passwd(self, username, password):
        try:
            self.session.query(User).filter(User.username == username).update({"password": password})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_user_passwd_byid(self, id, password):
        try:
            self.session.query(User).filter(User.id == id).update({"password": password})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def get_user_info(self, username):
        """
        返回用户信息
        :param username: 传入用户名
        :return:
        """
        return self.session.query(User).filter(User.username == username).first()

    def get_user_info_byid(self, id):
        """
        返回用户信息
        :param username: 传入用户名
        :return:
        """
        return self.session.query(User).filter(User.id == id).first()

    def get_category_articles(self, category):
        """
        返回当前分类下的文章信息
        :param category:
        :return:
        """
        return self.session.query(Category).filter(Category.name == category).first()

    def get_category_articles_by_basename(self, basename):
        return self.session.query(Category).filter(Category.basename == basename).first()

    def get_tag_articles_by_tagname(self, tagname):
        return self.session.query(Tag).filter(Tag.name == tagname).scalar()

    def get_article_byid(self, id):
        return self.session.query(Article).filter(Article.id == id).first()

    def get_category_info_by_basename(self, basename):
        return self.session.query(Category).filter(Category.basename == basename).first()

    def get_tag_info_by_tagname(self, name):
        return self.session.query(Tag).filter(Tag.name == name).first()

    def get_description(self):
        return self.session.query(Description).all()

    def get_category_articles_count(self, category_id):
        return self.session.query(Article).filter(Article.category_id == category_id).count()

    def get_tag_articles_count(self, tag_id):
        return len(self.session.query(Tag).filter(Tag.id == tag_id).scalar().articles)

    def get_articles_count(self):
        return self.session.query(Article).count()

    def get_recent_article(self):
        return self.session.query(Article).order_by(Article.pub_date.asc()).all()

    def get_most_click_articles(self):
        return self.session.query(Article).order_by(Article.click_count.desc()).all()

    def add_article_click_count(self, article_id):
        self.session.query(Article).filter(Article.id == article_id).update(
            {"click_count": Article.click_count + 1})
        self.session.commit()

    def get_admins_info(self):
        return self.session.query(Role).filter(Role.name == 'admin').first()

    def get_ordinary_info(self):
        return self.session.query(Role).filter(Role.name == 'ordinary').first()

    def set_user_info(self, id, username, role, email):
        try:

            user = self.session.query(User).filter(User.id == id).one()
            user.username = username
            user.email = email
            role_list = user.roles
            role_list.clear()  # 清空当前用户权限
            self.session.commit()

            role_obj = self.session.query(Role).filter(Role.name == role).one()
            role_id = role_obj.id
            # 手动更新权限
            sql = "INSERT INTO useridToRoleid (userid, roleid) VALUES (%s, %s)" % (id, role_id)
            self.engine.execute(sql)

            # user.roles = [Role(name=role)]
            return True

        except IntegrityError as e:
            return False

    def delete_user_byid(self, id):
        try:
            user_obj = self.session.query(User).filter(User.id == id).first()
            self.session.delete(user_obj)
            self.session.commit()
            return True
        except Exception as e:
            return False

    def get_all_article(self):
        return self.session.query(Article).all()

    def get_all_admins(self):
        return self.session.query(Role).filter(Role.name == 'admin').scalar()
        # return self.session.query(Role).filter(Role.name == 'admin').all()

    def get_all_admins_count(self):
        return len(self.session.query(Role).filter(Role.name == 'admin').scalar().users)

    def get_all_ordinaries(self):
        return self.session.query(Role).filter(Role.name == 'ordinary').scalar()

    def get_all_ordinaries_count(self):
        return len(self.session.query(Role).filter(Role.name == 'ordinary').scalar().users)

    def get_all_category(self):
        return self.session.query(Category).all()

    def add_article(self, title, description, category, tags, content, username):
        try:
            username = turn_bytes_to_str(username)
            now_time = get_datetime()

            category_obj = self.session.query(Category).filter(Category.name == category).first()
            user_obj = self.session.query(User).filter(User.username == username).first()

            article = Article(
                title=title,
                description=description,
                content=content,
                user_id=user_obj.id,
                category_id=category_obj.id,
                pub_date=now_time,
                last_modify_date=now_time,
            )

            # 标签名重复不添加，不重复添加
            tag_list = []
            for tmp in tags:
                tag_obj = self.session.query(Tag).filter(Tag.name == tmp).first()
                if tag_obj is not None:  # 标签重复,不添加，获取标签对象
                    tag = tag_obj
                    tag_list.append(tag)
                    # print('标签重复，不添加')
                else:  # 标签为新标签，先创建新标签
                    tag = Tag()
                    tag.name = tmp
                    tag.pub_date = now_time
                    tag_list.append(tag)
                    self.session.add(tag)
                    self.session.commit()

            article.tags = tag_list
            self.session.add(article)
            self.session.commit()
            return article
        except Exception as e:
            return False

    def update_article(self, id, title, description, category, tags, content):
        try:
            # username = turn_bytes_to_str(username)
            now_time = get_datetime()

            category_obj = self.session.query(Category).filter(Category.name == category).first()
            # user_obj = self.session.query(User).filter(User.username == username).first()

            self.session.query(Article).filter(Article.id == id).update({
                "title": title,
                "description": description,
                "content": content,
                "category_id": category_obj.id,
                "last_modify_date": now_time,
            })

            self.session.commit()

            tag_list = []
            for tmp in tags:
                tag_obj = self.session.query(Tag).filter(Tag.name == tmp).first()
                if tag_obj is not None:  # 标签重复,不添加，获取标签对象
                    tag = tag_obj
                    tag_list.append(tag)
                    # print('标签重复，不添加')
                else:  # 标签为新标签，先创建新标签
                    # print(tmp,"即将被添加")
                    tag = Tag()
                    tag.name = tmp
                    tag_list.append(tag)
                    self.session.add(tag)
                    self.session.commit()
            article = self.session.query(Article).filter(Article.id == id).first()
            article.tags = tag_list
            self.session.add(article)
            self.session.commit()
            return article
        except Exception as e:
            return False

    def get_tag_list(self):
        return self.session.query(Tag).all()

    def delete_users(self, users_id):
        try:
            # 删除用户会删除用户收藏文章，角色信息，但不会删除用户文章，文章作者显示未知
            for user in self.session.query(User).filter(User.id.in_(users_id)).all():
                # user.collections = []
                # self.session.commit()

                # 当前用户收藏的文章
                # collected_articles = self.session.query(User).filter(User.id==user.id).scalar().collections
                # print(collected_articles)
                user.collections.clear()
                self.session.delete(user)
                self.session.commit()

                return True
        except Exception as e:
            return False

    def delete_tags(self, tags_list):
        # 删除标签，不删除标签下的文章
        print(tags_list)
        try:
            for tag in self.session.query(Tag).filter(Tag.id.in_(tags_list)).all():
                tag.articles.clear()
                self.session.delete(tag)
                self.session.commit()
            return True
        except Exception as e:
            return False

    def delete_links(self, link_id_list):
        try:
            self.session.query(Links).filter(Links.id.in_(link_id_list)).delete(synchronize_session=False)
            self.session.commit()
            return True
        except Exception as e:
            return False


    def delete_categories(self, category_list):
        # 删除分类名，不删除分类下的文章
        try:
            for category in self.session.query(Category).filter(Category.id.in_(category_list)).all():
                category.articles.clear()
                self.session.delete(category)
                self.session.commit()
            return True
        except Exception as e:
            return False


    def delete_articles(self, article_list):
        # 删除文章
        try:
            for article in self.session.query(Article).filter(Article.id.in_(article_list)).all():
                self.session.delete(article)
                self.session.commit()
            return True
        except Exception as e:
            return False

    def change_category(self, id, category_name, category_basename):
        try:
            self.session.query(Category).filter(Category.id == id).update(
                {"name": category_name, "basename": category_basename, "pub_date": get_datetime()})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_link(self, id, link_name, link_url):
        try:
            self.session.query(Links).filter(Links.id == id).update(
                {"name": link_name, "callback_url": link_url, "pub_date": get_datetime()})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_tag(self, id, tag_name):
        print(tag_name)
        try:
            self.session.query(Tag).filter(Tag.id == id).update(
                {"name": tag_name, "pub_date": get_datetime()})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_description(self, id, content):
        try:
            self.session.query(Description).filter(Description.id == id).update(
                {"content": content, "pub_date": get_datetime()})
            self.session.commit()
            return True
        except Exception as e:
            return False

    def add_category(self, name, basename):
        try:
            category = Category(name=name, basename=basename, pub_date=get_datetime())
            self.session.add(category)
            self.session.commit()
            return True
        except Exception as e:
            return False

    def add_link(self, name, callback_url):
        try:
            link = Links(name=name, callback_url=callback_url, pub_date=get_datetime())
            self.session.add(link)
            self.session.commit()
            return True
        except Exception as e:
            return False

    def __del__(self):
        self.session.close()

