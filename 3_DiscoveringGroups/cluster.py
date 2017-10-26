# -*- coding:utf-8 -*-

from PIL import Image, ImageDraw
import random


def readFile(filename):
    lines = [line for line in file(filename)]
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data


from math import sqrt

# 一些博客比其他博客包含更多的文章条目，或者文章条目的长度比其他博客更长，
# 这样会导致这些博客在总体上比其他博客包含更多词汇。皮尔逊相关度可以纠正这一问题，
# 因为它判断的其实是两组数据与某条直线的拟合程度。
def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)
    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])
    num = pSum - sum1 * sum2 / len(v1)
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
    if den == 0:
        return 0
    return 1.0 - num / den


class biCluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hCluster(rows, distance=pearson):
    distances = {}
    currentClustID = -1

    clust = [biCluster(rows[i], id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestPair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)
        # 遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                if(clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
                d = distances[(clust[i].id, clust[j].id)]
                if d < closest:
                    closest = d
                    lowestPair = (i, j)
        # 计算两个聚类的平均值
        mergevec = [(clust[lowestPair[0]].vec[i] + clust[lowestPair[1]].vec[i]) / 2.0
                    for i in range(len(clust[0].vec))]
        # 建立新的聚类
        newCluster = biCluster(mergevec, left=clust[lowestPair[0]], right=clust[lowestPair[1]],
                               distance=closest, id=currentClustID)
        # 不在原始集合中的聚类，其id为负数
        currentClustID -= 1
        del clust[lowestPair[1]]
        del clust[lowestPair[0]]
        clust.append(newCluster)

    return clust[0]


def printClust(clust, labels=None, n=0):
    # 利用缩进来建立层级布局
    for i in range(n):
        print ' ',
    if clust.id < 0:
        # 负数标记代表这是一个分支
        print '_'
    else:
        # 正数标记代表这是一个叶节点
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]

    if clust.left != None:
        printClust(clust.left, labels=labels, n=n+1)
    if clust.left != None:
        printClust(clust.right, labels=labels, n=n+1)


def getHeight(clust):
    if clust.left == None and clust.right == None:
        return 1
    return getHeight(clust.left) + getHeight(clust.right)


def getDepth(clust):
    if clust.left == None and clust.right == None:
        return 0
    return max(getDepth(clust.left), getDepth(clust.right)) + clust.distance


def drawdendrogrom(clust, labels, jpeg='clusters.jpg'):
    h = getHeight(clust) * 20
    w = 1200
    depth = getDepth(clust)
    scaling = float(w - 150) / depth
    # 新创建一个白色背景的图片
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))
    # 画第一个节点
    drawNode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawNode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getHeight(clust.left) * 20
        h2 = getHeight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # 线的长度
        l1 = clust.distance * scaling
        # 聚类到其子节点的垂直线
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))
        # 连接左侧节点的水平线
        draw.line((x, top + h1 / 2, x + l1, top + h1 / 2), fill=(255, 0, 0))
        # 连接右侧节点的水平线
        draw.line((x, bottom - h2 / 2, x + l1, bottom - h2 / 2), fill=(255, 0, 0))

        drawNode(draw, clust.left, x + l1, top + h1 / 2, scaling, labels)
        drawNode(draw, clust.right, x + l1, bottom - h2 / 2, scaling, labels)
    else:
        # 如果这是一个叶节点，则绘制节点标签
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


def rotateMatrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata


def kCluster(rows, distance=pearson, k=4):
    # 确定每个点的最小值和最大值
    ranges = [(min(row[i] for row in rows), max(row[i] for row in rows))
              for i in range(len(rows[0]))]
    # 随机创建k个中心点
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)]

    bestmatches, lastMatches = None, None
    for t in range(100):
        print 'Iteration %d' % t
        bestmatches = [[] for i in range(k)]
        # 在每一行中寻找距离最近的中心点
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)
        # 如果结果与上一次相同，则整个过程结束
        if bestmatches == lastMatches:
            break
        lastMatches = bestmatches
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
                clusters[i] = avgs
    return bestmatches


# Jaccard相似度
def tanamoto(v1, v2):
    c1, c2, shr = 0, 0, 0
    for i in range(len(v1)):
        if v1[i] != 0:
            c1 += 1
        if v2[i] != 0:
            c2 += 1
        if v1[i] != 0 and v2[i] != 0:
            shr += 1
    return 1.0 - (float(shr) / (c1 + c2 - shr))


# MDS降维
def MDS(data, distance=pearson, rate=0.01):
    n = len(data)
    # 每一对数据项之间的真实距离
    realdist = [[distance(data[i], data[j]) for j in range(n)] for i in range(n)]
    outersum = 0.0
    # 随机初始化节点在二维空间中的位置
    loc = [[random.random(), random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]

    lasterror = None
    for m in range(0, 1000):
        # 寻找投影后的距离
        for i in range(n):
            for j in range(n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2)
                                           for x in range(len(loc[i]))]))
        # 移动节点
        grad = [[0.0, 0.0] for i in range(n)]

        totalerror = 0
        for k in range(n):
            for j in range(n):
                if j == k: continue
                # 误差值等于目标距离与当前距离之差的百分比
                errorterm = (fakedist[j][k] - realdist[j][k]) / realdist[j][k]
                # 每一个节点都需要根据误差的多少，按比例移离或移向其他节点
                grad[k][0] += ((loc[k][0] - loc[j][0]) / fakedist[j][k]) * errorterm
                grad[k][1] += ((loc[k][1] - loc[j][1]) / fakedist[j][k]) * errorterm

                # 记录总误差
                totalerror += abs(errorterm)
        print totalerror
        # 如果节点移动之后的情况变得更糟，则程序结束
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror

        # 根据rate参数与grad值相乘的结果，移动每一个节点
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]
    return loc


def draw2d(data, labels, jpeg='mds2d.jpg'):
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    img.save(jpeg, 'JPEG')




if __name__ == '__main__':
    blogNames, words, data = readFile('blogdata.txt')

    # 对博客进行层次聚类
    # clust = hCluster(data)
    # printClust(clust, labels=blogNames)
    # drawdendrogrom(clust, blogNames, jpeg='blogclust.jpg')

    # 对单词进行层次聚类
    # rdata = rotateMatrix(data)
    # wordClust = hCluster(rdata)
    # drawdendrogrom(wordClust, labels=words, jpeg='wordclust.jpg')

    # KMeans聚类
    # kClust = kCluster(data, k = 10)
    # for r in kClust[0]:
    #     print blogNames[r]

    # wants, people, data = readFile('zebo.txt')
    # clust = hCluster(data, distance=tanamoto)
    # drawdendrogrom(clust, wants)

    # MDS降维
    coords = MDS(data)
    draw2d(coords, blogNames, jpeg='blogs2d.jpg')
