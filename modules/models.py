#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File Name    : sb.py
# Author       : hexm
# Mail         : xiaoming.unix@gmail.com
# Created Time : 2017-03-29 20:03

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 用户id对应角色id 多对多
useridToRoleid = Table('useridToRoleid', Base.metadata,
                       Column('userid', Integer, ForeignKey('users.id')),
                       Column('roleid', Integer, ForeignKey('roles.id')),
                       )

# 角色id对应权限id 多对多
roleidToIdentityid = Table('roleidToIdentityid', Base.metadata,
                           Column('roleid', Integer, ForeignKey('roles.id')),
                           Column('identityid', Integer, ForeignKey('identities.id')),
                           )

# 文章id和标签id 多对多
articleidToTagid = Table('articleidToTagid', Base.metadata,
                         Column('articleid', Integer, ForeignKey('articles.id')),
                         Column('tagid', Integer, ForeignKey('tags.id')),
                         )

# 用户收藏的文章 多对多
useridToArticleid = Table('useridToArticleid', Base.metadata,
                          Column('userid', Integer, ForeignKey('users.id')),
                          Column('articleid', Integer, ForeignKey('articles.id')),
                          )


# 用户-->文章  一个用户收藏多个文章，一个文章被多个用户收藏，多对多关系

class User(Base):
    """
    用户表
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False, unique=True)
    create_date = Column(DateTime)

    articles = relationship('Article', backref='user')
    roles = relationship('Role', secondary=useridToRoleid, backref='users')

    collections = relationship('Article', cascade="save-update, merge", secondary=useridToArticleid, backref='users')


    def __repr__(self):
        return "<%s users.username: %s>" % (self.id, self.username)


class Role(Base):
    """
    角色表
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)

    identity = relationship('Identity', secondary=roleidToIdentityid, backref='roles')

    def __repr__(self):
        return self.name


class Identity(Base):
    """
    权限表
    """
    __tablename__ = 'identities'
    id = Column(Integer, primary_key=True)
    name = Column(String(16))

    def __repr__(self):
        return "<%s identities.name: %s>" % (self.id, self.name)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False, unique=True)
    basename = Column(String(16), nullable=False, unique=True)
    pub_date = Column(DateTime)

    articles = relationship('Article', backref='category')

    def __repr__(self):
        return "<%s categories.name: %s" % (self.id, self.name)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(300))
    content = Column(Text)
    click_count = Column(Integer, default=0)
    pub_date = Column(DateTime)
    last_modify_date = Column(DateTime)

    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    tags = relationship('Tag', cascade="save-update, merge", secondary=articleidToTagid, backref='articles')

    def __repr__(self):
        return "<%s article.name: %s>" % (self.id, self.title)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(16), unique=True)
    pub_date = Column(DateTime)

    def __repr__(self):
        return "<%s tag.name: %s>" % (self.id, self.name)


class Links(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    callback_url = Column(String(50), nullable=False)
    pub_date = Column(DateTime)

    def __repr__(self):
        return "<%s links.name: %s>" % (self.id, self.name)


class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer)
    articleid = Column(Integer)
    col_date = Column(DateTime)


class Description(Base):
    __tablename__ = "descriptions"
    id = Column(Integer, primary_key=True)
    content = Column(String(150))
    pub_date = Column(DateTime)


class Rotate(Base):
    __tablename__ = "rotates"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(200))
    pub_date = Column(DateTime)
    img_src = Column(String(200))
    article_src = Column(String(200))

    def __repr__(self):
        return "<%s rotates.name: %s" % (self.id, self.title)
