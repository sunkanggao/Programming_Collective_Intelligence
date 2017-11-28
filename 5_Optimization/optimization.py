# -*- coding:utf-8 -*-

import time
import random
import math

"""
为Glass一家找到最好的旅行安排方案
"""

people = [('Seymour','BOS'),
          ('Franny','DAL'),
          ('Zooey','CAK'),
          ('Walt','MIA'),
          ('Buddy','ORD'),
          ('Les','OMA')]

# New York的LaGuardia机场
destination = 'LGA'

flights = {}
for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # 将航班详情添加到航班列表中
    flights[(origin, dest)].append((depart, arrive, int(price)))


# 计算某个给定时间在一天中的分钟数
def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


# 打印时间表
def printshedule(r):
    for d in range(len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]
        ret = flights[(destination, origin)][r[2 * d + 1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % \
              (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2])


# 成本函数，sol是一个数组，记录一个解决方案（每个人的往程航班序号和返程航班序号），大小为人数的两倍
def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol) / 2):
        # 得到往程航班和返程航班
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]

        # 总价格等于所有往程航班和返程航班价格之和
        totalprice += outbound[2]
        totalprice += returnf[2]

        # 记录最晚到达时间和最早离开时间
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):
            earliestdep = getminutes(returnf[0])

    # 每个人必须在机场等待直到最后一个人到达为止
    # 他们也必须相同时间到达，并等候他们的返程航班
    totalwait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # 是否要多付一天汽车租用费用
    if latestarrival < earliestdep: totalprice += 50

    return totalprice + totalwait


# 随机搜索
def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    for i in range(1000):
        # 创建一个随机解
        r = [random.randint(domain[j][0], domain[j][1]) for j in range(len(domain))]

        # 得到成本
        cost = costf(r)
        if cost < best:
            best =cost
            bestr = r
    return bestr


# 爬山法
def hillclimb(domain, costf):
    # 创建一个随机解
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    # 主循环
    while 1:
        # 创建相邻解的列表
        neighbors = []
        for j in range(len(domain)):
            # 在每个方向上相对于原值偏离一点
            if sol[j] > domain[j][0]:
                neighbors.append(sol[:j] + [sol[j] - 1] + sol[j+1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[:j] + [sol[j] + 1] + sol[j+1:])

        # 在相邻解中寻找最优解
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
        if best == current:
            break

    return sol


# 模拟退火算法
# 在某些情况下，得到一个更优解之前转向一个更差的解是很有必要的。模拟退火算法之所以管用，不仅因为它总是会接受一个
# 更优的解，而且还因为它在退火过程的开始阶段会接受表现较差的解。随着退火过程的不断进行，算法越来越不可能接受较差的
# 解，直到最后它只会接受更优的解。
def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # 随机初始化值
    vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    while T > 0.1:
        # 选择一个索引值
        i = random.randint(0, len(domain) - 1)

        # 选择一个改变索引值的方向
        dir = random.randint(-step, step)

        # 创建一个代表题解的新列表，改变其中一个值
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1]

        # 计算当前成本和新的成本
        ea = costf(vec)
        eb = costf(vecb)

        # 它是更好的解吗？
        if eb < ea or (random.random() < pow(math.e, -(eb - ea)/T)):
            vec = vecb

        # 降低温度
        T = T * cool

    return vec

# 遗传算法
def geneticoptimize(domain, costf, popsize=50, step=1, mutprob=0.2, elite=0.2, maxiter=100):
    """
    :param domain: 解向量中每个值的值域（以元组为元素的列表）
    :param costf: 损失函数
    :param popsize: 种群大小
    :param step: 变异步长
    :param mutprob: 种群新成员是由变异而非交叉得来的概率
    :param elite: 种群中被公认是最优解且被允许传入下一代的部分
    :param maxiter: 需要运行多少代
    :return: 一个最优解
    """
    # 变异操作
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[:i] + [vec[i]-step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[:i] + [vec[i]+step] + vec[i+1:]
        else:
            return vec

    # 交叉操作
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[:i] + r2[i:]

    # 构造初始种群
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    # 每一代中有多少胜出者
    topelite = int(elite * popsize)

    # 主循环
    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # 从纯粹的胜出者开始
        pop = ranked[:topelite]

        # 添加变异和交叉后胜出者
        while len(pop) < popsize:
            if random.random() < mutprob:
                # 变异
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                # 交叉
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        # 打印当前最优值
        print scores[0][0]

    return scores[0][1]

if __name__ == '__main__':
    domain = [(0, 9)] * (len(people) * 2)
    s = geneticoptimize(domain, schedulecost)
    printshedule(s)