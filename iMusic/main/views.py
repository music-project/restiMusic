# coding: utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, request
from flask_cors import cross_origin

from . import api
from iMusic import db
from ..spider.qqmusic import _songdetail
from ..spider.qqmusic import _albumdetail
from ..spider.qqmusic import _search
from ..algorithm.recommender import recommender

import codecs
import json, base64, datetime
from ..models import User, Upload, Collect, Comment, Music, Follow
from flask_cors import cross_origin


def get_song_list(upload_list):
    songlist = []
    for item in upload_list:
        song = {}
        #上传表中的信息
        song['timestamp'] = item.utime.__str__()
        song['url'] = 'http://ws.stream.qqmusic.qq.com/C100' + item.usid + '.m4a?fromtag=38'

        #歌曲表中的信息
        music = Music.query.filter_by(music_id=item.usid).first()
        song['id'] = music.id
        song['music'] = music.name
        song['artist'] = music.singer

        #收藏表中的信息
        collect = Collect.query.filter_by(cuid=item.uuid, csid=item.usid).first()
        if collect is not None:
            song['is_like'] = False
        else:
            song['is_like'] = True

        #评论表中的信息
        song['comments'] = []

        #用户表中的信息
        user_info = {}
        user = User.query.filter_by(id=item.uuid).first()
        user_info['id'] = user.id
        user_info['avatar'] = user.avatar
        user_info['username'] = user.username
        user_info['twees'] = user.tweets
        user_info['is_following'] = user.is_following
        user_info['cover'] = user.cover
        user_info['bio'] = user.bio
        song['user'] = user_info

        songlist.append(song)

    return songlist


def get_singer_by_songmid(songmid):
    return  Music.query.filter_by(music_id=songmid).first().singer

def Auth2(Authorization):
    state = 502
    username, uid = base64.b64decode(Authorization.split(' ')[1]).split(':')
    # print username
    # print uid

    # 查询是否有该用户
    user = User.query.filter_by(username=username).first()
    print user
    if user is None:
        state = 401                 #未注册
    else:  # 查询密码是否正确
        state = 200             #密码错误

    return state

def Auth(Authorization):
    state = 502
    username, password = base64.b64decode(Authorization.split(' ')[1]).split(':')
    # print username
    # print password

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

@api.route('/<int:user_id>/music/', methods=['GET'])
@cross_origin(origin="*")
def get_index(user_id):
    if request.method == 'GET':
        rv = {}
        Authorization = request.headers.get('Authorization')
        state = Auth2(Authorization)
        rv['state'] = state
        rv['musics'] = []

        # 获取自己上传的音乐列表
        upload_list = Upload.query.filter_by(uuid=user_id).all()
        rv['musics'] += get_song_list(upload_list)

        # 获取自己关注的所有用户
        following_list = Follow.query.filter_by(follower_id=user_id).all()
        for follow in following_list:
            f_upload_list = Upload.query.filter_by(uuid=follow.followed_id).all()
            rv['musics'] += get_song_list(f_upload_list)

        return json.dumps(rv)

@api.route('/<int:user_id>/follower/', methods=['GET'])
@cross_origin(origin="*")
def get_follower(user_id):
    if request.method == 'GET':
        rv = {}
        Authorization = request.headers.get('Authorization')
        state = Auth2(Authorization)
        rv['state'] = state
        rv['users'] = []
        follower_list = Follow.query.filter_by(followed_id=user_id).all()
        for item in follower_list:
            u_id = item.follower_id
            u_user = User.query.filter_by(id=u_id).first()
            user_info = {}
            user_info['id']            = u_id
            user_info['avatar']        = u_user.avatar
            user_info['username']      = u_user.username
            user_info['tweets']        = list(u_user.tweets)
            user_info['is_following'] = u_user.is_following
            user_info['cover']         = u_user.cover
            user_info['bio']           = u_user.bio
            rv['users'].append(user_info)

        return json.dumps(rv)


@api.route('/<int:user_id>/following/', methods=['GET'])
@cross_origin(origin="*")
def get_following(user_id):
    if request.method == 'GET':
        rv = {}
        Authorization = request.headers.get('Authorization')
        state = Auth2(Authorization)
        rv['state'] = state
        rv['users'] = []
        following_list = Follow.query.filter_by(follower_id=user_id).all()
        for item in following_list:
            u_id = item.followed_id
            u_user = User.query.filter_by(id=u_id).first()
            user_info = {}
            user_info['id']            = u_id
            user_info['avatar']        = u_user.avatar
            user_info['username']      = u_user.username
            user_info['tweets']        = list(u_user.tweets)
            user_info['is_following'] = u_user.is_following
            user_info['cover']         = u_user.cover
            user_info['bio']           = u_user.bio
            rv['users'].append(user_info)

        return json.dumps(rv)

