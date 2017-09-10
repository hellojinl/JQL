#coding=utf-8
import re, io, os, sys, time
from JQLCore import AgentLogTableTitles, ColumnDefinition, QueryDefinition, JQL_TIME_FORMAT, EARLIEST_TIME
from JQLCore import JQL_OPERATOR, JqlItem, LogicalExpression, JqlFile, JqlParseException

START_TIME_PATTERN = re.compile(r"startTime:{.*}")
END_TIME_PATTERN = re.compile(r"endTime:{.*}")
CLASS_NAME_PATTERN = re.compile(r"className:{.*}")
METHOD_NAME_PATTERN = re.compile(r"methodName:.*")
COUNTER_PATTERN = re.compile(r"counter.*")
TIME_PATTERN = re.compile(r"time.*")
FILE_NAME_ILLEGAL_CHARACTER = re.compile(r"[*?\"\<\>\|]")
JQL_SPLIT_KEY = r"select |from |where |order by |limit |into |;"
ORDER_PATTERN = re.compile(r"asc|desc")

AVG_TIME_RE = AgentLogTableTitles[2] + "\s*(?=>|!=|=|<)"
END_TIME_RE = AgentLogTableTitles[6] + "\s*(?=>|!=|=|<)"
START_TIME_RE = AgentLogTableTitles[5] + "\s*(?=>|!=|=|<)"
TIME_RE = AgentLogTableTitles[0] + "\s*(?=>|!=|=|<)"
COUNT_RE = AgentLogTableTitles[1] + "\s*(?=>|!=|=|<)"
METHOD_RE = AgentLogTableTitles[3] + "\s*(?=>|!=|=|<)"
CLASS_RE = AgentLogTableTitles[4] + "\s*(?=>|!=|=|<)"

