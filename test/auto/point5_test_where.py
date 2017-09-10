#coding=utf-8

# 测试点5：where功能是否正确

# 测试jql：
# from point5/agentLog/
# where (avg time > 1000 or avg time < 100) and count >= 10000
# order by avg time desc
# limit 10
# into point5/actual;

import sys, os, io, time
sys.path.append(os.getcwd() + "/../../src/")

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, clear_folder, create_file, RESULT_SUCCESS, RESULT_FAILURE, handle_result
from auto_core import random_java_agent_log, block_list_2_JqlItem_list, RandomParams, write_select_list, cmp_select_list, write_block_list, select_columns
from JQLCore import JQL_TIME_FORMAT, EARLIEST_TIME
from JQL import executeQuery

POINT5_FOLDER = RESULT_FOLDER + "/test_where" #测试点5 where条件
PT5_RESULT_CMP = POINT5_FOLDER + RESULT_FILENAME #期望和实际结果对比
AGENT_LOG_FOLDER = POINT5_FOLDER + "/agentLog" #agent日志目录
LOG1 = AGENT_LOG_FOLDER + "/log1.log" #日志1
LOG2 = AGENT_LOG_FOLDER + "/log2.log" #日志2
REPLACE_KEYWORD_EXCEPTED = POINT5_FOLDER + "/replace_keyword_expected" #where测试期望
REPLACE_KEYWORD_ACTUAL = POINT5_FOLDER + "/replace_keyword_actual" #where测试实际

RESULT_MSG = "test where: " #结果
RANDOM_PARAMS = RandomParams(1, 2, 2, 2, 100, 100, 1, 10) #随机参数

def test_where(dic):
    """测试where"""
    
    item_list = generate_test_datas(dic)
    test_replace_keyword(item_list[:])
  
def generate_test_datas(dic):
    """生成测试数据
    
    Args:
        dic -- 单词词典
    Return:
        log1,log2的JqlItem list
    """
    
    create_folder(AGENT_LOG_FOLDER)
    create_file(PT5_RESULT_CMP)
    
    result = []
    
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG1)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)

    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG2)
    item_list = block_list_2_JqlItem_list(block_list)
    result.extend(item_list)
    
    return result
  
def test_replace_keyword(item_list):
    """测试关键字替换
    即：将where条件中的关键字替换成实际的数值，再用于比较
    
    Args:
        item_list -- log1,log2的JqlItem list
    """
    
    #创建期望结果
    item_list = [item for item in item_list if item.count > 10000]
    item_list = [item for item in item_list if item.avgTime > 1000 or item.avgTime < 100]
    key_lambda = lambda item: item.avgTime
    item_list.sort(key=key_lambda, reverse=True)
    
    length = 10 if len(item_list) > 10 else len(item_list)
    item_list = item_list[0:length]
    expected_list = select_columns(item_list)
    write_select_list(REPLACE_KEYWORD_EXCEPTED, expected_list)
    
    #运行jql
    test_jql = "from %s\nwhere (avg time > 1000 or avg time < 100) and count >= 10000\
                \norder by avg time desc\nlimit 10\ninto %s;" % (AGENT_LOG_FOLDER, REPLACE_KEYWORD_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "replace keyword", test_jql, result, cmp_msg, PT5_RESULT_CMP)

    
    