@api.route('/follow/', methods=['POST'])
@cross_origin(origin="*")
def follow():
    if request.method == 'POST':
        rv = {}
        Authorization = request.headers.get('Authorization')
        state = Auth2(Authorization)
        rv['state'] = state

        cname = request.json.get("cname")
        uname = request.json.get("uname")
        # 当前用户对象
        # 被关注用户对象
        c_user = User.query.filter_by(username=cname).first()
        u_user = User.query.filter_by(username=uname).first()

        # 计算当前用户的ID
        # 计算被关注用户的ID
        c_id = c_user.id
        u_id = u_user.id

        #添加关注信息
        new_follow = Follow(follower_id=c_id, followed_id=u_id)
        db.session.add(new_follow)
        db.session.commit()

        #当前用户的关注数加一
        #被关注用户的被关注数加一
        c_user.follower_num += 1
        u_user.followed_num += 1
        db.session.add(c_user)
        db.session.add(u_user)
        db.session.commit()

        return json.dumps(rv)

@api.route('/<mid>/like/', methods=['GET'])
@cross_origin(origin="*")
def like_music(mid):
    if request.method == 'GET':
        rv = {}
        Authorization = request.headers.get('Authorization')
        print "Auth" + Authorization
        state = Auth2(Authorization)
        rv['state'] = state
        username, uid = base64.b64decode(Authorization.split(' ')[1]).split(':')
        print (username, uid)
        songmid = Music.query.filter_by(id=mid).first().music_id
        item = Collect.query.filter_by(cuid=uid, csid=songmid).first()
        if item is None:
            new_like = Collect(cuid=uid, csid=songmid, ctime=datetime.datetime.now())
            db.session.add(new_like)
            db.session.commit()

        return json.dumps(rv)

@api.route('/<uid>/suggest_users/', methods=['GET'])
@cross_origin(origin="*")
def suggest(uid):
    if request.method == 'GET':
        # 歌曲评分
        path1 = "temp_music.csv"
        path2 = "temp_musicion.csv"
        path3 = "temp_tag.csv"
        f1 = codecs.open(path1, "wb", 'utf8')
        f2 = codecs.open(path2, "wb", 'utf8')
        f3 = codecs.open(path3, "wb", 'utf8')

        f1.write("UserID,MusicID,Rating\n")
        f2.write("UserID,MusicID,Rating\n")
        f1.write("UserID,TagID,Rating\n")

        collect = Collect.query.all()
        upload = Upload.query.all()
        rating = {}
        for item in collect:
            uuid = item.cuid
            songid = item.csid
            sstr = str(uuid) + "," + songid + ",5\n"
            f1.write(sstr)

            style = ""
            year = ""
            language = ""
            item = Music.query.filter_by(music_id=songid).first()
            if item is not None:
                singer = item.singer
                sstr2 = str(uuid) + "," + singer + ",5\n"
                f2.write(sstr2)

                style = item.style
                year = item.year
                language = item.language

            if uuid not in rating:
                rating[uuid] = {}
            if year not in rating[uuid]:
                rating[uuid][year] = 0
            if style not in rating[uuid]:
                rating[uuid][style] = 0
            if language not in rating[uuid]:
                rating[uuid][language] = 0
            rating[uuid][style] += 3
            rating[uuid][year] += 3
            rating[uuid][language] += 3


        for item in upload:
            uuid = item.uuid
            songid = item.usid
            sstr = str(uuid) + "," + songid + ",5\n"
            f1.write(sstr)


            style = ""
            year = ""
            language = ""
            item = Music.query.filter_by(music_id=songid).first()
            if item is not None:
                singer = item.singer
                sstr2 = str(uuid) + "," + singer + ",5\n"
                f2.write(sstr2)

                style = item.style.decode('utf-8')
                year = item.year.decode('utf-8')
                language = item.language.decode('utf-8')

            if uuid not in rating:
                rating[uuid] = {}
            if year not in rating[uuid]:
                rating[uuid][year] = 0
            if style not in rating[uuid]:
                rating[uuid][style] = 0
            if language not in rating[uuid]:
                rating[uuid][language] = 0
            rating[uuid][style] += 5
            rating[uuid][year] += 5
            rating[uuid][language] += 5

        for uuid in rating:
            for tag in rating[uuid]:
                f3.write(str(uuid) + "," + str(tag) + "," + str(rating[uuid][tag]) + "\n")
        f1.close()
        f2.close()
        f3.close()

        rec1 = recommender(path1).calcuteUserbyMusic(targetID=uid, TopN=2)
        rec2 = recommender(path2).calcuteUserbyMusic(targetID=uid, TopN=2)
        rec3 = recommender(path3).calcuteUserbyTag(targetID=uid, TopN=2)

        print rec1 + rec2 + rec3
        return "suggest"

