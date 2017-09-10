#coding=utf-8

#自动化测试
#依次测试from、select、order by、limit、where

import io

from auto_core import RESULT_FOLDER, SUMMARY, create_file, generate_dictionary, random_class_list
from point1_test_from import test_from, PT1_RESULT_CMP
from point2_test_select import test_select, PT2_RESULT_CMP
from point3_test_order_by import test_order_by, PT3_RESULT_CMP
from point4_test_limit import test_limit, PT4_RESULT_CMP
from point5_test_where import test_where, PT5_RESULT_CMP

def summarize():
    """总结"""
    
    result = []
    
    with io.open(PT1_RESULT_CMP, 'r') as fd:
        for line in fd:
            result.append(line)

    with io.open(PT2_RESULT_CMP, 'r') as fd:
        for line in fd:
            result.append(line)

    with io.open(PT3_RESULT_CMP, 'r') as fd:
        for line in fd:
            result.append(line)
            
    with io.open(PT4_RESULT_CMP, 'r') as fd:
        for line in fd:
            result.append(line)
            
    with io.open(PT5_RESULT_CMP, 'r') as fd:
        for line in fd:
            result.append(line)
            
    with io.open(SUMMARY, 'w') as fd:
        for line in result:
            fd.write(line)
    
def main():
    #生成字典，用于随机的生成包名，类名
    dic = generate_dictionary()
    
    test_from(dic)
    test_select(dic)
    test_order_by(dic)
    test_limit(dic)
    test_where(dic)
    summarize()
    
if __name__ == "__main__":
    main()
    
