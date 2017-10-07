# -*- coding:utf-8 -*-

from math import sqrt
import pprint


def sim_distance(prefs, person1, person2):
    """
    返回一个有关person1和person2的基于欧式距离的相似度评价
    :param prefs: 数据集
    :param person1:
    :param person2:
    :return:
    """
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    if len(si) == 0: return 0
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                         for item in prefs[person1] if item in prefs[person2]])
    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    """
    返回p1和p2的皮尔逊相关系数
    :param prefs:
    :param p1:
    :param p2:
    :return:
    """
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    n = len(si)
    if n == 0: return 0

    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    sun1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - sum1 * sum2 / n
    den = sqrt((sun1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    return num / den


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """
    从原始数据中返回与当前用户最为匹配的前n个用户
    :param prefs:
    :param person:
    :param n:
    :param similarity:
    :return:
    """
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0 : n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    """
    利用所有他人评价值的加权平均，为person推荐电影。
    基于用户的协同过滤。在用户量很大的系统中不适用。
    :param prefs:
    :param person:
    :param similarity:
    :return: 经过排序的物品列表
    """
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person: continue
        sim = similarity(prefs, person, other)
        if sim <= 0: continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                simSums.setdefault(item, 0)
                simSums[item] += sim
    # 建立一个归一化列表
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


def transformPrefs(prefs):
    """
    用户：电影 -> 电影：用户
    :param prefs:
    :return:
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n = 10):
    """
    计算物品之间的相似度
    :param prefs:
    :param n:
    :return: 字典，给出与这些物品最为相近的topn的其他物品
    """
    result = {}
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据集更新状态变量
        c += 1
        if c % 100 == 0: print "%d / %d" % (c, len(itemPrefs))
        # 寻找最为相近的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


def getRecommendedItems(prefs, itemMatch, user):
    """
    基于物品的协同过滤，为user推荐物品
    :param prefs:
    :param itemMatch:
    :param user:
    :return:
    """
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # 循环遍历由当前用户评分的电影
    for (item, rating) in userRatings.items():
        # 循环遍历与当前物品相近的物品
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRatings: continue
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    # 将每个合计值除以加权和，求出平均值
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


def loadMovieLens():
    """
    载入movielens数据
    :return:
    """
    movies = {}
    for line in open('u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title
    prefs = {}
    for line in open('u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


if __name__ == "__main__":
    critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
             'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
             'The Night Listener': 3.0},
             'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
              'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
              'You, Me and Dupree': 3.5},
             'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
              'Superman Returns': 3.5, 'The Night Listener': 4.0},
             'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
              'The Night Listener': 4.5, 'Superman Returns': 4.0,
              'You, Me and Dupree': 2.5},
             'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
              'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
              'You, Me and Dupree': 2.0},
             'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
              'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
             'Toby': {'Snakes on a Plane': 4.5,'You, Me and Dupree': 1.0,'Superman Returns': 4.0}}

    # pprint.pprint(critics)
    print u'=========与Toby最相似的3个用户=========='
    pprint.pprint(topMatches(critics, 'Toby', 3))
    print u'\n=============Pearson相关系数============'
    pprint.pprint(getRecommendations(critics, 'Toby'))
    print u'\n=============欧式距离=============='
    pprint.pprint(getRecommendations(critics, 'Toby', sim_distance))

    movies = transformPrefs(critics)
    print u'\n=====与Superman Returns最相似的5部电影======'
    pprint.pprint(topMatches(movies, 'Superman Returns'))
    print u'\n=====为Just My Luck推荐评论者======='
    pprint.pprint(getRecommendations(movies, 'Just My Luck'))

    itemsim = calculateSimilarItems(critics)
    print u'\n=========基于物品的推荐=========='
    pprint.pprint(getRecommendedItems(critics, itemsim, 'Toby'))

    prefs = loadMovieLens()
    print u'\n==============基于用户的推荐==============='
    pprint.pprint(getRecommendations(prefs, '87')[0 : 10])
    print u'\n==============基于物品的推荐==============='
    itemsim = calculateSimilarItems(prefs, 50)
    pprint.pprint(getRecommendedItems(prefs, itemsim, '87')[0 : 10])