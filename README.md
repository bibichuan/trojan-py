## 配置方式
修改config.py中的参数
``` python
suburl="" # 订阅地址
mail_user=""    #qq邮箱用户名
mail_pass=""   #qq邮箱口令,需要开启SMTP服务
sender = ''  # 发送人
receivers = ['']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
```
## 运行
``` sh
python3 trojan.py
```

在命令行中运行，会生成trojan_record.json文件，文件里面保存了从订阅地址中解析所有连接地址。