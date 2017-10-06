# -*- coding:utf-8 -*-

class decisionnode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        """
        :param col: 待检验的判断条件所对应的列索引值
        :param value: 对应于为了使结果为true，当前列必须匹配的值
        :param results: 字典，保存针对于当前分支的结果。除叶节点外，其他节点该值为None
        :param tb: 指向结果为true时的孩子节点
        :param fb: 指向结果为false时的孩子节点
        """
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


def divideset(rows, column, value):
    """
    在某一列上对数据集进行拆分，能够处理数值型数据或名词性数据
    :param rows: 当前数据集
    :param column: 拆分列（拆分特征对应的索引）
    :param value: 拆分阈值
    :return: 拆分好的两个数据子集
    """
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row : row[column] >= value
    else:
        split_function = lambda row : row[column] == value

    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1, set2)


def uniquecounts(rows):
    """
    对数据集的结果进行计数
    :param rows: 当前数据集
    :return: 返回一个字典，包含了每一项结果出现的次数
    """
    results = {}
    for row in rows:
        r = row[-1]
        if r not in results:
            results[r] = 0
        results[r] += 1
    return results


def giniImpurity(rows):
    """
    评价指标1：gini系数，pi*(1-pi)（分类问题）
    :param rows:
    :return:
    """
    counts = uniquecounts(rows)
    tmp = 0
    for i in counts:
        p = float(counts[i]) / len(rows)
        tmp += p * (1 - p)
    return tmp


def entropy(rows):
    """
    评价指标2：熵，-pi*lnpi（分类问题）
    :param rows:
    :return:
    """
    from math import log
    counts = uniquecounts(rows)
    tmp = 0
    for i in counts:
        p = float(counts[i]) / len(rows)
        tmp += (-p * log(p))
    return tmp


def variance(rows):
    """
    评价指标3：方差（数值型问题）其实cart树用的是平方误差。
    偏低的方差代表数字彼此都非常接近，偏高的方差则意味着数字分散得很开。
    :param rows:
    :return:
    """
    if len(rows) == 0:
        return 0
    data = [float(row[-1]) for row in rows]
    mean = sum(data) / len(data)
    variance = sum([(d - mean) ** 2 for d in data]) / len(data)
    return  variance


def buildTree(rows, scoref=entropy):
    """
    建树
    :param rows:
    :param scoref: 度量标准
    :return:
    """
    if len(rows) == 0: return decisionnode()
    current_score = scoref(rows)
    best_gain = 0.0
    best_criteria = None
    best_sets = None
    # 寻找最佳分割点（特征，阈值）
    for col in range(0, len(rows[0]) - 1):
        column_values = {}
        # 统计每一个特征的不同特征值
        for row in rows:
            column_values[row[col]] = 1
        # 寻找当前特征的最佳阈值
        for value in column_values:
            (set1, set2) = divideset(rows, col, value)
            p = float(len(set1)) / len(rows)
            gain = current_score - p * scoref(set1) - (1 - p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)
    # 递归创建分支
    if best_gain > 0:
        trueBranch = buildTree(best_sets[0])
        falseBranch = buildTree(best_sets[1])
        return decisionnode(col=best_criteria[0], value=best_criteria[1],
                            tb = trueBranch, fb = falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))


def classify(observation, tree):
    """
    对新数据进行预测
    :param observation: 一个新的观测数据
    :param tree: 决策树模型
    :return: 预测结果
    """
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(observation, branch)


def mdclassify(observation, tree):
    """
    对带有缺失项的数据进行预测。
    :param observation:
    :param tree:
    :return:
    """
    if tree.results != None:
        return  tree.results
    else:
        v = observation[tree.col]
        if v == None:
            tr, fr = mdclassify(observation, tree.tb), mdclassify(observation, tree.fb)
            tcount = sum(tr.values())
            fcount = sum(fr.values())
            tw = float(tcount) / (tcount + fcount)
            fw = float(fcount) / (tcount + fcount)
            result = {}
            for k, v in tr.items():
                result[k] = v * tw
            for k, v in fr.items():
                if k not in result:
                    result[k] = 0
                result[k] += v * fw
            return  result
        else:
            if isinstance(v, int) or isinstance(v, float):
                if v >= tree.value: branch = tree.tb
                else: branch = tree.fb
            else:
                if v == tree.value: branch = tree.tb
                else: branch = tree.fb
            return mdclassify(observation, branch)


def prune(tree, mingain):
    """
    剪枝的过程就是对具有相同父节点的一组节点进行检查，
    判断如果将其合并，熵的增加量是否会小于某个阈值。
    :param tree: 当前模型
    :param mingain: 最小收益阈值
    :return:
    """
    if tree.tb.results == None:
        prune(tree.tb, mingain)
    if tree.fb.results == None:
        prune(tree.fb, mingain)

    if tree.tb.results != None and tree.fb.results != None:
        tb, fb = [], []
        for v, c in tree.tb.results.items():
            tb += [[v]] * c
        for v, c in tree.fb.results.items():
            fb += [[v]] * c
        l1 = len(tree.tb.results)
        l2 = len(tree.fb.results)
        total = l1 + l2
        delta = entropy(tb + fb) - (l1 / total * entropy(tb) + l2 / total * entropy(fb))

        if delta < mingain:
            # 合并分支到父节点
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb + fb)


def printTree(tree, indent=''):
    # 判断当前节点是否是叶子节点
    if tree.results != None:
        print str(tree.results)
    else:
        print str(tree.col) + ':' + str(tree.value) + '? '
        # 打印分支
        print indent + 'T->',
        printTree(tree.tb, indent + '  ')
        print indent + 'F->',
        printTree(tree.fb, indent + '  ')


if __name__ == '__main__':
    # 数据格式（来源网站，位置，是否阅读过FAQ，注册前浏览网页的数量，选择的服务类型(预测目标)）
    my_data=[['slashdot','USA','yes',18,'None'],
            ['google','France','yes',23,'Premium'],
            ['digg','USA','yes',24,'Basic'],
            ['kiwitobes','France','yes',23,'Basic'],
            ['google','UK','no',21,'Premium'],
            ['(direct)','New Zealand','no',12,'None'],
            ['(direct)','UK','no',21,'Basic'],
            ['google','USA','no',24,'Premium'],
            ['slashdot','France','yes',19,'None'],
            ['digg','USA','no',18,'None'],
            ['google','UK','no',18,'None'],
            ['kiwitobes','UK','no',19,'None'],
            ['digg','New Zealand','yes',12,'Basic'],
            ['slashdot','UK','no',21,'None'],
            ['google','UK','yes',18,'Basic'],
            ['kiwitobes','France','yes',19,'Basic']]

    tree = buildTree(my_data, entropy)
    printTree(tree)
    print classify(['(direct)', 'USA', 'yes', 5], tree)
    prune(tree, 0.6)
    printTree(tree)
    print mdclassify(['google', None, 'yes', None], tree)
    print mdclassify(['google', 'France', None, None], tree)

