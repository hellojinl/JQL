#coding=utf-8

import sys, os
sys.path.append(os.getcwd() + "/../../src/")

import unittest, JQLCore, JQL 

class JQLTest(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass     
    
    def testisFloat(self):
        """test isFloat"""
        
        self.assertEqual(JQLCore.isFloat(''), False)
        self.assertEqual(JQLCore.isFloat('abc'), False)
        self.assertEqual(JQLCore.isFloat('0'), True)
        self.assertEqual(JQLCore.isFloat('-0'), True)
        self.assertEqual(JQLCore.isFloat('+0'), True)
        self.assertEqual(JQLCore.isFloat('0.'), True)
        self.assertEqual(JQLCore.isFloat('0.0'), True)
        self.assertEqual(JQLCore.isFloat('.1'), True)
        self.assertEqual(JQLCore.isFloat('-.1'), True)
        self.assertEqual(JQLCore.isFloat('2'), True)
        self.assertEqual(JQLCore.isFloat('+2'), True)
        self.assertEqual(JQLCore.isFloat('-2'), True)
        self.assertEqual(JQLCore.isFloat('2.0'), True)
        self.assertEqual(JQLCore.isFloat('-2.0'), True)
        self.assertEqual(JQLCore.isFloat('2e10'), True)
        self.assertEqual(JQLCore.isFloat('-2e10'), True)
        self.assertEqual(JQLCore.isFloat('2e-10'), True)
        self.assertEqual(JQLCore.isFloat('-2e-10'), True)
    
    def testisOperator(self):
        """test isOperator"""
        
        self.assertEqual(JQLCore.isOperator('>'), True)
        self.assertEqual(JQLCore.isOperator('>='), True)
        self.assertEqual(JQLCore.isOperator('<'), True)
        self.assertEqual(JQLCore.isOperator('<='), True)
        self.assertEqual(JQLCore.isOperator('='), True)
        self.assertEqual(JQLCore.isOperator('!='), True)
        self.assertEqual(JQLCore.isOperator('and'), True)
        self.assertEqual(JQLCore.isOperator('or'), True)
        self.assertEqual(JQLCore.isOperator('#'), True)
        self.assertEqual(JQLCore.isOperator('('), True)
        self.assertEqual(JQLCore.isOperator(')'), True)
        self.assertEqual(JQLCore.isOperator('abc'), False)
        self.assertEqual(JQLCore.isOperator(''), False)
        self.assertEqual(JQLCore.isOperator(' '), False)
    
    def testcompute(self):
        """test compute"""
        
        self.assertEqual(JQLCore.compute('2', '>', '1'), True)
        self.assertEqual(JQLCore.compute('2', '>', '11'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '>', '1970-01-01 12:00:11'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '>', '1970-01-01 12:00:02'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:01', '>', '1970-01-01 12:00:02'), False)
        self.assertEqual(JQLCore.compute('abc', '>', 'def'), False)
        self.assertEqual(JQLCore.compute('def', '>', 'abc'), True)
        
        self.assertEqual(JQLCore.compute('1', '>=', '0'), True)
        self.assertEqual(JQLCore.compute('11', '>=', '2'), True)
        self.assertEqual(JQLCore.compute('2', '>=', '11'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '>=', '1970-01-01 12:00:11'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '>=', '1970-01-01 12:00:02'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:01', '>=', '1970-01-01 12:00:02'), False)
        self.assertEqual(JQLCore.compute('abc', '>=', 'def'), False)
        self.assertEqual(JQLCore.compute('def', '>=', 'abc'), True)
        self.assertEqual(JQLCore.compute('abc', '>=', 'abc'), True)
    
        self.assertEqual(JQLCore.compute('2', '<', '1'), False)
        self.assertEqual(JQLCore.compute('2', '<', '11'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '<', '1970-01-01 12:00:11'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '<', '1970-01-01 12:00:02'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:01', '<', '1970-01-01 12:00:02'), True)
        self.assertEqual(JQLCore.compute('abc', '<', 'def'), True)
        self.assertEqual(JQLCore.compute('def', '<', 'abc'), False)
        
        self.assertEqual(JQLCore.compute('1', '<=', '0'), False)
        self.assertEqual(JQLCore.compute('11', '<=', '2'), False)
        self.assertEqual(JQLCore.compute('2', '<=', '11'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '<=', '1970-01-01 12:00:11'), True)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:11', '<=', '1970-01-01 12:00:02'), False)
        self.assertEqual(JQLCore.compute('1970-01-01 12:00:01', '<=', '1970-01-01 12:00:02'), True)
        self.assertEqual(JQLCore.compute('abc', '<=', 'def'), True)
        self.assertEqual(JQLCore.compute('def', '<=', 'abc'), False)
        self.assertEqual(JQLCore.compute('abc', '<=', 'abc'), True)
        
        self.assertEqual(JQLCore.compute('2', '=', '11'), False)
        self.assertEqual(JQLCore.compute('2', '=', '2'), True)
        self.assertEqual(JQLCore.compute('abc', '=', 'abc'), True)
        self.assertEqual(JQLCore.compute('abc', '=', 'cba'), False)
        
        self.assertEqual(JQLCore.compute('2', '!=', '11'), True)
        self.assertEqual(JQLCore.compute('2', '!=', '2'), False)
        self.assertEqual(JQLCore.compute('abc', '!=', 'abc'), False)
        self.assertEqual(JQLCore.compute('abc', '!=', 'cba'), True)
          
        self.assertEqual(JQLCore.compute(True, 'and', False), False)
        self.assertEqual(JQLCore.compute(True, 'and', True), True)
        
        self.assertEqual(JQLCore.compute(True, 'or', False), True)
        self.assertEqual(JQLCore.compute(False, 'or', False), False)
        
        self.assertEqual(JQLCore.compute('2.0', '>', '1'), True)
        self.assertEqual(JQLCore.compute(2.0, '>', '1'), True)
        self.assertEqual(JQLCore.compute('2.0', '>', 1), True)
        self.assertEqual(JQLCore.compute(2.0, '>', 1), True)
    
    def testLogicalExpression(self):
        """test LogicalExpression"""
        
        le = JQLCore.LogicalExpression("1>3")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("1>3.0")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("-1>-3.0")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("((1)>(3))")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("3>1")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("((3)>(1))")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("3<1")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("3 > 1 or 2 = 2")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("3 > 1 and 2 = 2")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("3 > 1 and 2 = 1")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("3 > 1 and 2!=1")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("3 > 1 and 2=1 or str = str")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("3 > 1 and (2=1 or str = str)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("(1 > 3 or abc=abc) and (2=1 or dce<=f)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("(1 > 3 or abc=abc) and (2=1 or 1970-01-01 12:00:11>1970-01-01 12:00:01)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("(1 > 3 or abc=abc) and (2=1 or 1970-02-01 12:00:11>1970-01-31 12:00:01)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("(1 > 3 and abc=abc) or (2=1 and dce<=f)")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("(1 > 3 and abc=abc) or (2=2 and dce<=f)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("((1 > 3 or 3 >= 2 )and abc=abc) or (2=1 and dce<=f)")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("com.thunisoft.susong51.sfks.service.getter.people.impl.ZxPeopleGetter=com.thunisoft.susong51.sfks.service.getter.people.impl.ZxPeopleGetter")
        self.assertEqual(le.result(), True)
        
        le = JQLCore.LogicalExpression("com.thunisoft.susong51.sfks.service.params.jsp.AjblWrit$TableOperation=com.thunisoft.susong51.sfks.service.getter.people.impl.ZxPeopleGetter")
        self.assertEqual(le.result(), False)
        
        le = JQLCore.LogicalExpression("")
        self.assertRaises(Exception, le.result)
            
        le = JQLCore.LogicalExpression("1>3>2")
        self.assertRaises(Exception, le.result)

    def testJqlFile(self):
        """test JqlFile"""
        
        jf1 = JQLCore.JqlFile("1.txt")
        jf2 = JQLCore.JqlFile("1.txt")
        self.assertEqual(jf1==jf2, True)
        
        jf2 = JQLCore.JqlFile("2.txt")
        self.assertEqual(jf1==jf2, False)
        
        jf2 = JQLCore.JqlFile("1.txt", "gbk")
        self.assertEqual(jf1==jf2, False)
             
    def testcheckJQL(self):
        """test checkJQL"""
        
        jql = "from ../agentLog2/agent.2015-10-26.log"
        cr = JQL.checkJQL(jql)
        self.assertIsNone(cr)
        
        jql = " select avg time, time, count, method, class, start time, end time \
                from ../agentLog \
                where (avg time >= 100 and avg time <= 1000) and count > 2 \
                    and (time < 400 or time > 1000) \
                    and (start time >= 2015-10-24 16:27:15 and start time <= 2015-10-26 14:41:08) \
                order by avg time desc, count desc \
                limit 200 \
                into result"
                
        cr = JQL.checkJQL(jql)
        self.assertIsNone(cr)
        
        jql = "from ../agentLog2/agent.2015-10-26.log select time"
        self.assertRaises(JQLCore.JqlParseException, JQL.checkJQL, jql)
        
    def testparseJQL(self):
        """test parseJQL"""
        
        jql = "from utest.py"
        r = JQL.parseJQL(jql)
        ex = JQLCore.QueryDefinition(JQLCore.AgentLogTableTitles, [JQLCore.JqlFile("utest.py")])
        self.assertEqual(r==ex, True)

        jql = " select avg time, time, count, method, class, start time, end time \
                from utest.py \
                where (avg time >= 100 and avg time <= 1000) and count > 2 and (time < 400 or time > 1000) and (start time >= 2015-10-24 16:27:15 and start time <= 2015-10-26 14:41:08) \
                order by avg time desc, count desc \
                limit 200 \
                into result"
        r = JQL.parseJQL(jql)
        ex = JQLCore.QueryDefinition(
                ["avg time", "time", "count", "method", "class", "start time", "end time"],
                [JQLCore.JqlFile("utest.py")],
                "(avg time >= 100 and avg time <= 1000) and count > 2 and (time < 400 or time > 1000) and (start time >= 2015-10-24 16:27:15 and start time <= 2015-10-26 14:41:08)",
                ["avg time", "count"],
                ["desc", "desc"],
                200,
                "result"
                )
        self.assertEqual(r==ex, True)
         
        jql = "select from utest.py"
        self.assertRaises(JQLCore.JqlParseException, JQL.parseJQL, jql)
        
        jql = " select avg time, time, count, method, class, start time, end time \
                from utest.py \
                where (avg time >= 100 and avg time <= 1000) and count > 2 and (time < 400 or time > 1000) and (start time >= 2015-10-24 16:27:15 and start time <= 2015-10-26 14:41:08) \
                order by avg time desc, count desc \
                limit  \
                into result"
        self.assertRaises(JQLCore.JqlParseException, JQL.parseJQL, jql)
        
if __name__ == '__main__':
    unittest.main()