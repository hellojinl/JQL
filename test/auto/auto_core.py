#coding=utf-8

import re, os, io, sys, shutil, string, random, datetime

sys.path.append(os.getcwd() + "/../../src/")

from JQLCore import JqlItem, AgentLogTableTitles

#结果目录
RESULT_FOLDER = "auto_test_result"
#结果文件名
RESULT_FILENAME = "/_result_cmp"
#总结
SUMMARY = RESULT_FOLDER + "/summary"
#字典来源
DICTIONARY_SOURCE = "../auto_dictionary"
#查找2个字符以上的单词
WORDS_KEY = "[a-zA-Z]+[a-zA-Z]+"
#时间格式
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
#java-agent分割线
JAVA_AGENT_SPLIT_LINE = "-----------------------"
#jql关键字
JQL_KEYWORDS = r"select|from|where|order by|limit|into"
#测试结果：成功
RESULT_SUCCESS = "[ SUCCESS ]"
#测试结果：失败
RESULT_FAILURE = "[ FAILURE ]"

#生成包名的最小单词个数
MIN_PACKAGE_WORDS_COUNT = 3
#生成包名的最大单词个数
MAX_PACKAGE_WORDS_COUNT = 6
#随机生成方法个数最大值
MAX_METHOND_COUNT = 20
#随机生成方法调用最大次数
MAX_METHOND_COUNTER = 1000000
#随机生成方法调用最大时间
MAX_METHOND_TIME = 3600000

class RandomParams:
    """随机参数
    
    Attributes:
        min_unit_count -- 最小单元个数
        max_unit_count -- 最大单元个数
        max_init_class_count -- 最大初始类个数
        max_block_count -- 最大块个数
        max_added_counter -- 最大增加的counter值
        max_added_time -- 最大增加的time值
        max_added_class_count -- 最大增加的class个数
        max_added_end_time -- 最大增加的endTime值
    """
    
    def __init__(self, min_unit_count, max_unit_count, max_class_count, max_block_count, 
        max_added_counter, max_added_time, max_added_class_count, max_added_end_time):
        self.min_unit_count = min_unit_count
        self.max_unit_count = max_unit_count
        self.max_class_count = max_class_count
        self.max_block_count = max_block_count
        self.max_added_counter = max_added_counter
        self.max_added_time = max_added_time
        self.max_added_class_count = max_added_class_count
        self.max_added_end_time = max_added_end_time

class ClassDefinition:
    """类定义
    
    Attributes:
        name -- 名称
        methodList -- 方法
    """
    
    def __init__(self, name, methodList):
        self.name = name
        self.methodList = methodList
        
    def __str__(self):
        list = ["{\nclassName:{%s}\n" % (self.name)]
        for method in self.methodList:
            list.append("methodName:{%s},counter:{%d},time:{%d}\n" % (
                method.name, method.counter, method.time))
        list.append("}")
        
        return ''.join(list)

    def randomAddCounterAndTime(self, maxAddedCounter, maxAddedTime):
        """增加个数和时间
        
        Args:
            maxAddedCounter -- counter被增加的最大值
            maxAddedTime -- time被增加的最大值
        """
        
        for method in self.methodList:
            method.randomAddCounterAndTime(maxAddedCounter, maxAddedTime)
            
    def copy(self):
        clonedMethodList = []
        for method in self.methodList:
            clonedMethodList.append(method.copy())
        return ClassDefinition(self.name, clonedMethodList)
        
class MethodDefinition:
    """方法定义
    
    Attributes:
        name -- 名称
        counter -- 个数
        time -- 时间
    """
    
    def __init__(self, name, counter, time):
        self.name = name
        self.counter = counter
        self.time = time
        
    def randomAddCounterAndTime(self, maxAddedCounter, maxAddedTime):
        """随机增加个数和时间
        
        Args:
            maxAddedCounter -- counter被增加的最大值
            maxAddedTime -- time被增加的最大值
        """
    
        self.counter += random_int(0, maxAddedCounter)
        self.time += random_int(0, maxAddedTime)
    
    def copy(self):
        return MethodDefinition(self.name, self.counter, self.time)
    
