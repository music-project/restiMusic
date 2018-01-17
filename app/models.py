# -*- coding=UTF-8 -*-
import os
from flask_sqlalchemy import SQLAlchemy
from app import app

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy(app)

class Music(db.Model):
    __tablename__   = 'music_info'
    music_id        = db.Column(db.String(20), primary_key=True, index=True, nullable=False)    #歌曲ID
    album_id        = db.Column(db.String(20))                      #歌曲所在专辑ID
    name            = db.Column(db.String(20))                      #歌曲名字
    style           = db.Column(db.String(50))                      #歌曲流派
    year            = db.Column(db.Date)                            #歌曲年代
    singer          = db.Column(db.String(20))                      #歌手
    language        = db.Column(db.String(20))                      #语种

    def __repr__(self):
        return '<Music %r>' % self.music_id

class Comment(db.Model):
    __tablename__   = 'comment_list'
    comment_id      = db.Column(db.String(20), primary_key=True, nullable=False)    #评论ID
    commened_id     = db.Column(db.String(20), nullable=False)                      #被评论人ID
    commening_id    = db.Column(db.String(20), nullable=False, index=True)          #评论人ID
    time            = db.Column(db.DateTime, nullable=False)                        #评论时间
    comment_info    = db.Column(db.String(512))                                     #评论内容

    def __repr__(self):
        return '<Comment %r>' % self.comment_id

class User(db.Model):
    __tablename__   = 'user_info'
    user_id         = db.Column(db.String(20), primary_key=True, nullable=False)    #用户ID
    username        = db.Column(db.String(20), nullable=False)                      #用户昵称
    password        = db.Column(db.String(40), nullable=False)                      #用户密码
    follower_num    = db.Column(db.Integer)                                          #关注数
    follower_list   = db.Column(db.String(2048))                                    #关注列表
    followed_num    = db.Column(db.Integer)                                         #粉丝数
    followed_list   = db.Column(db.String(2048))                                    #粉丝列表

    def __repr__(self):
        return '<User %r>' % self.user_id

class Upload(db.Model):
    __tablename__   = 'upload_info'
    id      = db.Column(db.String(20), primary_key=True, nullable=False)    #
    uuid            = db.Column(db.String(20), nullable=False)                      #上传者用户ID
    usid            = db.Column(db.String(20), nullable=False)                      #被上传的歌曲ID
    utime           = db.Column(db.DateTime, nullable=False)                        #上传时间

    def __repr__(self):
        return '<upload_id %r>' % self.upload_id

class Collect(db.Model):
    __tablename__   = 'collect_info'
    id      = db.Column(db.String(20), primary_key=True, nullable=False)     #
    cuid        = db.Column(db.String(20), nullable=False)                      #收藏者用户ID
    csid        = db.Column(db.String(20), nullable=False)                      #被收藏的歌曲ID
    ctime       = db.Column(db.DateTime, nullable=False)                        #收藏时间

    def __repr__(self):
        return '<collect_info %r>' % self.collect_info

if __name__ == "__main__":
    db.create_all()