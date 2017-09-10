#coding=utf-8
import sys, os
sys.path.append(os.getcwd() + "/../../src/")
sys.path.append(os.getcwd() + "/../auto/")

from auto_core import random_java_agent_log, generate_dictionary, RandomParams
from JQL import executeQuery

RANDOM_PARAMS = RandomParams(50, 70, 40, 30, 100, 100, 5, 5) #随机参数

LARGE_LOG = "large.log"

#profile结果说明:
#ncalls -- 函数被调用次数
#tottime -- 函数总计运行时间，除去函数中调用函数的运行时间
#percall -- 函数运行一次的平均时间，等于tottime/ncalls
#cumtime -- 函数总计运行时间，含调用的函数运行时间
#percall -- 函数运行一次的平均时间，等于cumtime/ncalls
#filename:lineno(function) -- 函数所在的文件名，函数的行号，函数名

if __name__ == "__main__":
    import cProfile, pstats, io
    
    dic = generate_dictionary()    
    random_java_agent_log(dic, RANDOM_PARAMS, LARGE_LOG)
    
    pr = cProfile.Profile()
    pr.enable()
    pr.run("""executeQuery(' \
        select avg time, time, count, method, class, start time, end time \
        from %s \
        where count > 2 \
            and (time < 400 or time > 1000)  \
            and start time >= 2015-10-24 00:00:00 \
        order by avg time desc, count desc \
        limit 200; \
        ', True)"""%(LARGE_LOG))
    pr.disable()
    sortby = 'cumtime'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()
    
    
    
