loophole
========

网站后台攻击全过程演示配套源代码 华理网络攻防课程设计

# 一.设计题目
利用信息采集技术和网站技术模拟网站后台攻击全过程。

# 二.设计目的
通过这个课程设计，用最简单的方式演示网站攻击全过程。
重现经典的网站漏洞：SQL漏洞以及弱密码漏洞。
探索SQL漏洞的攻防策略。
通过编程方式实现暴力口令破解。

# 三.设计设备和环境
这个课程设计演示的环境：
攻击者采用了Ubuntu12.04操作系统。
攻击者计算机中用nmap、Chrome、Wireshark、python软件作为主要攻击工具。
被攻击站点架设在FreeBSD9.2操作系统的虚拟机中，采用Tornado框架和SQLite3数据库。
被攻击主机系统需要安装python解释器以及Tornado网站框架，以及SQLite3数据库。
攻击者的计算机与被攻击主机通过Virtual Box虚拟机软件中的Host-Only方式组建网络。

具体演示步骤参考课程设计报告（暂时不开放）