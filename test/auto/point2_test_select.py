#coding=utf-8

# 测试点2：select功能的正确性

# a. 测试avg time, method, start time
# select avg time, method, start time
# from point2/agentLog/log1.log
# into point2/actualA;

# b. 测试count, time, class, end time
# select count, time, class, end time
# from point2/agentLog/log2.log
# into point2/actualB;

import sys, os, io
sys.path.append(os.getcwd() + "/../../src/")

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, clear_folder, create_file, RESULT_SUCCESS, RESULT_FAILURE, handle_result
from auto_core import random_java_agent_log, block_list_2_JqlItem_list, RandomParams, write_select_list, cmp_select_list, write_block_list, select_columns
from JQL import executeQuery

POINT2_FOLDER = RESULT_FOLDER + "/test_select" #测试点2目录
PT2_RESULT_CMP = POINT2_FOLDER + RESULT_FILENAME #期望和实际结果对比
AGENT_LOG_FOLDER = POINT2_FOLDER + "/agentLog" #agent日志目录
LOG1 = AGENT_LOG_FOLDER + "/log1.log" #日志1
LOG2 = AGENT_LOG_FOLDER + "/log2.log" #日志2
THREE_COLUMNS_EXPECTED = POINT2_FOLDER + "/three_columns_expected" #3列测试期望
THREE_COLUMNS_ACTUAL = POINT2_FOLDER + "/three_columns_actual" #3列测试实际
FOUR_COLUMNS_EXPECTED = POINT2_FOLDER + "/four_columns_expected" #4列测试期望
FOUR_COLUMNS_ACTUAL = POINT2_FOLDER + "/four_columns_actual" #4列测试实际

RESULT_MSG = "test select: " #结果信息
RANDOM_PARAMS = RandomParams(1, 2, 2, 2, 100, 100, 1, 10) #随机参数

def test_select(dic):
    """测试select"""
    
    create_folder(AGENT_LOG_FOLDER)
    create_file(PT2_RESULT_CMP)
    
    test_three_columns(dic)
    test_four_columns(dic)
    
def test_three_columns(dic):
    """测试3列"""
    
    #准备测试数据
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG1)
    
    #创建期望结果
    item_list = block_list_2_JqlItem_list(block_list)
    expected_list = select_columns(item_list, ["avg time", "method", "start time"])
    write_select_list(THREE_COLUMNS_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select avg time, method, start time \nfrom %s\ninto %s;" % (LOG1, THREE_COLUMNS_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "select three columns", test_jql, result, cmp_msg, PT2_RESULT_CMP)

    
def test_four_columns(dic):
    """测试4列"""
   
    #准备测试数据
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG2)
    
    #创建期望结果
    item_list = block_list_2_JqlItem_list(block_list)
    expected_list = select_columns(item_list, ['count', 'time', 'class', 'end time'])
    write_select_list(FOUR_COLUMNS_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "select count, time, class, end time \nfrom %s\ninto %s;" % (LOG2, FOUR_COLUMNS_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "select four columns", test_jql, result, cmp_msg, PT2_RESULT_CMP)