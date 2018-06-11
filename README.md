# python

## 1、lagou
爬取拉勾网运维工程师的岗位信息,new为多线程重构的版本，速度快了N倍
博客地址： https://www.boheyan.cn/pachong-thread.html

## 2、proxy_ip
爬取代理网站 (www.xicidaili.com/nn) 的代理IP，并检测代理IP的可用性。
全部用的多线程，其中检测IP可用性，速度较慢，200个IP，用时17秒左右。应该用协程
的方式会好一些，下次改进。

## 3、inotify
用python实现了两台服务器间文件夹实时同步，日志输出。用到了paramiko，watchdog，logging等模块。
博客地址： https://www.boheyan.cn/file-sync.html

## 4、game
这是图书<python编程从入门到实践>中一个打飞机的项目，跟着做了一遍，记录了mac开发pygame的一些坑。
