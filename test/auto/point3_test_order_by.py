#coding=utf-8

# 测试点3：order by功能是否正确

# a. 测试avg time默认排序：
# select avg time
# from point3/agentLog/
# order by avg time
# into point3/A_actual;

# b. 测试avg time升序
# select avg time
# from point3/agentLog/
# order by avg time asc
# into point3/B_actual;

# c. 测试avg time降序
# select avg time
# from point3/agentLog/
# order by avg time desc
# into point3/C_actua;

# d. 测试time升序
# select time
# from point3/agentLog/
# order by time asc
# into point3/D_actual;

# e. 测试time降序
# select time
# from point3/agentLog/
# order by time desc
# into point3/E_actual;

# f. 测试start time升序
# select start time
# from point3/agentLog/
# order by start time asc
# into point3/F_actual;

# g. 测试start time降序
# select start time
# from point3/agentLog/
# order by start time desc
# into point3/G_actual;

import sys, os, io, time
sys.path.append(os.getcwd() + "/../../src/")

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, clear_folder, create_file, RESULT_SUCCESS, RESULT_FAILURE, handle_result
from auto_core import random_java_agent_log, block_list_2_JqlItem_list, RandomParams, write_select_list, cmp_select_list, write_block_list, select_columns
from JQLCore import JQL_TIME_FORMAT, EARLIEST_TIME
from JQL import executeQuery

POINT3_FOLDER = RESULT_FOLDER + "/test_order_by" #测试点3目录
PT3_RESULT_CMP = POINT3_FOLDER + RESULT_FILENAME #期望和实际结果对比
AGENT_LOG_FOLDER = POINT3_FOLDER + "/agentLog" #agent日志目录
LOG1 = AGENT_LOG_FOLDER + "/log1.log" #日志1
LOG2 = AGENT_LOG_FOLDER + "/log2.log" #日志2
AVG_TIME_DEFAULT_ORDER_EXPECTED = POINT3_FOLDER + "/avg_time_default_order_expected" #平均时间默认排序期望
AVG_TIME_DEFAULT_ORDER_ACTUAL = POINT3_FOLDER + "/avg_time_default_order_actual" #平均时间默认排序实际
AVG_TIME_ASC_ORDER_EXPECTED = POINT3_FOLDER + "/avg_time_asc_order_expected" #平均时间升序期望
AVG_TIME_ASC_ORDER_ACTUAL = POINT3_FOLDER + "/avg_time_asc_order_actual" #平均时间升序实际
AVG_TIME_DESC_ORDER_EXPECTED = POINT3_FOLDER + "/avg_time_desc_order_expected" #平均时间降序期望
AVG_TIME_DESC_ORDER_ACTUAL = POINT3_FOLDER + "/avg_time_desc_order_actual" #平均时间降序实际
TIME_ASC_ORDER_EXPECTED = POINT3_FOLDER + "/time_asc_order_expected" #时间升序期望
TIME_ASC_ORDER_ACTUAL = POINT3_FOLDER + "/time_asc_order_actual" #时间升序实际
TIME_DESC_ORDER_EXPECTED = POINT3_FOLDER + "/time_desc_order_expected" #时间降序期望
TIME_DESC_ORDER_ACTUAL = POINT3_FOLDER + "/time_desc_order_actual" #时间降序实际
START_TIME_ASC_ORDER_EXPECTED = POINT3_FOLDER + "/start_time_asc_order_expected" #开始时间升序期望
START_TIME_ASC_ORDER_ACTUAL = POINT3_FOLDER + "/start_time_asc_order_actual" #开始时间升序实际
START_TIME_DESC_ORDER_EXPECTED = POINT3_FOLDER + "/start_time_desc_order_expected" #开始时间降序期望
START_TIME_DESC_ORDER_ACTUAL = POINT3_FOLDER + "/start_time_desc_order_actual" #开始时间降序实际

RESULT_MSG = "test order by: " #结果
RANDOM_PARAMS = RandomParams(1, 2, 2, 2, 100, 100, 1, 10) #随机参数

