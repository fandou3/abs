# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import imaplib
import email
import re
from datetime import datetime, timedelta
import random
import string
from colorama import init, Fore, Style
import configparser
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

# 初始化 colorama
init()

def log_step(message, is_sub=False, status=None):
    """统一的日志输出格式，添加颜色
    status: 'success' (绿色), 'error' (红色), 'warning' (黄色), 'info' (蓝色)
    """
    prefix = "  └─" if is_sub else "►"
    
    # 选择颜色
    color = Fore.WHITE  # 默认白色
    if status == 'success':
        color = Fore.GREEN
    elif status == 'error':
        color = Fore.RED
    elif status == 'warning':
        color = Fore.YELLOW
    elif status == 'info':
        color = Fore.CYAN
        
    print(f"{color}{prefix} {message}{Style.RESET_ALL}")

def log_section(title, status=None):
    """输出分节标题，添加颜色"""
    color = Fore.BLUE  # 默认蓝色
    if status == 'success':
        color = Fore.GREEN
    elif status == 'error':
        color = Fore.RED
        
    print(f"\n{color}{'='*50}")
    print(f"▶ {title}")
    print(f"{'='*50}{Style.RESET_ALL}")

class AbstractRegistration:
    def __init__(self):
        log_section("初始化")
        log_step("启动浏览器...")
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        log_step("浏览器初始化完成", True)
        
    def setup(self):
        log_step("访问目标网站...")
        self.driver.get("https://abs.xyz/")
        time.sleep(1)
        log_step("页面加载完成", True)
        
    def click_join_button(self):
        log_step("点击加入按钮...")
        time.sleep(1)
        self.driver.execute_script('document.querySelector(\'[type="button"]\').click()')
        time.sleep(1)
        log_step("按钮点击完成", True)

    def enter_email(self, email_address):
        log_step(f"输入邮箱: {email_address}")
        email_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[placeholder="Email"]'))
        )
        time.sleep(1)
        email_input.send_keys(email_address)
        time.sleep(1)
        log_step("邮箱输入完成", True)

    def submit_form(self, va):
        print("提交表单...")
        time.sleep(1)
        if va == 1:
            self.driver.execute_script('''
                                       document.querySelectorAll('[type="submit"]')[0].click()
                                   ''')
        else:
            self.driver.execute_script('''
                                               document.querySelectorAll('[type="submit"]')[1].click()
                                           ''')
        time.sleep(1)
        print("表单提交完成")

    def get_verification_code(self, email_address, password):
        try:
            log_section("获取验证码", 'info')
            # 保存当前窗口句柄
            main_window = self.driver.current_window_handle
            
            # 打开新窗口用于解析HTML
            self.driver.execute_script("window.open('about:blank', 'temp');")
            self.driver.switch_to.window("temp")
            
            log_step("连接Gmail邮箱...", False, 'info')
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            log_step("尝试登录...", True, 'info')
            mail.login(email_address, password)
            log_step("登录成功", True)
            mail.select("inbox")

            # 添加重试机制
            max_retries = 3  # 最大重试次数
            for attempt in range(max_retries):
                log_step(f"等待邮件到达 (尝试 {attempt + 1}/{max_retries})...")
                time.sleep(10)  # 等待10秒
                
                log_step(f"搜索邮件: {email_address}")
                # 修改搜索条件，获取所有邮件
                _, messages = mail.search(None, 'ALL', f'FROM "no-reply@abs.xyz"', f'TO "{email_address}"')

                if messages[0]:
                    log_step(f"找到邮件", True)
                    items = messages[0].split()
                    log_step(f"找到 {len(items)} 封邮件", True)

                    # 按时间倒序排序，先处理最新的邮件
                    items = sorted(items, reverse=True)
                    
                    for i in items:
                        resp, msg = mail.fetch(i, "(RFC822)")
                        for response in msg:
                            if isinstance(response, tuple):
                                email_msg = email.message_from_bytes(response[1])
                                
                                if email_msg['to'].lower() != email_address.lower():
                                    continue
                                
                                log_step("邮件信息:", True)
                                log_step(f"发件人: {email_msg['from']}", True)
                                log_step(f"收件人: {email_msg['to']}", True)
                                log_step(f"时间: {email_msg['date']}", True)
                                
                                html_content = None
                                for part in email_msg.walk():
                                    if part.get_content_type() == "text/html":
                                        html_content = part.get_payload(decode=True)
                                        break
                                
                                if html_content:
                                    try:
                                        html_content = html_content.decode('utf-8')
                                    except:
                                        try:
                                            html_content = html_content.decode('latin-1')
                                        except:
                                            log_step("无法解码HTML内容", True)
                                            continue
                                    
                                    log_step("解析验证码...", True)
                                    self.driver.execute_script(f"document.body.innerHTML = `{html_content}`")
                                    verification_code = self.driver.execute_script(
                                        'return document.querySelector("[role=presentation] tbody tr td table tbody tr td table:nth-of-type(2) td table p")?.innerText'
                                    )
                                    
                                    if verification_code:
                                        verification_code = verification_code.strip()
                                        log_step(f"✓ 验证���: {verification_code}", True, 'success')
                                        
                                        # 关闭临时窗口并切回主窗口
                                        self.driver.close()
                                        self.driver.switch_to.window(main_window)
                                        
                                        mail.close()
                                        mail.logout()
                                        return verification_code
                                else:
                                    log_step("未找到HTML内容", True)

                    log_step("未能获取验证码", True, 'error')
                    # 如果没有找到验证码，也要确保关闭临时窗口
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    
                    mail.close()
                    mail.logout()
                    return None
                else:
                    if attempt < max_retries - 1:
                        log_step("未找到邮件，继续等待...", True)
                        continue
                    else:
                        log_step("最终未找到验证邮件", True)
                        return None
            
        except Exception as e:
            # 确保发生错误时也关闭临时窗口
            try:
                self.driver.close()
                self.driver.switch_to.window(main_window)
            except:
                pass
            log_step(f"错误: {str(e)}", True, 'error')
            log_step(f"错误类型: {str(e.__class__.__name__)}", True)
            return None
        
    def enter_verification_code(self, code):
        print(f"准备输入验证码: {code}")
        time.sleep(2)
        code_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[placeholder="Code"]'))
        )
        time.sleep(1)
        code_input.send_keys(code)
        time.sleep(1)
        print("验证码输入完成")
        
    def cleanup(self):
        print("清理资源，关闭浏览器...")
        self.driver.quit()
        print("浏览器已关闭")

