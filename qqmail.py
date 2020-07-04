#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
## 导入当前目录包
sys.path.append('.')
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import json

## 自定义配置
import config 
 
# 第三方 SMTP 服务
mail_host="smtp.qq.com"  #设置服务器
mail_user=config.mail_user    #用户名
mail_pass=config.mail_pass   #口令 
 
 
sender = config.sender
receivers = config.receivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
 
mail_msg="""
<!DOCTYPE>
<html>
<head>
<style type="text/css">
body,html{
    text-algin:center
    position:absolute;
    margin:0;
    padding:0;
    width:100%;
}
table.gridtable {
    font-family: verdana,arial,sans-serif;
    font-size:11px;
    color:#333333;
    border-width: 1px;
    border-color: #666666;
    border-collapse: collapse;
    width:100%;
}
table.gridtable th {
    border-width: 1px;
    padding: 8px;
    border-style: solid;
    border-color: #666666;
    background-color: #dedede;
}
table.gridtable td {
    border-width: 1px;
    padding: 8px;
    border-style: solid;
    border-color: #666666;
    background-color: #ffffff;
}
</style>
</head>
<body>
<table border="0" class="gridtable">
  <thead>
    <tr>
      <th>名称</th>
      <th>地址</th>
      <th>端口</th>
      <th>密码</th>
      <th>延迟</th>
    </tr>
  </thead>
  <tbody>
"""
 

def send_mail(send_msg):
    ## 打开文件
    global mail_msg

    with open("./trojan_record.json",'r+',encoding="utf-8") as t_json:
        trojan_array = json.load(t_json)
        ## 循环读取数据，构造表格
        for item in trojan_array:
            mail_msg+='<tr>'
            mail_msg+='<td>'+item['name']+'</td>'
            mail_msg+='<td>'+item['remote_addr']+'</td>'
            mail_msg+='<td>'+str(item['remote_port'])+'</td>'
            mail_msg+='<td>'+item['password'][0]+'</td>'
            mail_msg+='<td>'+str(item['rtt'])+'</td>'
            mail_msg+='</tr>'
        ## 完善表格
        mail_msg+='</tbody></table></body></html>'
    print(mail_msg)
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header("bibichuan", 'utf-8')
    message['To'] =  Header("", 'utf-8')
    
    subject = '西部世界订阅地址'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == "__main__":
    send_mail("")