# coding: utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, request
from flask_cors import cross_origin

from . import api
from iMusic import db
from ..spider.qqmusic import _songdetail
from ..spider.qqmusic import _albumdetail
from ..spider.qqmusic import _search

import json, base64
from ..models import User, Upload, Collect
from flask_cors import cross_origin

def Auth(Authorization):
    state = 502
    username, password = base64.b64decode(Authorization.split(' ')[1]).split(':')
    print username
    print password

    # 查询是否有该用户
    user = User.query.filter_by(username=username).first()
    print user
    if user is None:
        state = 401                 #未注册
    else:  # 查询密码是否正确
        dbpassword = User.query.filter_by(username=username).first().password
        print dbpassword
        if dbpassword == base64.b64encode(username + ':' + password):
            state = 200             #密码正确
        else:
            state = 403             #密码错误
    return state


@api.route('/user/<int:id>', methods=['GET'])
@cross_origin(origin="*")
def get_user_info(id):
    rv = {}
    if request.method == 'GET':
        Authorization = request.headers.get('Authorization')
        state = Auth(Authorization)
        rv['state'] = state
        rv['user'] = {}

        if state == 200:
            user_info = User.query.filter_by(id=id).first()
            rv['user']['avatar']        = user_info.avatar
            rv['user']['username']      = user_info.username
            rv['user']['tweets']        = list(user_info.tweets)
            rv['user']['is_following'] = user_info.is_following
            rv['user']['cover']         = user_info.cover
            rv['user']['bio']           = user_info.bio

        return json.dumps(rv)

@api.route('/following/music/', methods=['GET'])
@cross_origin(origin="*")
def following_music():
    rv = {}
    if request.method == 'GET':
        time = request.args.get('time')
        Authorization = request.headers.get('Authorization')
        state = Auth(Authorization)
        rv['state'] = state
        rv['list'] = []
        songmidlist = []
        if state != 403:
            ## 获取当前用户关注的所有用户
            username = base64.b64decode(Authorization.split(' ')[1]).split(':')[0]
            follower_list = list(User.query.filter_by(username=username).first().follower_list) #关注的人
            for uid in follower_list:
                ##  获取所有关注用户上传的音乐
                upload_list = Upload.query.filter_by(uuid=uid).all()
                for up_list in upload_list:
                    songmidlist.add(up_list.usid)

            # for sid in songmidlist:


        return json.dumps(rv)

@api.route('/token/', methods=['POST'])
@cross_origin(origin="*")
def get_token():
    if request.method == 'POST':
        rv = {}
        Authorization = request.headers.get('Authorization')
        username = base64.b64decode(Authorization.split(' ')[1]).split(':')[0]

        rv['state'] =  Auth(Authorization)
        token = ""
        if rv['state'] != 401:
            uid = User.query.filter_by(username=username).first().id
            token = base64.b64encode(username + ':' + str(uid))
        rv['token'] = token

        return json.dumps(rv)

@api.route('/user/', methods=['POST'])
@cross_origin(origin="*")
def register():
    rv = {}
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        encode_password = base64.b64encode(username + ':' + password)

        #查询该用户名是否已经存在
        user = User.query.filter_by(username=username).first()
        print(user)
        if user is None:
            new = User(username=username, password=encode_password, follower_num=0, follower_list='[]', followed_num=0,
                       followed_list='[]')
            #添加新用户
            db.session.add(new)
            db.session.commit()
            rv['state'] = 200
        else:
            rv['state'] = 502
    return json.dumps(rv)

@api.route('/', methods=['GET', 'POST'])
@cross_origin(origin="*")
def index():
    """
    form = NameForm()

    if form.validate_on_submit():  # ...
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())
    """
    teststr = {'test': 'test'}
    return json.dumps(teststr)
    # def adduser():
    #     name = raw_input('Username> ')
    #     email = raw_input('Email> ')
    #     input_password = getpass('Password> ')
    #
    #     password = base64.b64encode(input_password)
    #     new = User(name=name, email=email,
    #                password=password, role=role)
    #     db.session.add(new)
    #     db.session.commit()
    #     print "new user <{name}> created".format(name)

@api.route('/test/', methods=['GET', 'POST'])
@cross_origin(origin="*")
def test():
    teststr = {'test': 'test'}
    return json.dumps(teststr)

@api.route('/search/', methods=['POST'])
@cross_origin(origin="*")
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

@api.route('/play/', methods=['POST'])
@cross_origin(origin="*")
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

@api.route('/songdetail/', methods=['POST'])
@cross_origin(origin="*")
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

@api.route('/api/albumdetail/', methods=['POST'])
@cross_origin(origin="*")
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

@api.route('/dbtest/', methods=['GET'])
@cross_origin(orifin="*")
def dbtest():
    user = User.query.filter_by(follower_num=0).all()
    print user[0].id
    return 'just test'