def generate_random_alias(base_email, length=8):
    """生成随机邮箱别名"""
    # 生成随机字符串，包含小写字母和数字
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    # 将基础邮箱转换为别名
    return base_email.replace("@gmail.com", f"+{random_str}@gmail.com")

def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    try:
        config.read('config.ini', encoding='utf-8')
        return {
            'base_email': config['Email']['base_email'],
            'password': config['Email']['password'],
            'success_log': config['Settings']['success_log'],
            'threads': config['Settings'].getint('threads'),
            'register_count': config['Settings'].getint('register_count')
        }
    except Exception as e:
        log_step(f"读取配置文件失败: {str(e)}", False, 'error')
        raise

def record_success(email, log_file):
    """记录成功注册的账号"""
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} | {email}\n")
        log_step(f"账号记录成功: {email}", False, 'success')
    except Exception as e:
        log_step(f"记录账号失败: {str(e)}", False, 'error')

def register_task(base_email, password, success_log):
    """单个注册任务"""
    try:
        ALIAS_EMAIL = generate_random_alias(base_email)
        log_step(f"开始注册: {ALIAS_EMAIL}", False, 'info')
        
        bot = AbstractRegistration()
        bot.setup()
        bot.click_join_button()
        bot.enter_email(ALIAS_EMAIL)
        bot.submit_form(1)
        
        code = bot.get_verification_code(ALIAS_EMAIL, password)
        if code:
            bot.enter_verification_code(code)
            bot.submit_form(2)
            log_step("等待注册完成...", False, 'info')
            time.sleep(5)
            
            record_success(ALIAS_EMAIL, success_log)
            log_step(f"注册成功: {ALIAS_EMAIL}", False, 'success')
        else:
            log_step(f"注册失败: {ALIAS_EMAIL}", False, 'error')
            
    except Exception as e:
        log_step(f"注册错误: {str(e)}", False, 'error')
    finally:
        bot.cleanup()

def main():
    log_section("Abstract 自动注册程序")
    
    try:
        # 加载配置
        config = load_config()
        BASE_EMAIL = config['base_email']
        PASSWORD = config['password']
        SUCCESS_LOG = config['success_log']
        THREADS = config['threads']
        REGISTER_COUNT = config['register_count']
        
        log_step(f"启动配置:", False, 'info')
        log_step(f"基础邮箱: {BASE_EMAIL}", True)
        log_step(f"线程数量: {THREADS}", True)
        log_step(f"每线程注册数: {REGISTER_COUNT}", True)
        log_step(f"总注册数量: {THREADS * REGISTER_COUNT}", True)
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            # 提交所有任务
            futures = []
            for _ in range(THREADS * REGISTER_COUNT):
                future = executor.submit(
                    register_task,
                    BASE_EMAIL,
                    PASSWORD,
                    SUCCESS_LOG
                )
                futures.append(future)
            
            # 等待所有任务完成
            for future in futures:
                future.result()
                
        log_section("所有任务完成", 'success')
            
    except Exception as e:
        log_step(f"程序错误: {str(e)}", False, 'error')
        log_section("程序异常退出", 'error')

if __name__ == "__main__":
    main() 