class Block:
    """块
    一个块包括1个开始时间，1个结束时间，和若干类组成
    
    例如：
    startTime:{2015-10-19 13:57:35}
    {
    className:{com.thunisoft.susong51.sfks.service.ThreeSidesServiceImpl}
    methodName:{setRygxService},counter:{1},time:{0},avg:{0}
    }
    {
    className:{com.thunisoft.susong51.sfks_ssb.action.SsbAction}
    methodName:{setCodeCache},counter:{1},time:{0},avg:{0}
    methodName:{setStoreService},counter:{1},time:{0},avg:{0}
    }
    endTime:{2015-10-19 13:57:55}
    
    Attributes:
        startTime -- 开始时间，格式%Y-%m-%d %H:%M:%S
        endTime -- 结束时间，格式%Y-%m-%d %H:%M:%S
        classList -- 类（ClassDefinition）列表
    """
    
    def __init__(self, startTime, endTime, classList):
        self.startTime = startTime
        self.endTime = endTime
        self.classList = classList
        
    def __str__(self):
        list = [JAVA_AGENT_SPLIT_LINE, "\nstartTime:{%s}\n"%(self.startTime.strftime(TIME_FORMAT))]
        for clazz in self.classList:
            list.append(str(clazz))
            list.append("\n")
        list.append("endTime:{%s}\n"%(self.endTime.strftime(TIME_FORMAT)))
        
        return ''.join(list)
        
    def copy(self):
        clonedClassList = []
        for clazz in self.classList:
            clonedClassList.append(clazz.copy())
        return Block(self.startTime, self.endTime, clonedClassList)
        
    
    def setStartTimeAndEndTime(self, startTime, maxAddedMinutes):
        """设置开始时间和结束时间
        
        Args:
            startTime -- 开始时间
            maxAddedMinutes -- 随机增加的最大分钟
        """
        
        ms = random_int(1, maxAddedMinutes)
        self.startTime = startTime + datetime.timedelta(minutes=ms)
        ms = random_int(1, maxAddedMinutes)
        self.endTime = self.startTime + datetime.timedelta(minutes=ms)
    
    def randomAddStartTime(self, maxAddedMinutes):
        """增加开始时间
        
        Args:
            maxMinutes -- 随机增加的最大分钟
        """
        
        ms = random_int(1, maxAddedMinutes)
        self.startTime += datetime.timedelta(minutes=ms)
        return self
        
    def randomAddEndTime(self, maxAddedMinutes):
        """增加结束时间
        
        Args:
            maxMinutes -- 随机增加的最大分钟
        """
        
        ms = random_int(1, maxAddedMinutes)
        self.endTime += datetime.timedelta(minutes=ms)
        return self
        
    def randomAddCounterAndTime(self, maxAddedCounter, maxAddedTime):
        """增加个数和时间
        
        Args:
            maxAddedCounter -- counter被增加的最大值
            maxAddedTime -- time被增加的最大值
        """
        
        for clazz in self.classList:
            clazz.randomAddCounterAndTime(maxAddedCounter, maxAddedTime)
            
        return self
        
    def randomAddClasses(self, dic, maxAddedClassCount):
        """增加类的个数
        
        Args:
            maxAddedClassCount -- 增加class的最大个数
        """
        
        addedClasses = random_class_list(dic, maxAddedClassCount)
        self.classList.extend(addedClasses)
        return self

class Unit:
    """单元
    由开始时间相同，结束时间递增一组块组成
    
    Attributes:
        blockList -- 块列表，开始时间相同，结束时间递增
    """
    
    def __init__(self, dic, tempBlock, randomParams):
        """ 
        Args:
            dic -- 字典
            tempBlock -- 第一个块 
            randomParams -- 随机参数
        """
        
        count = random_int(1, randomParams.max_block_count)
        i = 0
        cur = tempBlock
        self.blockList = []
        while i < count:
            block = cur.copy()
            block.randomAddCounterAndTime(randomParams.max_added_counter, randomParams.max_added_time)
            block.randomAddClasses(dic, randomParams.max_added_class_count)
            block.randomAddEndTime(randomParams.max_added_end_time)
            self.blockList.append(block)
            cur = block
            i += 1
    
    def __str__(self):
        list = []
        for block in self.blockList:
            list.append(str(block))
            
        return "".join(list)
            
        
