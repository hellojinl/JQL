# JQL
用途：通过查询语句JQL来分析java-agent生成的日志文件，以表格的形式返回结果，可输出到文件或屏幕上
语言及版本：python3.4.3+

JQL语法说明：
[select title1[, title2, title3, ... ]]
<from file1|dir1 [encoding1][, file2|dir2 [encoding2], ... ]>
[where logical expression]
[order by title1 [asc|desc][, title2 [asc|desc], ...]]
[limit integer]
[into filename]

[]可选，<>必选，具体例子请看Examples

关键字：select, from, where, order by, limit, into
关键字必须小写，且关键字不能出现在逻辑表达式中
title取值范围：[avg time, time, count, method, class, start time, end time]
avg time -- 类方法调用的平均时间
time -- 类方法调用的总时间
count -- 类方法调用的总次数
method -- 方法名
class -- 类名
start time -- 时间段开始
end time -- 时间段结束
encoding为文件或文件夹（下所有文件）的编码，默认值为utf-8
logical expression为逻辑表达式支持and,or,=,!=,>,>=,<,<=,()逻辑运算符，不支持+,-,*,/,%等算数运算符，不支持短路算法
如果jql包括了关键字into，结果将只会保存到指定的文件中，否则将输出到命令行

目录结构
src  --  源代码
test  --  测试
...auto  --  自动化测试
...performance  --  性能测试
...unit  --  单元测试

源代码阅读索引：
1. jql执行算法在JQL.executeQuery
2. 逻辑表达式算法在JQLCore.LogicalExpression
3. 多文件排序算法在JQL.mergeSort
4. 输出结果方法在JQL.drawTable
5. 自动化测试在auto_test.main
6. 性能测试在performance.py

如何运行JQL？
1. 确保安装了python，并正确配置了环境变量
2. 在命令行将目录切换到JQL/src/
3. 在命令行输入jql即可


如何运行JQL的自动化测试？
1. 在命令行将目录切换到JQL/test/auto
2. 在命令行输入auto_test

测试数据哪里来？
运行自动化测试后会在当前目录生成auto_test_result
在auto_test_result/目录下，搜索agentLog（有多个），里边的文件就是测试数据

使用举例
在JQL/src/打开命令行，输入jql
Please input JQL
input 'q!' for quit, input ';' for execute jql

>>> select avg time, time, count, method, class, start time, end time
>>>  from ../test/auto/auto_test_result/test_select/agentLog
>>>  where count > 100
>>>  order by avg time desc, time desc, count desc
>>>  limit 10;
+------------+------------+------------+-------------------------------------+------------------------------------------------------------------------------------------------------+----------------------+----------------------+
| avg time   | time       | count      | method                              | class                                                                                                | start time           | end time             |
+------------+------------+------------+-------------------------------------+------------------------------------------------------------------------------------------------------+----------------------+----------------------+
| 81         | 1695238    | 20862      | filmpersonwasdanieltowith           | which.bond.the.and.and.want.Happy                                                                    | 2015-12-24 23:59:05  | 2015-12-25 00:20:05  |
| 81         | 1695170    | 20702      | filmpersonwasdanieltowith           | which.bond.the.and.and.want.Happy                                                                    | 2015-12-24 23:34:05  | 2015-12-24 23:50:05  |
| 61         | 3194804    | 51949      | donpahlajcutthosego                 | which.bond.the.and.and.want.Happy                                                                    | 2015-12-24 23:59:05  | 2015-12-25 00:20:05  |
| 61         | 3194678    | 51826      | donpahlajcutthosego                 | which.bond.the.and.and.want.Happy                                                                    | 2015-12-24 23:34:05  | 2015-12-24 23:50:05  |
| 49         | 3114164    | 62898      | tooenoughit                         | are.who.born.want.smiling.Lifeuntil                                                                  | 2015-12-24 23:55:05  | 2015-12-25 00:06:05  |
| 41         | 3598887    | 87369      | necessarilytheirlengthwith          | the.kisses.what.days.To                                                                              | 2015-12-24 23:59:05  | 2015-12-25 00:20:05  |
| 41         | 3598809    | 87249      | necessarilytheirlengthwith          | the.kisses.what.days.To                                                                              | 2015-12-24 23:34:05  | 2015-12-24 23:50:05  |
| 40         | 2950594    | 73680      | sweetpromptedreally                 | want.of.those.People                                                                                 | 2015-12-24 23:55:05  | 2015-12-25 00:06:05  |
| 25         | 2986942    | 118504     | youandboardthemscenespast           | of.they.to.confirmed.With                                                                            | 2015-12-24 23:59:05  | 2015-12-25 00:20:05  |
| 25         | 2986795    | 118474     | youandboardthemscenespast           | of.they.to.confirmed.With                                                                            | 2015-12-24 23:34:05  | 2015-12-24 23:50:05  |
+------------+------------+------------+-------------------------------------+------------------------------------------------------------------------------------------------------+----------------------+----------------------+
tottime: 0.05s

然后可以根据这个表格的结果，有针对性的优化代码
(正确的格式，请点击左上角的"原始文件")
