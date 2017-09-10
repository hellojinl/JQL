#coding=utf-8

# 测试点1：from功能的正确性

# a. 测试空文件夹
# from point1/agentLog/emptyDir
# into point1/empty_directory_actual;

# b. 测试空日志
# from point1/agentLog/empty_log.log
# into point1/empty_file_actual;

# c. 测试1个日志
# from point1/agentLog/log1.log
# into point1/one_file_actual;

# d. 测试2个日志
# from point1/agentLog/log1.log, point1/agentLog/log2.log
# into point1/two_files_actual;

# e. 测试3个日志
# from point1/agentLog/log1.log, point1/agentLog/log2.log, point1/agentLog/log3.log
# into point1/three_files_actual;

# f. 测试非java-agent日志
# from point1/agentLog/notAgent/log1.log
# into point1/not_java_agent_log_actual;

import sys, os, io
sys.path.append(os.getcwd() + "/../../src/")

from auto_core import RESULT_FOLDER, RESULT_FILENAME, create_folder, clear_folder, create_file, RESULT_SUCCESS, RESULT_FAILURE, handle_result
from auto_core import random_java_agent_log, block_list_2_JqlItem_list, RandomParams, write_select_list, cmp_select_list, write_block_list, select_columns
from JQL import executeQuery

POINT1_FOLDER = RESULT_FOLDER + "/test_from" #测试点1目录
PT1_RESULT_CMP = POINT1_FOLDER + RESULT_FILENAME #期望和实际结果对比
AGENT_LOG_FOLDER = POINT1_FOLDER + "/agentLog" #agent日志目录
NOT_AGENT_FOLDER = AGENT_LOG_FOLDER + "/notAgent" #not agent日志目录
EMPTY_FOLDER = AGENT_LOG_FOLDER + "/emptyDir" #空目录
EMPTY_LOG = AGENT_LOG_FOLDER + "/empty_log.log" #空日志
LOG1 = AGENT_LOG_FOLDER + "/log1.log" #日志1
LOG2 = AGENT_LOG_FOLDER + "/log2.log" #日志2
LOG3 = AGENT_LOG_FOLDER + "/log3.log" #日志3
NOT_AGENT_LOG = NOT_AGENT_FOLDER + "/log1.log" #非java-agent日志
EMPTY_DIR_EXPECTED = POINT1_FOLDER + "/empty_directory_expected" #空目录测试期望
EMPTY_DIR_ACTUAL = POINT1_FOLDER + "/empty_directory_actual" #空目录测试实际
EMPTY_FILE_EXPECTED = POINT1_FOLDER + "/empty_file_expected" #空文件测试期望
EMPTY_FILE_ACTUAL = POINT1_FOLDER + "/empty_file_actual" #空文件测试实际
ONE_FILE_EXPECTED = POINT1_FOLDER + "/one_file_expected" #1个文件测试期望
ONE_FILE_ACTUAL = POINT1_FOLDER + "/one_file_actual" #1个文件测试实际
TWO_FILES_EXPECTED = POINT1_FOLDER + "/two_files_expected" #2个文件测试期望
TWO_FILES_ACTUAL = POINT1_FOLDER + "/two_files_actual" #2个文件测试实际
THREE_FILES_EXPECTED = POINT1_FOLDER + "/three_files_expected" #3个文件测试期望
THREE_FILES_ACTUAL = POINT1_FOLDER + "/three_files_actual" #3个文件测试实际
NOT_AGENT_EXPECTED = POINT1_FOLDER + "/not_java_agent_log_expected" #非java-agent日志期望
NOT_AGENT_ACTUAL = POINT1_FOLDER + "/not_java_agent_log_actual" #非java-agent日志实际

RESULT_MSG = "test from: " #结果信息
RANDOM_PARAMS = RandomParams(1, 4, 10, 10, 100, 100, 5, 5) #随机参数


def test_from(dic):
    """测试from
    
    Args:
        dic -- 单词词典
    """

    create_folder(POINT1_FOLDER)
    create_file(PT1_RESULT_CMP)
    
    test_empty_directory()
    test_empty_file()
    one_expected_list = test_one_file(dic)
    two_expected_list = test_two_files(dic, one_expected_list)
    test_three_files(dic, two_expected_list)
    test_not_java_agent_log(dic)
    
