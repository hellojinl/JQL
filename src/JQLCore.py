#coding=utf-8
import re, time

#时间格式
JQL_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
#最早时间
EARLIEST_TIME = time.strptime('1970-01-01 12:00:00', JQL_TIME_FORMAT)
#逻辑运算元素查询关键字
LOGICAL_FIND_KEY = r"\(|\)|>=|<=|>|!=|=|<|[aA][nN][dD]|[oO][rR]|\d{4}-\d{2}-\d{2}[ ]\d{2}:\d{2}:\d{2}|[\w\.\$-]+"
#逻辑运算关键字
OPERATOR_KEY = r"\(|\)|>=|<=|>|!=|=|<|#|[aA][nN][dD]|[oO][rR]"
#优先级
#-1表示<, 0表示=， 1表示>, None表示表达式错误
#'#'运算符表示表达式的开始和结束，优先级最低
#例如:
#JQL_PRIORITY['and']['and'] = 1 表示 st1 and st2 and st3 的计算顺序为(st1 and st2) and st3
#JQL_PRIORITY['=']['and'] = 1 表示 st1 = st2 and st3 的计算顺序为 (st1 = st2) and st3
#
JQL_PRIORITY = {
      '(': { '(': -1,   ')': 0,    'and': -1,   'or': -1,   '=': -1,   '!=': -1,   '>': -1,   '>=': -1,   '<': -1,   '<=': -1,   '#': None },
      ')': { '(': None, ')': None, 'and': None, 'or': None, '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': None },
    'and': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': -1,   '!=': -1,   '>': -1,   '>=': -1,   '<': -1,   '<=': -1,   '#': 1    },
     'or': { '(': -1,   ')': 1,    'and': -1,   'or': 1,    '=': -1,   '!=': -1,   '>': -1,   '>=': -1,   '<': -1,   '<=': -1,   '#': 1    },
      '=': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
     '!=': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
      '>': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
     '>=': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
      '<': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
     '<=': { '(': -1,   ')': 1,    'and': 1,    'or': 1,    '=': None, '!=': None, '>': None, '>=': None, '<': None, '<=': None, '#': 1    },
      '#': { '(': -1,   ')': None, 'and': -1,   'or': -1,   '=': -1,   '!=': -1,   '>': -1,   '>=': -1,   '<': -1,   '<=': -1,   '#': 0    }
}

class ColumnDefinition:
    """列定义
    
    Attributes:
        name -- 名称
        type -- 类型
        size -- 大小
    """
    
    def __init__(self, name, type, size):
        self.name = name
        self.type = type
        self.size = int(size)
        
#java-agent-log-table表头定义
AgentLogTableTitles = ['time', 'count', 'avg time', 'method', 'class', 'start time', 'end time']
        
#java-agent-log-table定义
AgentLogTable = {
    AgentLogTableTitles[0]: ColumnDefinition(AgentLogTableTitles[0], 'int', 10),
    AgentLogTableTitles[1]: ColumnDefinition(AgentLogTableTitles[1], 'int', 10),
    AgentLogTableTitles[2]: ColumnDefinition(AgentLogTableTitles[2], 'int', 10),
    AgentLogTableTitles[3]: ColumnDefinition(AgentLogTableTitles[3], 'string', 35),
    AgentLogTableTitles[4]: ColumnDefinition(AgentLogTableTitles[4], 'string', 100),
    AgentLogTableTitles[5]: ColumnDefinition(AgentLogTableTitles[5], 'string', 20),
    AgentLogTableTitles[6]: ColumnDefinition(AgentLogTableTitles[6], 'string', 20)
}
           
class QueryDefinition:
    """查询定义，将解析后的查询条件保存于此，用于查询方法间的参数传递
    
    Attributes:
        titleList -- 表头
        fileList -- 文件
        condition -- 过滤条件
        keyList -- 排序关键字
        orderList -- 排序规则
        limit -- 个数限制
        into -- 写入文件路径，如果into=None，则在命令行输出结果，
                否则在into指定的文件写入结果（覆盖原文件）
    """
    
    def __init__(self, titleList, fileList, condition=None, keyList=[], orderList=[], limit=-1, into=None):
        self.titleList = titleList
        self.fileList = fileList
        self.condition = condition
        self.keyList = keyList
        self.orderList = orderList
        self.limit = int(limit)
        self.tableCols= AgentLogTable
        self.into = into
        
    def __eq__(self, other):
        return (other != None 
            and self.titleList == other.titleList
            and self.fileList == other.fileList
            and self.keyList == other.keyList
            and self.orderList == other.orderList
            and self.condition == other.condition
            and self.limit == other.limit
            and self.tableCols == other.tableCols
            and self.into == other.into)
        
class JqlFile:
    """jql文件
    
    Attributes:
        path -- 路径，包括文件名
        encoding -- 文件编码，默认值utf-8
    """
    
    def __init__(self, path, encoding="utf-8"):
        self.path = path
        self.encoding =encoding
        
    def __eq__(self, other):
        return (other != None 
            and self.path == other.path 
            and self.encoding == other.encoding)
        