def create_folder(path):
    """如果没有则新建目录
    
    Args:
        path -- 文件夹路径
    """
    
    if os.path.exists(path) == False:
        os.makedirs(path)
        
def clear_folder(path):
    """清空目录
    
    Args:
        path -- 文件夹路径
    """
    
    if os.path.exists(path):
        shutil.rmtree(path)
        
def create_file(path):
    """新建文件
    
    Args:
        path -- 文件路径
    """
    
    f = open(path, 'w')
    f.close()
    
def generate_dictionary():
    """从文章中获取单词字典，用于生成类名、包名"""
    
    with open(DICTIONARY_SOURCE, 'r') as f:
        content = f.read()
        content, num = re.subn(JQL_KEYWORDS, "", content)
        words = re.findall(WORDS_KEY, content)
        return [x.lower() for x in words]

def random_package(dic):
    """随机生成java包名
    
    Args:
        dic -- 字典
        
    Return:
        随机生成java包名
    """
    
    return '.'.join(random.sample(dic, random_int(MIN_PACKAGE_WORDS_COUNT, MAX_PACKAGE_WORDS_COUNT)))
    
def random_class_name(dic):
    """随机生成类名（包含包）
    
    Args:
        dic -- 字典
        
    Return:
        随机生成类名（包含包）
    """
    
    package = random_package(dic)
    clazz = dic[random_int(0, len(dic) - 1)].title()
    return '.'.join([package, clazz])
    
def random_method(dic):
    """随机方法名
    
    Args:
        dic -- 字典
    
    Return:
        随机方法名
    """
    
    return ''.join(random.sample(dic, random_int(3, 6)))
    
def random_int(min, max):
    """生成min到max之间的随机整数
    
    Args:
        min -- 最小值
        max -- 最大值
        
    Return:
        随机整数
    """
    
    return random.randint(min, max)
    
def random_class(dic):
    """随机类
    
    Args:
        dic -- 字典
    
    Return:
        随机类
    """
     
    methodList = []
    i = 0
    count = random_int(1, MAX_METHOND_COUNT)
    while (i < count):
        methodList.append(MethodDefinition(random_method(dic), 
            random_int(1, MAX_METHOND_COUNTER), random_int(0, MAX_METHOND_TIME)))
        i = i + 1
    
    return ClassDefinition(random_class_name(dic), methodList)
    
def random_class_list(dic, max_count):
    """随机类list
    
    Args:
        dic -- 字典
        max_count -- 最大个数
        
    Return:
        随机类列表
    """
    
    result = []
    i = 0
    count = random_int(1, max_count)
    while (i < count):
        result.append(random_class(dic))
        i = i + 1
        
    return result
    
def random_increase_counter_time(class_list):
    """随机的增加counter和time的数值"""
    
    for clazz in class_list:
        for method in clazz.methodList:
            count = random_int(0, 100)
            time = random_int(0, 100)
            method.counter += count
            method.time += time
    
def local_now():
    """本地当前时间"""

    return datetime.datetime.now()
    
def random_java_agent_log(dic, random_params, filename):
    """随机java-agent日志
    
    Args:
        max_unit_count -- 最大单元个数
        random_params -- 随机参数
    Return:
        有效数据（block list）
    """
    
    result = []
    
    unit_count = random_int(random_params.min_unit_count, random_params.max_unit_count)
    startTime = local_now()
    endTime = startTime + datetime.timedelta(minutes=random_params.max_added_end_time)
    classList = random_class_list(dic, random_params.max_class_count)
    block = Block(startTime, endTime, classList)
    with io.open(filename, 'w') as fd:
        i = 0
        while i < unit_count:
            unit = Unit(dic, block, random_params)
            fd.write(str(unit))
            block = unit.blockList[-1].copy()
            block.setStartTimeAndEndTime(block.endTime, random_params.max_added_end_time)
            i += 1
            
            result.append(unit.blockList[-1].copy()) # 每个单元的最后一个块为有效数据
    
    return result

def block_list_2_JqlItem_list(blockList):
    """将块list转换成JqlItem list
    
    Args:
        block list -- 块list
    Return:
        JqlItem list -- jql元素list
    """
    
    result = []
    for block in blockList:
        itemList = block_2_JqlItem_list(block)
        result.extend(itemList)
    return result
    
