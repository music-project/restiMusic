# -*- coding:utf-8 -*-
# author = oulaline

import os
import sys
import codecs
import pandas as pd
import math


class recommender(object):
    def __init__(self, path):
        self.csvpath = path  # 格式应为'UserID','MusicID','Rating', 要有列头

    def readRatingDate(self, path='../ml-1m/ratings.dat'):
        '''
        读取评分数据并存储为csv文件
        :param path:文件路径
        :return: DataFrame
        '''
        f = pd.read_table(path, sep='::', names=['UserID', 'MusicID', 'Rating', 'Timestamp'], engine='python')
        f.to_csv('../ml-1m/ratings.csv', columns=['UserID', 'MusicID', 'Rating'], index=False)
        return f

    def calcuteSimilarbyTag(self, series1, series2):
        '''
        对两用户共同评价的tag计算余弦相似度
        :param data1: 数据集1 Series
        :param data2: 数据集2 Series
        :return: 相似度
        '''
        # print series1.dtypes
        series3 = pd.merge(series1, series2, on=['TagID'])
        unionLen = len(series3)
        if unionLen == 0:
            return 0.0
        sum1 = (series3['Rating_x'] * series3['Rating_y']).sum()
        den1 = math.sqrt((series3['Rating_x'] * series3['Rating_x']).sum())
        den2 = math.sqrt((series3['Rating_y'] * series3['Rating_y']).sum())
        return sum1 / (den1 * den2)

    def calcuteSimilarbyMusic(self, series1, series2):
        '''
		根据两用户听歌的歌曲或歌手的重合度计算余弦相似度
		'''
        unionLen = len(set(series1) & set(series2))
        if unionLen == 0:
            return 0.0
        product = len(series1) * len(series2)
        similarity = unionLen / math.sqrt(product)
        return similarity

    def calcuteUserbyMusic(self, targetID=1, TopN=10):
        '''''
        计算targetID的用户与其他用户的相似度
        :return:相似度TopN的UserID
        csv表头为['UserID','MusicID','Rating']
        'MusicID'在不同的文件中既可指代歌手也可指代歌曲
        '''
        frame = pd.read_csv(self.csvpath)  # 返回数据类型： DataFrame#读取数据
        targetUser = frame[frame['UserID'] == targetID]
        # print "targetUser： \n", targetUser                        #目标用户数据
        otherUsersID = [i for i in set(frame['UserID']) if i != targetID]  # 其他用户ID
        otherUsers = [frame[frame['UserID'] == i] for i in otherUsersID]  # 其他用户数据

        # 根据music计算相似度
        similarlist = [self.calcuteSimilarbyMusic(targetUser, user) for user in otherUsers]
        similarSeries = pd.Series(similarlist, index=otherUsersID)
        return similarSeries.sort_values()[-TopN:].index

    def calcuteUserbyTag(self, targetID=1, TopN=10):
        '''
		表头为['UserID','TagID','Rating']
		'''
        frame = pd.read_csv(self.csvpath)  # 返回数据类型： DataFrame
        targetUser = frame[frame['UserID'] == targetID]
        otherUsersID = [i for i in set(frame['UserID']) if i != targetID]
        otherUsers = [frame[frame['UserID'] == i] for i in otherUsersID]

        similarlist = [self.calcuteSimilarbyTag(targetUser, user) for user in otherUsers]
        similarSeries = pd.Series(similarlist, index=otherUsersID)
        return similarSeries.sort_values()[-TopN:].index


if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = '.ml-1m/ratings.csv'
    else:
        path = sys.argv[1]

    rec = recommender(path)
    sim1 = rec.calcuteUserbyMusic(targetID=1, TopN=10)
    for si in sim1:
        print si

    path2 = '../ml-1m/tag_ratings.csv'
    rec2 = recommender(path2)
    sim2 = rec2.calcuteUserbyTag(targetID=1, TopN=10)

    print "asdasd"
    for si in sim2:
        print si