def test_order_by(dic):
    """测试order by
    
    Args:
        dic -- 单词词典
    """
    
    item_list = generate_test_datas(dic)
    
    test_avg_time_default_order(item_list[:])
    test_avg_time_asc_order(item_list[:])
    test_avg_time_desc_order(item_list[:])
    test_time_asc_order(item_list[:])
    test_time_desc_order(item_list[:])
    test_start_time_asc_order(item_list[:])
    test_start_time_desc_order(item_list[:])
    
def generate_test_datas(dic):
    """生成测试数据
    
    Args:
        dic -- 单词词典
    Return:
        log1,log2的JqlItem list
    """   
    
    create_folder(AGENT_LOG_FOLDER)
    create_file(PT3_RESULT_CMP)
    
    result = []
    
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG1)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)

    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG2)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)
    
    return result

def test_avg_time_default_order(item_list):
    """测试avg time默认排序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: item.avgTime
    item_list.sort(key=key_lambda, reverse=False)
    expected_list = select_columns(item_list, ["avg time"])
    write_select_list(AVG_TIME_DEFAULT_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time \nfrom %s \norder by avg time \ninto %s;" % (AGENT_LOG_FOLDER, AVG_TIME_DEFAULT_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "avg time default order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_avg_time_asc_order(item_list):
    """测试avg time升序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: item.avgTime
    item_list.sort(key=key_lambda, reverse=False)
    expected_list = select_columns(item_list, ["avg time"])
    write_select_list(AVG_TIME_ASC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time \nfrom %s \norder by avg time asc \ninto %s;" % (AGENT_LOG_FOLDER, AVG_TIME_ASC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "avg time asc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_avg_time_desc_order(item_list):
    """测试avg time降序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: item.avgTime
    item_list.sort(key=key_lambda, reverse=True)
    expected_list = select_columns(item_list, ["avg time"])
    write_select_list(AVG_TIME_DESC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time \nfrom %s \norder by avg time desc \ninto %s;" % (AGENT_LOG_FOLDER, AVG_TIME_DESC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "avg time desc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_time_asc_order(item_list):
    """测试time升序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: item.time
    item_list.sort(key=key_lambda, reverse=False)
    expected_list = select_columns(item_list, ["time"])
    write_select_list(TIME_ASC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select time \nfrom %s \norder by time asc \ninto %s;" % (AGENT_LOG_FOLDER, TIME_ASC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "time asc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_time_desc_order(item_list):
    """测试time降序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: item.time
    item_list.sort(key=key_lambda, reverse=True)
    expected_list = select_columns(item_list, ["time"])
    write_select_list(TIME_DESC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select time \nfrom %s \norder by time desc \ninto %s;" % (AGENT_LOG_FOLDER, TIME_DESC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "time desc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_start_time_asc_order(item_list):
    """测试start time升序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: time.strptime(item.startTime, JQL_TIME_FORMAT) if item.startTime != None else EARLIEST_TIME
    item_list.sort(key=key_lambda, reverse=False)
    expected_list = select_columns(item_list, ["start time"])
    write_select_list(START_TIME_ASC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select start time \nfrom %s \norder by start time asc \ninto %s;" % (AGENT_LOG_FOLDER, START_TIME_ASC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "start time asc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)
    
def test_start_time_desc_order(item_list):
    """测试start time降序
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    key_lambda = lambda item: time.strptime(item.startTime, JQL_TIME_FORMAT) if item.startTime != None else EARLIEST_TIME
    item_list.sort(key=key_lambda, reverse=True)
    expected_list = select_columns(item_list, ["start time"])
    write_select_list(START_TIME_DESC_ORDER_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select start time \nfrom %s \norder by start time desc \ninto %s;" % (AGENT_LOG_FOLDER, START_TIME_DESC_ORDER_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "start time desc order", test_jql, result, cmp_msg, PT3_RESULT_CMP)

    