def equal(x, y):
    return x == y

def notEqual(x, y):
    return x != y
    
def lessThan(x, y):
    return x < y
    
def lessThanOrEqualTo(x, y):
    return x <= y
        
def greaterThan(x, y):
    return x > y
    
def greaterThanOrEqualTo(x, y):
    return x >= y   

def jql_and(x, y):
    return x and y
    
def jql_or(x, y):
    return x or y

#jql操作
JQL_OPERATOR = {
    "=": equal,
    "!=": notEqual,
    "<": lessThan,
    "<=": lessThanOrEqualTo,
    ">": greaterThan,
    ">=": greaterThanOrEqualTo,
    "and": jql_and,
    "or": jql_or
}

class JqlItem:
    """数据项
    
    Attributes:
        clazz -- 类名
        method -- 方法
        count -- 总次数
        time -- 总时间
        startTime -- 开始时间
        endTime -- 结束时间
        avgTime -- 平均时间
    """
    
    def __init__(self, clazz, method, count, time, startTime, endTime=None):
        self.clazz = clazz
        self.method = method
        self.count = int(count)
        self.time = int(time)
        self.startTime = startTime
        self.endTime = endTime
        self.avgTime = int(self.time / self.count)
 
    def copy(self):
        """复制"""

        return JqlItem(self.clazz, self.method, self.count, self.time, self.startTime)
    
    def __eq__(self, other):
        return (other != None
            and self.clazz == other.clazz 
            and self.method == other.method
            and self.count == other.count 
            and self.time == other.time
            and self.startTime == other.startTime 
            and self.endTime == other.endTime
            and self.avgTime == other.avgTime)
            
    def __str__(self):
        list = [
            str(self.time),
            str(self.count),
            str(self.avgTime),
            str(self.method),
            str(self.clazz),
            str(self.startTime),
            str(self.endTime)
        ]
        
        return " ".join(list)
        
            
class LogicalExpression:
    """逻辑表达式
    
    Attributes:
        strExp -- 表达式的字符串
        segments -- 字符串表达式分片后的数组
    """
    
    def __init__(self, strExp):
        self.strExp = strExp
        if isinstance(strExp, str):
            self.segments = re.findall(LOGICAL_FIND_KEY, strExp)
        else:
            raise Exception('strExp must be a string') 
            
    def result(self):
        """结果"""
        
        if len(self.segments) == 0:
            raise Exception('none expression')
        
        op = ['#'] #运算符栈
        dt = [] #操作数栈
        exp = self.segments #表达式
        exp.append('#')
        for elem in exp:
            if isOperator(elem):
                p = prior(op[-1], elem)
                while p > 0:
                    r = dt.pop()
                    o = op.pop()
                    l = dt.pop()
                    dt.append(compute(l, o, r))
                    p = prior(op[-1], elem)
                if p is None:
                   raise Exception("not supported expression: " + self.strExp)  
                elif p == 0:
                    op.pop()
                else:
                    op.append(elem)
            else:
                dt.append(elem)
        
        return dt[0]
      
def isOperator(elem):
    """是否为支持的运算符"""

    return re.match(OPERATOR_KEY, elem) is not None
    
def prior(left, right):
    """判断相邻2个运算符优先级
    
    Args:
        left -- 左侧运算符
        right -- 右侧运算符
    Return:
        1 -- left优先级高
        0 -- left、right优先级相等
        -1 -- left优先级低
        None -- 错误的表达式
    """
    
    return JQL_PRIORITY[left][right]
    
def compute(left, op, right):
    """计算结果
    
    Args:
        left -- 左操作数
        op -- 运算符字符串
        right -- 右操作数
        
    Return:
        True or False
    """
    
    if left == '' or op == '' or right == '':
        raise Exception('expression empty value error') 

    l = left
    if isinstance(l, str):
        if isFloat(l):
            l = float(l)  
        elif isValidDatetime(l):
            l = time.strptime(l, JQL_TIME_FORMAT)
            
    r = right
    if isinstance(r, str):
        if isFloat(r): 
            r = float(r)
        elif isValidDatetime(r):
            r = time.strptime(r, JQL_TIME_FORMAT)
    
    ltype = type(l)
    rtype = type(r)
    if ltype == int and rtype == float:
        l = float(l)
    elif ltype == float and rtype == int:
        r = float(r)
        
    if type(l) != type(r):
       raise Exception('expression type error: ' + str(left) + ' ' + op + ' ' + str(right))  
    
    return JQL_OPERATOR[op](l, r)
 
def isFloat(str):
    """判断是否为浮点数"""
    
    try:
        float(str)
    except:
        return False
    else:
        return True
    
def isValidDatetime(str):
    """判断是否是一个有效的日期字符串"""
  
    try:
        time.strptime(str, JQL_TIME_FORMAT)
    except:
        return False
    else:
        return True

class JqlParseException(Exception):
    """jql解析异常
    
    Attributes:
        msg -- 信息
    """
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return repr(self.msg)
