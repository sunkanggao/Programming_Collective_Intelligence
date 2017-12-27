# -*- coding:utf-8 -*-
import math
from optimization import randomoptimize, annealingoptimize, geneticoptimize
from PIL import Image, ImageDraw

people=['Charlie','Augustus','Veruca','Violet','Mike','Joe','Willy','Miranda']

links=[('Augustus', 'Willy'),
       ('Mike', 'Joe'),
       ('Miranda', 'Mike'),
       ('Violet', 'Augustus'),
       ('Miranda', 'Willy'),
       ('Charlie', 'Mike'),
       ('Veruca', 'Joe'),
       ('Miranda', 'Augustus'),
       ('Willy', 'Augustus'),
       ('Joe', 'Charlie'),
       ('Veruca', 'Augustus'),
       ('Miranda', 'Joe')]


# 交叉线损失函数（增加了节点距离损失）
def crosscount(v):
    # 将数字序列转换成一个person: (x,y)的字典
    loc = dict([(people[i], (v[2*i], v[2*i+1])) for i in range(len(people))])
    total = 0

    # 遍历每一对线（交叉线损失）
    for i in range(len(links)):
        for j in range(i+1, len(links)):
            # 获取坐标位置
            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

            # 如果den=0，则两线平行
            if den == 0: continue

            # 否则，ua与ub就是两条交叉线的分数值
            ua = 1.0 * ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = 1.0 * ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

            # 如果两条线的分数值介于0和1之间，则两条线彼此交叉
            if ua > 0 and ua < 1 and ub >0 and ub < 1:
                total += 1

    # 遍历每一对点（节点间距离损失）
    for i in range(len(people)):
        for j in range(i+1, len(people)):
            # 获得两个节点的位置
            (x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]

            # 计算两点之间的距离
            dist = math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))
            # 对间距小于50个像素的结点进行判罚
            if dist < 50:
                total += (1.0 - (dist / 50.0))

    return total


def drawnetwork(sol):
    # 建立image对象
    img = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 建立标志位置信息的字典
    pos = dict([(people[i], (sol[i*2], sol[i*2+1])) for i in range(len(people))])

    # 绘制连线
    for (a, b) in links:
        draw.line((pos[a], pos[b]), fill=(255, 0, 0))

    # 绘制代表人的节点
    for n, p in pos.items():
        draw.text(p, n, (0, 0, 0))

    img.show()


if __name__ == '__main__':
    domain = [(10, 370)] * (len(people) * 2)
    # sol = randomoptimize(domain, crosscount)
    # sol = annealingoptimize(domain, crosscount, step=50, cool=0.99)
    sol = geneticoptimize(domain, crosscount)
    print crosscount(sol), sol
    drawnetwork(sol)
