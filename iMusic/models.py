# -*- coding=UTF-8 -*-
import os
from . import db

basedir = os.path.abspath(os.path.dirname(__file__))

class Music(db.Model):
    __tablename__   = 'music_info'
    id             = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)        #数据库id
    music_id        = db.Column(db.String(20))   #歌曲mID
    album_id        = db.Column(db.String(20))                      #歌曲所在专辑ID
    name            = db.Column(db.String(20))                      #歌曲名字
    style           = db.Column(db.String(50))                      #歌曲流派
    year            = db.Column(db.String(20))                      #歌曲年代
    singer          = db.Column(db.String(20))                      #歌手
    language        = db.Column(db.String(20))                      #语种

    def __repr__(self):
        return '<Music %r>' % self.id

class Comment(db.Model):
    __tablename__   = 'comment_list'
    id             = db.Column(db.Integer, primary_key=True, index=True)        #数据库id
    commened_id     = db.Column(db.String(20), nullable=False)                      #被评论歌曲ID
    commening_id    = db.Column(db.String(20), nullable=False, index=True)          #评论人ID
    time            = db.Column(db.String(40), nullable=False)                        #评论时间
    comment_info    = db.Column(db.String(512))                                     #评论内容

    def __repr__(self):
        return '<Comment %r>' % self.id

class User(db.Model):
    __tablename__   = 'user_info'
    id              = db.Column(db.Integer, primary_key=True, index=True)        #数据库id
    username        = db.Column(db.String(20), nullable=False, index=True)                      #用户昵称
    password        = db.Column(db.String(40), nullable=False)                      #用户密码
    avatar          = db.Column(db.String(50), default='https://pic3.zhimg.com/aadd7b895_xs.jpg')
    tweets          = db.Column(db.String(2048), default='')                           #
    is_following    = db.Column(db.Boolean)                                         #
    cover           = db.Column(db.String, default='https://user-images.githubusercontent.com/10671733/3508799'
                                                   '4-14e705ce-fc6d-11e7-8203-bbd045c6a3bb.jpg')
    bio             = db.Column(db.String(200), default='intro yourself')         #用户介绍
    follower_num    = db.Column(db.Integer)                                          #关注数
    follower_list   = db.Column(db.String(2048))                                    #关注列表
    followed_num    = db.Column(db.Integer)                                         #粉丝数
    followed_list   = db.Column(db.String(2048))                                    #粉丝列表

    def __repr__(self):
        return '<User %r>' % self.id

class Upload(db.Model):
    __tablename__   = 'upload_info'
    id             = db.Column(db.Integer, primary_key=True, index=True)            #数据库id
    uuid            = db.Column(db.Integer, nullable=False)                      #上传者用户ID
    usid            = db.Column(db.String(20), nullable=False)                      #被上传的歌曲ID
    utime           = db.Column(db.String(40), nullable=False)                        #上传时间

    def __repr__(self):
        return '<upload_id %r>' % self.id

class Collect(db.Model):
    __tablename__   = 'collect_info'
    id             = db.Column(db.Integer, primary_key=True, index=True)        #数据库id
    cuid        = db.Column(db.Integer, nullable=False)                      #收藏者用户ID
    csid        = db.Column(db.String(20), nullable=False)                      #被收藏的歌曲ID
    ctime       = db.Column(db.String(40), nullable=False)                        #收藏时间

    def __repr__(self):
        return '<collect_info %r>' % self.id

# python manage.py db init
# python manage.py db migrate
# python manage.py db upgrade


# autoincrement=True