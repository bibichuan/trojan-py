#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
## 导入当前目录包
sys.path.append('.')
import urllib.request
import base64
import json
import urllib.parse as urlparse
import shutil
import subprocess
import re
import os
## 多线程
import threading
import queue

import platform

## 导入邮件发送
import qqmail
## 自定义配置
import config 

## 解析base64字符串
def base64StrFun(base64Str):
    # print(base64Str)
    try:
        base64Str=base64.urlsafe_b64decode(base64Str)
    except Exception as es1:
        try:
            lens = len(base64Str)
            lenx = lens - (lens % 4 if lens % 4 else 4)
            base64Str= base64.decodestring(base64Str[:lenx])
        except Exception as es2:
            missing_padding = len(base64Str) % 4
            if missing_padding != 0:
                base64Str += b'='* (4 - missing_padding)
            base64Str= base64.urlsafe_b64decode(base64Str)

    return base64Str
## 获取订阅内容，并处理
def getSubscribeContent(url):
    try:

        ## 获取订阅地址
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        ## v2ray订阅地址
        subscribe_url = url

        req = urllib.request.Request(url=subscribe_url, headers=headers)
        return_content = urllib.request.urlopen(req,timeout=10).read()


        ## 获取内容成功
        # print(return_content)
        print('获取内容成功')

        ## 特殊处理，如果return_content中有下划线，就进行分割处理
        return_content=return_content.split(b'_')

        share_links=[]
        # 解析订阅地址内容
        if len(return_content) > 1 :
            for res in return_content:
                resStr=base64StrFun(res)
                share_links.append(resStr.replace(b'\n', b'').replace(b'\r', b'').replace(b' ',b''))

            links=b''.join(share_links)
            share_links.clear()
            # print(links)gi
            links=bytes.decode(links)
            
            ## 无法使用正则表达式,通过substr方式获取字符串
            strIndex=0
            while strIndex >= 0 :
                strIndex=links.find('trojan',1)
                if strIndex == -1 :
                    strIndex=links.find('ssr',1)
                if strIndex == -1 :
                    strIndex=links.find('vmess',1)

                if strIndex >0:
                    tempStr=links[0:strIndex]
                    links=links[strIndex:]
                    share_links.append(tempStr)
        else:
            result=base64StrFun(return_content[0])
            share_links=result.splitlines()

        for share_link in share_links:
            if isinstance(share_link,bytes):
                share_link=bytes.decode(share_link)

            url=share_link.split("://")
            ## 解析协议
            scheme=url[0]
            if scheme != "trojan" :
                continue
            ## 解析内容url
            net=url[1]
            net=urlparse.unquote(net)
            
            netParse=urlparse.urlparse(net)

            ## 放入队列
            ipqueue.put(netParse)          

        ## print(configs)
        ping_threading()
        ## 将结果写入文件中
        with open("trojan_record.json","w",encoding="utf-8") as dump_f:
            json.dump(allNode,dump_f,ensure_ascii=False,sort_keys=True, indent=4,separators=(',', ':'))
        
        print('解析协议成功')
        return configs
    except TimeoutError:
        print('getSubscribeContent链接超时')
        return None
    except Exception as e :
        print('getSubscribeContent',e)
        return None

## 生成配置文件
def configFile(config):

    ##读取配置文件
    load_dict=None
    try:
        with open("./trojan_config.json",'r+') as load_f:
            
            load_dict = json.load(load_f)
                    
            if load_dict :
                load_dict['remote_addr']=config['remote_addr']
                load_dict['password']=config['password']
                load_dict['remote_port']=config['remote_port']
                load_dict['name']=config['name']
            ## print(load_dict)
            ## 将指针移到文件开头
            load_f.seek(0)
            load_f.truncate()

            json.dump(load_dict,load_f,ensure_ascii=False,sort_keys=True, indent=4, separators=(',', ':'))

        print('修改配置文件成功')
        pass
    except Exception as e:
        print('configFile')
        print(e)
        pass

    return

## 测试网络延迟
def shend_icmp_packet(ip_address,times):
    try:
        response=''
        net={}
        sysstr = platform.system()
        if (sysstr =="Windows"):
            response = os.popen('ping -n ' + str(times) + ' '+ ip_address).read()
            net=windows_ping_text(response)
        else:
            response = os.popen('ping -c ' + str(times) + ' '+ ip_address).read()
            net=linux_ping_text(response)

        print(ip_address+":",net)

        return net
    except Exception as e:
        print(ip_address+":ping exec error",e)
        return {}

## 处理linux系统下的丢包率等问题
def linux_ping_text(response):
    min='999'
    avg='999'
    max='999'
    lost='100'
    try:
        # 取出丢包率
        lost = response[response.rindex(',',0,response.index("%"))+1:response.index("%")].strip()
        ## 如果丢包率达到100，则丢弃
        if lost == '100' :
            return -1
        #取出指定的延时字符串
        try:
            res = list(response)
        except :
            print(response)
        index = 0
        count = 0
        for r in res:
            count += 1
            if r == "=" :
                index = count
        response = response[index + 1:-4]

        # 取出执行的延迟
        i = 0
        j = []
        res1 = list(response)
        for r in res1:
            i += 1
            if r == "/" :
                j.append(i)

        avg = response[j[0]:j[1]-1]

        min = response[:j[0]-1]
        avg = response[j[0]:j[1]-1]
        max = response[j[1]:j[2]-1]
    except Exception as e:
        print('linux_ping_text')
        print(e)   

    net={
        'min':min,
        'avg':avg,
        'max':max,
        'lost':lost
    }
    return net