# @api.route('/<uid>/suggest_users/', methods=['GET'])
# @cross_origin(origin="*")
# def suggest_user(uid):
#     if request.method == 'GET':
#         path = "temp.csv"
#         with open(path, "wb") as f:
#             f.write("UserID,MusicID,Rating\n")
#             collect = Collect.query.all()
#             for item in collect:
#                 uuid  = str(item.cuid)
#                 songid = item.csid
#                 sstr = uuid + "," + songid + "," +  "5\n"
#                 f.write(sstr)
#
#         rec = recommender(path)
#         print rec.calcuteUserbyMusic(targetID=uid, TopN=4)
#         return "test"
#     # return rec.calcuteUserbyMusic(targetID=uid, TopN=4)


@api.route('/<uid>/music/', methods=['POST'])
@cross_origin(origin="*")
def upload_music(uid):
    rv = {}
    if request.method == 'POST':
        #身份验证
        Authorization = request.headers.get('Authorization')
        state = Auth2(Authorization)
        music = request.args.get('music')
        artist = request.args.get('artist')

        rv['state'] = state
        rv['url'] = ""
        rv['comments'] = []
        rv['id'] = 0
        rv['is_like'] = False
        rv['timestamp'] = datetime.datetime.now().__str__()

        #根据歌曲名查找歌曲列表
        info = eval(_search('1', music))
        val = {}
        val['song'] = info['data']['song']
        # with open("temp3.txt", "wb") as f:
        #     f.write(str(val))
        #根据歌手筛选歌曲列表
        songmid = ""
        flag = False
        for song in val['song']['list']:
            if song['singer'][0]['name'].decode('utf-8') == artist:
                songmid = song['songmid']
                # print "*********" + songmid
                flag = True
                break
        if flag == False:           #找不到匹配的结果
            rv['state'] = 404
            return json.dumps(rv)
        else:                       #根据歌曲ID查找播放链接
            rv['url'] = 'http://ws.stream.qqmusic.qq.com/C100' + songmid + '.m4a?fromtag=38'

            item = Collect.query.filter_by(csid=songmid, cuid=uid).first()
            if item is None:
                rv['is_like'] = False
            else:
                rv['is_like'] = True

            comment = Comment.query.filter_by(commened_id=songmid).all()
            for item in comment:
                rv['comments'].add(item)

            date = datetime.datetime.now()
            #更新上传表
            upload = Upload(uuid=uid, usid=songmid, utime=date)
            db.session.add(upload)
            db.session.commit()
            rv['timestamp'] = date.__str__()

            #更新歌曲表
            ##根据歌曲ID查找歌曲专辑ID
            # print "songmid = " + songmid
            info = eval(_songdetail(songmid))
            # with open("temp2.txt", "wb") as f:
            #     f.write(str(info))
            albummid    = info['data'][0]['album']['mid'].decode('utf-8')

            ##根据专辑ID查找专辑详情
            # print(_albumdetail(albummid))
            info = _albumdetail(albummid)
            style       = info['data']['genre']
            year        = info['data']['aDate'].decode("utf-8")
            language    = info['data']['lan']

            new_music = Music(music_id=songmid,
                              album_id=albummid,
                              name=music,
                              style=style,
                              year=year,
                              singer=artist,
                              language=language)
            db.session.add(new_music)
            db.session.commit()

            mid = Music.query.filter_by(music_id=songmid).first().id
            rv['id'] = mid

            return json.dumps(rv)

@api.route('/user/<int:id>/', methods=['GET'])
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
            rv['user']['id']            = id

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
            new = User(username=username, password=encode_password, follower_num=0, followed_num=0)
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
    new1 = Collect(cuid="1", csid="aaa", ctime=datetime.datetime.now())
    new2 = Collect(cuid="2", csid="bbb", ctime=datetime.datetime.now())
    new3 = Collect(cuid="3", csid="ccc", ctime=datetime.datetime.now())
    new4 = Collect(cuid="4", csid="ddd", ctime=datetime.datetime.now())

    db.session.add(new1)
    db.session.add(new2)
    db.session.add(new3)
    db.session.add(new4)

    db.session.commit()


    # user = User.query.filter_by(follower_num=0).all()
    # print user[0].id
    return 'just test'
#
# class Collect(db.Model):
#     __tablename__   = 'collect_info'
#     id             = db.Column(db.Integer, primary_key=True, index=True)        #数据库id
#     cuid        = db.Column(db.Integer, nullable=False)                      #收藏者用户ID
#     csid        = db.Column(db.String(20), nullable=False)                      #被收藏的歌曲ID
#     ctime       = db.Column(db.DateTime, nullable=False)                        #收藏时间