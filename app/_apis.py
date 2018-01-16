# -*- coding=UTF-8 -*-

import os, json
from flask import Flask
from flask import request
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy


from spider.qqmusic import _search
from spider.qqmusic import _songdetail
from spider.qqmusic import _albumdetail

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
manager = Manager(app)

class Music(db.Model):
    __tablename__   = 'music_info'
    music_id        = db.Column(db.String(20), primary_key=True)    #歌曲ID
    album_id        = db.Column(db.String(20))                      #歌曲所在专辑ID
    style           = db.Column(db.String(50))                      #歌曲流派
    year            = db.Column(db.Date)                            #歌曲年代
    singer          = db.Column(db.String(20))                      #歌手
    language        = db.Column(db.String(20))                      #语种

    def __repr__(self):
        return '<Music %r>' % self.music_id


class Comment(db.Model):
    __tablename__   = 'comment_list'
    comment_id      = db.Column(db.String(20), primary_key=True)    #评论ID
    commened_id     = db.Column(db.String(20))                      #被评论人ID
    commening_id    = db.Column(db.String(20))                      #评论人ID
    time            = db.Column(db.DateTime)                        #评论时间
    comment_info    = db.Column(db.String(512))                     #评论内容

    def __repr__(self):
        return '<Comment %r>' % self.comment_id

class User(db.Model):
    __tablename__   = 'user_info'
    user_id         = db.Column(db.String(20), primary_key=True)
    username        = db.Column(db.String(20))                      #被评论人ID
    password        = db.Column(db.String(40))                      #评论人ID
    follower_num    = db.Column(db.Integer)                        #评论时间
    follower_list   = db.Column(db.String(1024))                     #评论内容
    followed_num    = db.Column(db.Integer)
    followed_list   = db.Column(db.String(1024))

    def __repr__(self):
        return '<User %r>' % self.user_id

@app.route('/test/test11/', methods=['GET'])
def test():
    teststr = {'test': 'test'}
    return json.dumps(teststr)


@app.route('/api/search/', methods=['POST'])
def searchsong():
    """
    :function:  searchsong
    :args:      none
    :rv         qqmusic spider function return value

    根据搜索词查询相关歌曲
    """

    if request.method == 'POST':
        page = request.form.get('page')
        word = request.form.get('word')

        info = eval(_search(page, word))

        val = {}
        val['song'] = info['data']['song']
        keyword = ['albumname_hilight', 'alertid', 'belongCD', 'cdIdx', 'chinesesinger', 'docid', 'grp',
                   'interval', 'isonly', 'lyric', 'lyric_hilight', 'media_mid', 'msgid', 'newStatus', 'nt',
                   'pay', 'preview', 'pubtime', 'pure', 'size128', 'size320', 'sizeape', 'sizeflac', 'sizeogg',
                   'songname_hilight', 'strMediaMid', 'stream', 'switch', 't', 'tag', 'type', 'ver', 'vid',
                   'format', 'songurl']
        for song in val['song']['list']:
            for word in keyword:
                if song.has_key(word):
                    song.pop(word)
        return json.dumps(val)


@app.route('/api/play/', methods=['POST'])
def getm4a():
    """
    :function:  getm4a
    :args:      none
    :rv         the link to song`s m4a

    根据歌曲ID返回m4a播放链接
    """
    id = request.args.get('id')
    return json.dumps(
        {'url': 'http://ws.stream.qqmusic.qq.com/C100' + id + '.m4a?fromtag=38'}
    )


@app.route('/api/songdetail/', methods=['POST'])
def songdetail():
    """
    :function:  songsdetail
    :args:      none
    :rv         song detail

    根据歌曲ID返回歌曲详情
    """
    songid = request.args.get('id')
    info = eval(_songdetail(songid))
    val = {}
    val['data'] = info['data']
    keyword = ['subtitle', 'ksong', 'genre', 'file', 'id', 'modify_stamp', 'trace', 'pay', 'label', 'version',
               'type', 'status', 'index_cd', 'data_type', 'volume', 'isonly', 'index_album', 'language',
               'url', 'interval', 'bpm', 'fnote', 'mv', 'action', 'name', 'time_public']
    for item in val['data']:
        for word in keyword:
            if item.has_key(word):
                item.pop(word)

    return json.dumps(val)


@app.route('/api/albumdetail/', methods=['POST'])
def albumdetail():
    """
    :function:  albumdetail
    :args:      none
    :rv         album detail

    根据专辑ID返回专辑详情
    """
    albumid = request.args.get('id')
    info = eval(_albumdetail(albumid))
    val = {}
    val['data'] = info['data']
    keyword = ['singermblog', 'singerid', 'color', 'singermid', 'albumTips', 'song_begin', 'company_new',
               'radio_anchor', 'id', 'desc']
    for word in keyword:
        if val['data'].has_key(word):
            val['data'].pop(word)

    keyword2 = ['sizeape', 'sizeflac', 'alertid', 'vid', 'rate', 'albumdesc', 'albummid', 'songtype',
                'stream', 'msgid', 'label', 'albumid', 'cdIdx', 'preview', 'type', 'belongCD', 'pay', 'songid',
                'size128', 'size320', 'albumname', 'songorig', 'isonly', 'songname', 'singer', 'interval',
                'songmid', 'size5_1', 'switch', 'sizeogg']
    for song in val['data']['list']:
        for word in keyword2:
            if song.has_key(word):
                song.pop(word)

    return json.dumps(val)


if __name__ == '__main__':
    manager.run()
    # app.run(debug=True)