def checkJQL(jql):
    """校验jql
    
    校验规则：
        1. 关键字顺序必须为：select, from, where, order by, limit, into
        2. from为必填项
    """
    
    if len(jql.strip()) == 0:
        raise JqlParseException("JQL empty")
    
    max = -1
    pos = jql.find("select ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('select order error')
            
    pos = jql.find("from ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('from order error')
    else:
        raise JqlParseException('no from')
        
    pos = jql.find("where ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('where order error')
             
    pos = jql.find("order by ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('order by order error')
    
    pos = jql.find("limit ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('limit order error')
            
    pos = jql.find("into ")
    if pos != -1:
        if pos > max:
            max = pos
        else:
            raise JqlParseException('into order error')

def parseJQL(jql):
    """解析查询语句
    
    Args:
        jql --  查询语句
    Return:
        QueryDefinition -- 解析查询语句得到的定义
    """
    
    #分片
    segments = re.split(JQL_SPLIT_KEY, jql)
    
    i = 1
    #处理select
    titleList = []
    if jql.find("select") != -1:
        selectStr = segments[i].strip()
        i += 1
        
        if len(selectStr) == 0:
            raise JqlParseException('select no values')
            
        for title in selectStr.split(","):
            title = title.strip()
            
            if len(title) == 0:
                raise JqlParseException('selct empty value: select ' + selectStr) 
            
            if title not in AgentLogTableTitles:
                raise JqlParseException('select value error:\'' + title + '\'')
                
            titleList.append(title)
    else:
        # 默认表头
        titleList = AgentLogTableTitles

    #处理from
    fileList = []
    if jql.find("from") != -1:
        fromStr = segments[i].strip()
        i += 1
        
        if len(fromStr) == 0:
            raise JqlParseException('from no values')
        
        for root in fromStr.split(","):
            root = root.strip()
            rl = len(root)
            if rl == 0:
                raise JqlParseException('from empty value: where ' + fromStr)
                
            ra = re.split("\s+", root)
            encoding="utf-8"
            if len(ra) > 1:
                encoding = ra[-1]
                root = root[:rl-len(ra[-1])].strip()
                
            if os.path.isdir(root):
                files = os.listdir(root)
                for file in files:
                    fileList.append(JqlFile(os.path.join(root, file), encoding))
            elif os.path.isfile(root):
                fileList.append(JqlFile(root, encoding))
            else:
                raise JqlParseException('from value error: ' + root + ' is not a file or dir')
    else:
        raise JqlParseException('no from')
     
    #处理where
    condition = None
    if jql.find("where") != -1:
        whereStr = segments[i].strip()
        i += 1
        
        if len(whereStr) == 0:
            raise JqlParseException('where no values')
         
        condition = whereStr
        
    #处理order by
    keyList = []
    orderList = []
    if jql.find("order by") != -1:
        orderByStr = segments[i].strip()
        i += 1
        
        if len(fromStr) == 0:
            raise JqlParseException('order by no values')
         
        for order in orderByStr.split(","):
            order = order.strip()
            
            if len(order) == 0:
                raise JqlParseException('order by empty values')     
            else:
                pos = re.search(ORDER_PATTERN, order)
                key = None
                keyOrder = None
                if pos is None:
                    # 默认升序
                    key = order
                    keyOrder = "asc"
                else:
                    key = order[: pos.start()].strip()
                    keyOrder = order[pos.start() : pos.end()]
         
                if key not in AgentLogTableTitles:
                    raise JqlParseException('order by no support key error. key = ' + key)
                    
                keyList.append(key)
                orderList.append(keyOrder)
    
    #处理limit
    limit = -1
    if jql.find("limit") != -1:
        limitStr = segments[i].strip()
        i += 1
         
        if len(limitStr) == 0:
            raise JqlParseException('limit no values')
        
        if limitStr.isdigit() == False:
            raise JqlParseException("limit value type error, value must be a nonnegative integer, value = " + limitStr)
        
        limit = limitStr
        
    #处理into
    into = None
    if jql.find("into") != -1:
        intoStr = segments[i].strip()
        i += 1
        
        if len(intoStr) == 0:
            raise JqlParseException('into no value')
            
        if re.search(FILE_NAME_ILLEGAL_CHARACTER, intoStr) is not None:
            raise JqlParseException('into value error, value must be a valid file name, value = ' + intoStr)
        
        into = intoStr
        
    return QueryDefinition(titleList, fileList, condition, keyList, orderList, limit, into)

def getValueInBrackets(str):
    """得到括号内的值
    
    Args:
        str -- 包括{}的字符串

    Return:
        {}内的值(去除了2端的空格)
    """
    
    return str[str.find("{") + 1 : str.find("}")].strip()
    
def queryAndFilter(file, queryDef):
    """查询并过滤数据
    
    Args:
        file -- 文件(类型: JQLCore.JqlFile)
        queryDef -- 查询定义
    Return:
       已过滤的数据
    """
    
    result = []
    buffer = []
    startTime = None
    with io.open(file.path, 'r', encoding=file.encoding) as fd:
        for line in fd:
            #处理startTime:...行
            match = START_TIME_PATTERN.match(line)
            if match: 
                #如果开始时间有变化，则过滤并保存结果，否则丢弃
                newStartTime = getValueInBrackets(line)
                if newStartTime != startTime: 
                    datas = filterDatas(buffer, startTime, queryDef)
                    startTime = newStartTime
                    result.extend(datas)
                    
                buffer = []
            else:
                buffer.append(line) 
        
        #保存最后一个时间域的数据
        datas = filterDatas(buffer, startTime, queryDef)
        result.extend(datas)
    
    return result

def filterDatas(buffer, startTime, queryDef):
    """过滤数据
    
    Args:
        buffer -- 行缓存
        startTime -- 开始时间
        queryDef -- 查询定义
    """
    
    if len(buffer) == 0:
        return []
    
    clazz = None
    method = None
    count = 0
    totalTime = 0
    dataList = []
    temp = []
    for line in buffer:
        #解析className...行
        match = CLASS_NAME_PATTERN.match(line)
        if match:
            clazz = getValueInBrackets(line)
            continue
            
        #解析methodName...行
        match = METHOD_NAME_PATTERN.match(line)
        if match:
            for str in line.split(','):
                #处理methodName
                match = METHOD_NAME_PATTERN.match(str)
                if match:
                    method = getValueInBrackets(str)
                    continue   
                #处理counter
                match = COUNTER_PATTERN.match(str)
                if match:
                    count = getValueInBrackets(str)
                    continue       
                #处理time
                match = TIME_PATTERN.match(str)
                if match:
                    totalTime = getValueInBrackets(str)

            item = JqlItem(clazz, method, count, totalTime, startTime)
            temp.append(item) 
            continue
            
        #处理endTime:...行
        match = END_TIME_PATTERN.match(line)
        if match:
            endTime = getValueInBrackets(line)
            for item in temp:
                item.endTime = endTime
                if checkItem(item, queryDef):
                    dataList.append(item)
    
    return dataList   

def checkItem(item, queryDef):
    """校验数据
    
    Args:
        item -- 数据
        queryDef -- 查询定义
    """
    
    #没有过滤条件
    if queryDef.condition is None:
        return True
    
    #计算过滤条件
    condition = queryDef.condition[:]
    condition, num = re.subn(AVG_TIME_RE, str(item.avgTime), condition)
    condition, num = re.subn(END_TIME_RE, str(item.endTime), condition)
    condition, num = re.subn(START_TIME_RE, str(item.startTime), condition)
    condition, num = re.subn(TIME_RE, str(item.time), condition)
    condition, num = re.subn(COUNT_RE, str(item.count), condition)
    condition, num = re.subn(METHOD_RE, str(item.method), condition)
    condition, num = re.subn(CLASS_RE, str(item.clazz), condition)
    
    le = LogicalExpression(condition)
    return le.result() 
 
def sortAndCut(itemList, queryDef):
    """将itemList根据查询条件排序和剪切
    
    Args:
        itemList -- 数据
        queryDef -- 查询定义
    Return:
        dataList -- 排序和剪切后的结果
    """
    
    #处理排序
    for key, order in zip(reversed(queryDef.keyList), reversed(queryDef.orderList)):
        #得到lambda函数
        keyLambda = None
        
        if key == AgentLogTableTitles[0]:
            keyLambda = lambda item: item.time
        elif key == AgentLogTableTitles[1]:
            keyLambda = lambda item: item.count
        elif key == AgentLogTableTitles[2]:
            keyLambda = lambda item: item.avgTime
        elif key == AgentLogTableTitles[3]:
            keyLambda = lambda item: item.method
        elif key == AgentLogTableTitles[4]:
            keyLambda = lambda item: item.clazz
        elif key == AgentLogTableTitles[5]: 
            keyLambda = lambda item: time.strptime(item.startTime, JQL_TIME_FORMAT) if item.startTime != None else EARLIEST_TIME
        elif key == AgentLogTableTitles[6]:
            keyLambda = lambda item: time.strptime(item.endTime, JQL_TIME_FORMAT) if item.endTime != None else EARLIEST_TIME
        else:
            continue
        
        #判断是否逆排序（默认递增排序）
        rev = (order == 'desc')
        
        itemList.sort(key=keyLambda, reverse=rev)

    return itemList[0 : queryDef.limit] if queryDef.limit != -1 else itemList
    
def mergeSort(list, queryDef):
    """合并算法
    
    Args:
        list -- 待合并的列表集合
        queryDef -- 查询定义
    Return:
        合并后的列表
    """
    
    result = list[:]
    length = len(result)
    while length > 1:
        tempList = []
        i = 0
        while i < length:
            if i + 1 < length:
                temp = merge(result[i], result[i + 1], queryDef)
                tempList.append(temp)
            else:
                tempList.append(result[i])
            i += 2
        result = tempList
        length = len(result)
    return result[0] if length >= 1 else []
        
def merge(list1, list2, queryDef):
    """按照queryDef里定义的规则合并列表
    
    Args:
        list1 -- 列表1
        list2 -- 列表2
        queryDef -- 查询定义
    Return
        合并后的列表
    """
    
    list = []
    list.extend(list1)
    list.extend(list2)
    return sortAndCut(list, queryDef)

def drawTable(dataList, queryDef, showMsg):
    """画表格
    
    Args:
        dataList -- 数据
        queryDef -- 查询定义
        showMsg -- 在屏幕是否显示信息，True：显示，False：不显示
    Return:
        纯数据(无表格格式)的最终结果
    Example:
    +---------+----------+-----------+------------+--------------+
    | count   | time     | avg time  | method     | class        |
    +---------+----------+-----------+------------+--------------+
    | 10      | 500      | 50        | sayHello   | Test.java    |
    +---------+----------+-----------+------------+--------------+
    """
    
    buffer = io.StringIO()
    
    #在缓冲中画表格
    drawLine(buffer, queryDef)
    drawTitle(buffer, queryDef)
    drawLine(buffer, queryDef)
    result = drawDataRows(dataList, buffer, queryDef)
    drawLine(buffer, queryDef, "")
    
    table = buffer.getvalue()
    
    buffer.close()
    
    #输出表格
    if queryDef.into is None:
        jql_print(table, showMsg)
    else:
        with io.open(queryDef.into, 'w') as fd:
            fd.write(table)
        msg = "OK, saved in file '%s'"%(queryDef.into)
        length = len(msg)
        jql_print("%s\n%s\n%s" % ("*"*length, msg, "*"*length), showMsg)
        
    return result
    
def drawLine(buffer, queryDef, newline="\n"):
    """画分割线
    
    Args:
        buffer -- 缓存
        queryDef -- 查询定义
        newline -- 换行符
    """
    
    formatList = []
    valueList = []
    for title in queryDef.titleList:
        colDef = queryDef.tableCols[title]
        size = colDef.size + 2
        formatList.append('+' + formatString("string", size, False))
        valueList.append("-"*size)
    formatList.append('+' + newline)
    formatStr = ''.join(formatList)
    
    buffer.write(formatStr % tuple(valueList))

def drawTitle(buffer, queryDef, newline="\n"):
    """画表头
    
    Args:
        buffer -- 缓存
        queryDef -- 查询定义
        newline -- 换行符
    """
    
    formatList = []
    valueList = []
    for title in queryDef.titleList:
        colDef = queryDef.tableCols[title]
        formatList.append('| ' + formatString("string", colDef.size) + ' ')
        valueList.append(title)
    formatList.append('|' + newline)
    formatStr = ''.join(formatList)
    
    buffer.write(formatStr % tuple(valueList))
  
def drawDataRows(itemList, buffer, queryDef, newline="\n"):
    """画数据行
    
    Args:
        itemList -- 数据
        buffer -- 缓存
        queryDef -- 查询定义
        newline -- 换行符
    Return:
        纯数据(无表格格式)的最终结果
    """

    formatList = []
    for title in queryDef.titleList:
        colDef = queryDef.tableCols[title]
        formatList.append('| ' + formatString(colDef.type, colDef.size) + ' ')
    formatList.append('|' + newline)
    formatStr = ''.join(formatList)
    
    result = []
    for item in itemList:
        valueList = []
        for title in queryDef.titleList: 
            if title == AgentLogTableTitles[0]:
                valueList.append(item.time)
            elif title == AgentLogTableTitles[1]:
                valueList.append(item.count)
            elif title == AgentLogTableTitles[2]:
                valueList.append(item.avgTime)
            elif title == AgentLogTableTitles[3]:
                valueList.append(item.method)
            elif title == AgentLogTableTitles[4]:
                valueList.append(item.clazz)
            elif title == AgentLogTableTitles[5]:
                valueList.append(item.startTime)
            elif title == AgentLogTableTitles[6]:
                valueList.append(item.endTime)
        result.append(valueList)
                
        buffer.write(formatStr % tuple(valueList))
        
    return result
               
def formatString(type, size, leftAlignment=True):
    """得到格式化占位符
    
    Args:
        type -- 数据类型
        size -- 位数
        leftAlignment -- 是否左对齐
        
    Return:
        格式化占位符
    """
    
    prefix = ('-' if leftAlignment else '')
    result = '%' + prefix + str(size)
    
    if type == "int":
        result += 'd'
    elif type == "float":
        result += '.2f'
    else:
        result += 's'
        
    return result

def executeQuery(jql, showMsg):
    """执行jql，并输出表格
    
    Args:
        jql -- 查询语句
        showMsg -- 是否在屏幕显示信息，True：显示，False：不显示
    Return:
        没有异常 -- 结果集
        有异常 -- 异常信息
    """
    
    try:  
        start = time.time()
        
        #校验jql
        checkJQL(jql)
        #解析jql
        queryDef = parseJQL(jql)
        #处理各个文件的数据
        list = []
        for file in queryDef.fileList:
            #查询、过滤数据
            dataList = queryAndFilter(file, queryDef)
            #排序、裁剪数据
            dataList = sortAndCut(dataList, queryDef)
            #收集结果  
            list.append(dataList)
        
        #合并多个文件的数据
        dataList = mergeSort(list, queryDef)  
        #画表
        result = drawTable(dataList, queryDef, showMsg)
        
        end = time.time()

        jql_print("tottime: %.2fs\n"%(end-start), showMsg)  
        
        return result
    except JqlParseException as perr:
        msg = "[JQL PARSE ERROR] {0}".format(perr)
        length = len(msg)
        parseError = "%s\n%s\n%s\n" % ("*"*length, msg, "*"*length)
        if showMsg:
            print(parseError)
        return parseError
    except Exception as err:
        msg = "[JQL ERROR] {0}".format(err)
        length = len(msg)
        exError = "%s\n%s\n%s\n" % ("*"*length, msg, "*"*length)
        if showMsg:
            print(exError)
        return exError

def jql_print(content, show):
    """jql输出
    
    Args:
        content -- 内容
        show -- 是否输出，True:输出，False:不输出
    """
    
    if show:
        print(content)
        
def main():
    """主函数"""
   
    if len(sys.argv) > 1:
        executeQuery(sys.argv[1], True)
    else:
        print("Please input JQL\ninput 'q!' for quit, input ';' for execute jql\n")
        jql = ""
        while (True):
            line = input(">>> ")
            if (line == "q!" or line == "Q!"):
                print("Thanks.")
                sys.exit()
            elif line.find(";") != -1:
                line = line.split(";")
                jql += (' ' + line[0].strip() + ';')
                executeQuery(jql, True)
                jql = ""
            else:
                jql += (' ' + line.strip())
      
if __name__ == "__main__":
    main()
 