def test_empty_directory():
    """测试空文件夹"""
    
    #准备测试数据
    clear_folder(EMPTY_FOLDER)
    create_folder(EMPTY_FOLDER)
    
    #创建期望结果
    create_file(EMPTY_DIR_EXPECTED)
    expected_list = []
    
    #运行jql
    test_jql = "from %s \ninto %s;" % (EMPTY_FOLDER, EMPTY_DIR_ACTUAL) 
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "empty directory", test_jql, result, cmp_msg, PT1_RESULT_CMP)
    
def test_empty_file():
    """测试空文件"""
    
    #准备测试数据
    create_file(EMPTY_LOG)
    
    #创建期望结果
    create_file(EMPTY_FILE_EXPECTED)
    expected_list = []
    
    #运行jql
    test_jql = "from %s \ninto %s;" % (EMPTY_LOG, EMPTY_FILE_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "empty file", test_jql, result, cmp_msg, PT1_RESULT_CMP)
        
def test_one_file(dic):
    """测试一个文件
    
    Args:
        dic -- 单词词典
    Return:
        expected list -- 期望结果
    """
    
    #准备测试数据
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG1)
    
    #创建期望结果
    item_list = block_list_2_JqlItem_list(block_list)
    expected_list = select_columns(item_list)
    write_select_list(ONE_FILE_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "from %s \ninto %s;" % (LOG1, ONE_FILE_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "one file", test_jql, result, cmp_msg, PT1_RESULT_CMP)
    
    return expected_list[:]
    
def test_two_files(dic, one_expected_list):
    """测试两个文件
    
    Args:
        dic -- 单词词典
        one_expected_list -- 单文件期望结果，用于生成期望结果
    Return:
       expected list -- 期望结果
    """
    
    # 准备测试数据
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG2)
    
    # 创建期望结果
    item_list = block_list_2_JqlItem_list(block_list)
    expected_list = select_columns(item_list)
    expected_list.extend(one_expected_list)
    write_select_list(TWO_FILES_EXPECTED, expected_list)
    
    # 运行jql
    test_jql = "from %s, %s\ninto %s;" % (LOG2, LOG1, TWO_FILES_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    # 比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list) 
    handle_result(RESULT_MSG + "two files", test_jql, result, cmp_msg, PT1_RESULT_CMP)
    
    return expected_list[:]
     
def test_three_files(dic, two_expected_list):
    """测试三个文件
    
    Args:
        dic -- 单词词典
        two_expected_list -- 双文件期望结果，用于生成期望结果
    Return:
        expected list -- 期望结果
    """
   
    #准备测试数据
    block_list = random_java_agent_log(dic, RANDOM_PARAMS, LOG3)
    
    #创建期望结果
    item_list = block_list_2_JqlItem_list(block_list)
    expected_list = select_columns(item_list)
    expected_list.extend(two_expected_list)
    write_select_list(THREE_FILES_EXPECTED, expected_list)
    
    #运行jql
    test_jql = "from %s, %s, %s\ninto %s;" % (LOG3, LOG2, LOG1, THREE_FILES_ACTUAL)
    actual_list = executeQuery(test_jql, False)
    
    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "three files", test_jql, result, cmp_msg, PT1_RESULT_CMP)
    
def test_not_java_agent_log(dic):
    """测试非java-agent日志"""
    
    #准备测试数据
    with io.open(NOT_AGENT_EXPECTED, 'w') as fd:
        for e in dic:
            fd.write(e)
    
    #创建期望结果
    expected_list = []
    
    #运行jql
    test_jql = "from %s \ninto %s;" % (NOT_AGENT_EXPECTED, NOT_AGENT_ACTUAL)
    actual_list = executeQuery(test_jql, False)

    #比较结果并写入文件
    result, cmp_msg = cmp_select_list(expected_list, actual_list)
    handle_result(RESULT_MSG + "not java agent log", test_jql, result, cmp_msg, PT1_RESULT_CMP)
    

def append_result_file(path, msg):
    """追加结果文件内容
    
    Args:
        path -- 路径
        msg -- 消息
    """
    
    with io.open(path, 'a') as fd:
        fd.write(msg) 
        fd.write("\n") 
        