def windows_ping_text(response):

    min='999'
    avg='999'
    max='999'
    lost='100'
    try:
        # 取出丢包率
        lost = response[response.rindex('(',0,response.index('%'))+1:response.index('%')].strip()
        if lost == '100' :
            return -1
        if response.find('最短 =') > 0 :
            min=response[response.find('最短 =')+5:response.find('ms',response.find('最短 ='))]
            max=response[response.find('最长 =')+5:response.find('ms',response.find('最长 ='))]
            avg=response[response.find('平均 =')+5:response.find('ms',response.find('平均 ='))]
    except Exception as e:
        print('windows_ping_text')
        print(e)

    net={
        'min':min,
        'avg':avg,
        'max':max,
        'lost':lost
    }
    return net

## 订阅地址
configs = None
## 全部地址
allNode=[]
## 网络延迟
minRtt=400
## ip队列
ipqueue=queue.Queue()

## 多线程ping
def queue_ping():
    while not ipqueue.empty():
        global configs
        ## 全部地址
        global allNode
        ## 网络延迟
        global minRtt

        netParse = ipqueue.get()
        ## 改造相关内容
        tempNode={}

        netpath=""
        netquery=""

        # print(netParse)
        
        ## 服务器地址,如果服务器地址中的query为空,netParse为下列形式，需要特殊处理
        ## (scheme='', netloc='', path='sdfascsdf@45.88.90.137:224allowInsecure=1&peer=ded237.ovod.me', params='', query='', fragment='年费·T·德国V·商务·237·1000M·空闲')
        ## 正常的是这样的
        ## ParseResult(scheme='', netloc='', path='qsdfsdfp@118.99.224.161:216allowInsecure=1&peer=jpdcl61ddd.ovod.me', params='', query='', fragment='年费·T·日本C·原生·161·200M·空闲')
        ## 还有
        ## ParseResult(scheme='', netloc='', path='sdfccsdf@hkgg5dddss.ovod.me:8443', params='', query='', fragment='年费·T·高速 · 香港 G · 51·1000M·空闲')

        ## 去掉体验节点
        # if netParse.fragment.find('体验') >= 0 or netParse.fragment.find("订阅")>=0:
        #     return

        ## 根据协议不同，需要从不同的地方取出url和端口号、以及密码，有的地址在query中，有的在path后面allowInsecure=1，有的直接在密码的后面

        if netParse.query == '' :
            tempUrl=netParse.path
            
            ## 针对没有allowInsecure的进行特殊处理
            if tempUrl.find('allowInsecure')>=0:
                netquery=tempUrl[tempUrl.find('allowInsecure'):]
                netpath=tempUrl[:tempUrl.find('allowInsecure')]
            else:
                netpath=tempUrl
                netquery=''
        else:
            netquery=netParse.query
            netpath=netParse.path

        ## 解析查询字符串
        url=urlparse.parse_qs(netquery)
        ## 密码
        path=str(netpath).split('@')
        password=path[0]
        
        ## 去掉网站简介等节点
        if password=='12' or password == 'vip' or password == 'web' :
            return
        tempNode['password']=[password]
        ## 端口
        port=path[1].split(':')
 

        tempNode['remote_port']=int(port[1]) if int(port[1])>80 else 443

        tempNode['ip']=port[0]
        remote_addr=port[0]
        
        if 'peer' in url:
            remote_addr=url['peer'][0]
        tempNode['remote_addr']=remote_addr

        tempNode['name']=netParse.fragment
        ## rtt=pingIp(remote_addr)
        rtt=shend_icmp_packet(remote_addr,10)

        tempNode['rtt']=rtt

        if (rtt != -1) and ('avg' in rtt):
           
            lost=float(rtt['lost'])
            avg=float(rtt['avg'])
            rt=lost+avg

            allNode.append(tempNode)
            ## 测试最快节点,对体验节点和订阅专享节点不参与配置
            if rt <= minRtt and (netParse.fragment.find('体验') < 0 and netParse.fragment.find("订阅")< 0):
                # print(netParse)
                configs=tempNode 
                minRtt=rt 

## 开启多线程
def ping_threading():
    print('多线程测试网络延迟')
    threads = []
    WORD_THREAD=50
    for i in range(WORD_THREAD):
        thread = threading.Thread(target=queue_ping)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    ## 停止代理
    ## subprocess.check_call(['sudo','systemctl','stop','trojan'])

    trojanUrl=config.suburl
    ## 获取订阅内容
    getSubscribeContent(trojanUrl)

    ## 全局配置
    if configs :
        ## 修改配置文件
        configFile(configs)

        ## 发送邮件
        qqmail.send_mail("")

        sysstr = platform.system()
        print(sysstr)
        if (sysstr =="Linux"):
            
            # 判断用户以管理源权限运行
            if os.getuid() == 0 :
                # 复制文件
                src='trojan_config.json'
                dist='/etc/trojan/config.json'
                shutil.copyfile( src, dist)
                subprocess.check_call(['sudo','cp',src,dist])
                print('文件复制成功')


                print('开启应用程序')
                subprocess.check_call(['sudo','systemctl','stop','trojan'])
                subprocess.check_call(['sudo','systemctl','restart','trojan'])
                print('成功开启应用程序')
            else:
                print('请以管理员身份运行脚本！！！')

    

