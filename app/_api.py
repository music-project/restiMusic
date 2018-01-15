# -*- coding=UTF-8 -*-

from flask import Flask
from flask import request
import json
from spider.qqmusic import search


app = Flask(__name__)

@app.route('/test/test11/', methods=['GET'])
def test():
    return "just test"


@app.route('/api/search/', methods=['POST'])
def searchsong():
    """
    :function:  search songs
    :args:      none
    :rv         qqmusic spider function return value

    根据搜索词查询相关歌曲
    """
    if request.method == 'POST':
        page = request.form.get('page')
        word = request.form.get('word')

        info = eval(search(page, word))
        keylist1 = ['code', 'message', 'notice', 'subcode', 'time', 'tips']
        for keyword in keylist1:
            info.pop(keyword)
        keylist2 = ['priority', 'qc', 'semantic', '']

        print info
        return "test"


if __name__ == '__main__':
    app.run(debug=True)