def block_2_JqlItem_list(block):
    """将块转换成JqlItem list
    
    Args:
        block -- 块
    Return:
        JqlItem list -- jql元素list
    """
    
    result = []
    for clazz in block.classList:
        for method in clazz.methodList:
            item = JqlItem(clazz.name, method.name, method.counter, method.time, 
                        block.startTime.strftime(TIME_FORMAT), block.endTime.strftime(TIME_FORMAT))
            result.append(item)
    return result
    
def select_columns(item_list, cols=AgentLogTableTitles):
    """选择列
    
    Args:
        item_list -- JqlItem list
        cols - 列名
    Return:
        按列名排列的值二维数组
    """
    
    if cols is None:
        return []
    
    result = []
    for item in item_list:
        valueList = []
        for title in cols: 
            if title == 'time':
                valueList.append(item.time)
            elif title == 'count':
                valueList.append(item.count)
            elif title == 'avg time':
                valueList.append(item.avgTime)
            elif title == 'method':
                valueList.append(item.method)
            elif title == 'class':
                valueList.append(item.clazz)
            elif title == 'start time':
                valueList.append(item.startTime)
            elif title == 'end time':
                valueList.append(item.endTime)
        result.append(valueList)
    
    return result
    
def write_item_list(path, item_list):
    """写元素列表
    
    Args:
        path -- 文件路径
        item_list -- 元素列表
    """

    with io.open(path, 'w') as fd:
        for item in item_list:
            fd.write(str(item)) 
            fd.write("\n")
            
def write_select_list(path, row_list):
    """写select结果列表
    
    Args:
        path -- 文件路径
        row_list -- 行列表，二维
    """
    
    with io.open(path, 'w') as fd:
        for row in row_list:
            for data in row:
                fd.write(str(data))
                fd.write(' ')
            fd.write("\n")
            
def cmp_select_list(expected_list, actual_list):
    """比较select List
    
    Args:
        expected_list -- 期望列表
        actual_list -- 实际列表
    Return:
        result, info -- 结果（True -- 相等， False -- 不相等），不相等记录的描述
    """
        
    len1 = len(expected_list)
    len2 = len(actual_list)
    if len1 < len2:
        return False, ["实际结果比期望结果多了%d条记录" % ( len2 - len1 )]
    elif len1 > len2:
        return False, ["期望结果比实际结果多了%d条记录" % ( len1 - len2 )]
    else:
        i = 1
        result = True
        msg_list = []
        for expected, actual in zip(expected_list, actual_list):
            len1 = len(expected)
            len2 = len(actual)
            if len1 != len2:
                result = False
                msg_list.append("第%d条记录不相等\nexpected:%s\n  actual:%s\n" % (i, str(expected), str(actual)))
            else:
                for e_data, a_data in zip(expected, actual):
                    if e_data != a_data:
                        result = False
                        msg_list.append("第%d条记录不相等\nexpected:%s\n  actual:%s\n" % (i, str(expected), str(actual)))
                        break
            i += 1
        return result, "".join(msg_list)
        
def test():
    dic = generate_dictionary()
    rp = RandomParams(1, 4, 10, 10, 100, 100, 5, 5)
    result = random_java_agent_log(dic, rp, "test_java_agent.log")
    print_block_list(result)
    
def print_block_list(block_list):
    for block in block_list:
        print(str(block))
        
def write_block_list(path, block_list):
    with io.open(path, 'w') as fd:
        for block in block_list:
            fd.write(str(block)) 
            fd.write("\n")

def handle_result(content, jql, result, cmp_msg, result_path):
    """处理结果
    
    Args:
        content -- 测试内容
        jql -- 测试语句
        result -- 测试结果
        cmp_msg -- 比较信息
    """
    
    result_msg = ""
    if result is True:
        result_msg = "%s %s" % (RESULT_SUCCESS, content)
    else:
        length = 1000 if len(cmp_msg) > 1000 else len(cmp_msg)
        msg = cmp_msg[0:length]
        result_msg = "%s %s\n%s\njql:\n%s\n\n%s%s\n%s" % (RESULT_FAILURE, content, '*'*60, jql, msg, ' ...' '*'*60)
    print(result_msg)
    
    with io.open(result_path, 'a') as fd:
        fd.write(result_msg) 
        fd.write("\n") 
    
if __name__ == "__main__":
    test()