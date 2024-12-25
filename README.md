h1. Abstract 自动注册程序

项目地址：https://abs.xyz/

h2. 问题描述
需要一个自动化工具来批量注册 Abstract 账号，使用 Gmail 别名实现多账号注册。

h2. 解决方案
使用 Python + Selenium 实现自动化注册流程，支持多线程并发注册。

h2. 环境需求
* Python 3.7+
* Chrome 浏览器
* Gmail 账号（需开启两步验证）

h2. 安装步骤

h3. 1. 依赖安装
<pre>
pip install selenium colorama configparser
</pre>

h3. 2. Gmail 配置
# 开启两步验证
** 访问：https://myaccount.google.com/security
** 找到"2-Step Verification"并开启

# 获取应用专用密码
** 访问：https://myaccount.google.com/security
** 找到"App passwords"
** 选择"Other (Custom name)"
** 生成16位密码

h3. 3. 配置文件设置
<pre>
[Email]
base_email = your.email@gmail.com
password = xxxx xxxx xxxx xxxx

[Settings]
success_log = registered_accounts.txt
threads = 3
register_count = 2
</pre>

h2. 使用方法

h3. 运行程序
<pre>
python auto_register.py
</pre>

h3. 日志颜色说明
* *绿色* - 成功信息
* *红色* - 错误信息
* *黄色* - 警告信息
* *蓝色* - 标题信息
* *青色* - 进度信息

h2. 注意事项
# 避免频繁注册操作
# 及时备份注册成功的账号信息
# 定期检查 Gmail 安全设置
# 遵守使用条款

h2. 相关文件
* @auto_register.py@ - 主程序
* @config.ini@ - 配置文件
* @registered_accounts.txt@ - 注册记录

h2. 常见问题

h3. Gmail 登录失败
* 检查应用专用密码是否正确
* 确认两步验证是否已开启
* 检查账号安全设置

h3. 验证码获取失败
* 检查邮箱设置
* 增加等待时间
* 确认网络连接

h3. 浏览器问题
* 更新 Chrome 浏览器
* 更新 ChromeDriver
* 检查网络代理设置

h2. 版本历史
* v1.0.0 (2024-03-25)
** 初始版本发布
** 支持多线程注册
** 配置文件支持
** 日志记录功能 

官方频道：https://t.me/a645645654
官方客服：@kexuejia3