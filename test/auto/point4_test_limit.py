#coding=utf-8

# 测试点4：limit功能是否正确

# a. 测试正整数：
# select avg time
# from point4/agentLog/
# order by avg time desc
# limit 10
# into point4/A_actual;

# b. 测试0：
# select avg time
# from point4/agentLog/
# order by avg time desc
# limit 0
# into point4/B_actual;

# c. 测试负整数
# select avg time
# from point4/agentLog/
# order by avg time desc
# limit -10
# into point4/C_actua;

# d. 测试浮点数
# select avg time
# from point4/agentLog/
# order by avg time desc
# limit 10.3
# into point4/D_actual;

import sys, os, io
sys.path.append(os.getcwd() + "/../../src/")

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, clear_folder, create_file, RESULT_SUCCESS, RESULT_FAILURE, handle_result
from auto_core import random_java_agent_log, block_list_2_JqlItem_list, RandomParams, write_select_list, cmp_select_list, write_block_list, select_columns
from JQLCore import JqlParseException
from JQL import executeQuery

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, create_file

POINT4_FOLDER = RESULT_FOLDER + "/test_limit" #测试4 limit
PT4_RESULT_CMP = POINT4_FOLDER + RESULT_FILENAME #期望和实际结果对比
AGENT_LOG_FOLDER = POINT4_FOLDER + "/agentLog" #agent日志目录
LOG1 = AGENT_LOG_FOLDER + "/log1.log" #日志1
LOG2 = AGENT_LOG_FOLDER + "/log2.log" #日志2
POSITIVE_INTEGER_EXPECTED = POINT4_FOLDER + "/positive_integer_expected" #测试正整数期望
POSITIVE_INTEGER_ACTUAL = POINT4_FOLDER + "/positive_integer_actual" #测试正整数实际
ZERO_EXPECTED = POINT4_FOLDER + "/zero_expected" #测试0期望
ZERO_ACTUAL = POINT4_FOLDER + "/zero_actual" #测试0实际
NEGTIVE_INTEGER_EXPECTED = POINT4_FOLDER + "/negtive_integer_expected" #测试负数期望
NEGTIVE_INTEGER_ACTUAL = POINT4_FOLDER + "/negtive_integer_actual" #测试负数实际
FLOAT_EXPECTED = POINT4_FOLDER + "/float_expected" #测试浮点数期望
FLOAT_ACTUAL = POINT4_FOLDER + "/float_actual" #测试浮点数实际

RESULT_MSG = "test limit: " #结果信息
RANDOM_PARAMS = RandomParams(1, 2, 2, 2, 100, 100, 1, 10) #随机参数

def test_limit(dic):
    """测试limit"""
    
    item_list = generate_test_datas(dic)
    test_positive_integer(item_list[:])
    test_zero()
    test_negtive_integer()
    test_float()
    
def generate_test_datas(dic):
    """生成测试数据
    
    Args:
        dic -- 单词词典
    Return:
        log1,log2的JqlItem list
    """
    
    create_folder(AGENT_LOG_FOLDER)
    create_file(PT4_RESULT_CMP)
    
    result = []
    
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG1)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)

    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG2)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)
    
    return result
    
def test_positive_integer(item_list):
    """测试正整数
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    num = 10
    
    #创建期望结果
    key_lambda = lambda item: item.avgTime
    item_list.sort(key=key_lambda, reverse=True)
    expected_list = select_columns(item_list, ["avg time"])
    expected_list = expected_list[0 : num]
    write_select_list(POSITIVE_INTEGER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time\nfrom %s\norder by avg time desc\nlimit %d\ninto %s" % (AGENT_LOG_FOLDER, num, POSITIVE_INTEGER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "positive integer", test_jql, result, cmp_msg, PT4_RESULT_CMP)
    
def test_zero():
    """测试0"""
    
    #创建期望结果
    expected_list = []
    write_select_list(ZERO_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time\nfrom %s\norder by avg time desc\nlimit %d\ninto %s" % (AGENT_LOG_FOLDER, 0, ZERO_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "zero", test_jql, result, cmp_msg, PT4_RESULT_CMP)
    
def test_negtive_integer():
    """测试负数"""
    
    num = -10
    
    #创建期望结果
    msg = "[JQL PARSE ERROR] 'limit value type error, value must be a nonnegative integer, value = %d'" % (num)
    length = len(msg)
    expected_list = ["%s\n%s\n%s\n" % ("*"*length, msg, "*"*length)]
    write_select_list(NEGTIVE_INTEGER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time\nfrom %s\norder by avg time desc\nlimit %d\ninto %s" % (AGENT_LOG_FOLDER, num, NEGTIVE_INTEGER_ACTUAL)
    result = executeQuery(test_jql, False)
    actual_list = [result]
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "negtive integer", test_jql, result, cmp_msg, PT4_RESULT_CMP)
    
def test_float():
    """测试浮点数"""
    
    num = 10.3
    
    #创建期望结果
    msg = "[JQL PARSE ERROR] 'limit value type error, value must be a nonnegative integer, value = %f'" % (num)
    length = len(msg)
    expected_list = ["%s\n%s\n%s\n" % ("*"*length, msg, "*"*length)]
    write_select_list(FLOAT_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time\nfrom %s\norder by avg time desc\nlimit %f\ninto %s" % (AGENT_LOG_FOLDER, num, FLOAT_ACTUAL)
    result = executeQuery(test_jql, False)
    actual_list = [result]
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "float", test_jql, result, cmp_msg, PT4_RESULT_CMP)

    
    