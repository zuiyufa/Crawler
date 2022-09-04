import json
import os
import sys
import requests
from urllib import parse
import time
import random
import re
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver #-------------------#配置webdriver
PROXIES="http://127.0.0.1:8000"  # 这里填代理的端口
edge_options=webdriver.EdgeOptions()
edge_options.headless=True  # 设置浏览器是否显示，如果要谷歌验证的话就把这个打开
edge_options.add_argument('--proxy-server=%s' % PROXIES)
driver=webdriver.Edge(options=edge_options)
try:
    driver.get("https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page")
except:
    print("代理失效，请更换节点后重试")
    sys.exit()


def is_reCAPTCHA_present(): #----------------------#用于检验登录时谷歌验证是否弹出
    try:
        reCAPTCHA = driver.find_element(By.CSS_SELECTOR, "[class='sc-2o1uwj-5 cPXLxz']")
    except NoSuchElementException as e:
        return False
    return True

def is_reLOGINSIGN_present(): #-------------------#用于检验登录时账号密码是否正确
    try:
        reloginsign = driver.find_element(By.CSS_SELECTOR, "[class='sc-2o1uwj-2 hLrkTC']")
    except NoSuchElementException as e:
        return False
    return True

def getcookies(pixiv_id,pix_pwd):#----------------#获取cookie来验证登录
    try:
        time.sleep(random.randint(1, 3))  # 适当停顿一下避免被ban
        user_input=driver.find_element(By.CSS_SELECTOR, "[class='sc-bn9ph6-6 degQSE']")
        pwd_input=driver.find_element(By.CSS_SELECTOR, "[class='sc-bn9ph6-6 hfoSmp']")
        login_btn=driver.find_element(By.CSS_SELECTOR, "[class='sc-bdnxRM jvCTkj sc-dlnjwi pKCsX sc-2o1uwj-7 fguACh sc-2o1uwj-7 fguACh']")
        user_btn=driver.find_element(By.CSS_SELECTOR, "[class='sc-bn9ph6-0 kJkgq sc-2o1uwj-3 diUbPW']")
        pwd_btn=driver.find_element(By.CSS_SELECTOR, "[class='sc-bn9ph6-0 kJkgq sc-2o1uwj-4 hZIeVE']")
        user_btn.click()
        user_input.send_keys(pixiv_id)
        pwd_btn.click()
        pwd_input.send_keys(pix_pwd)
        login_btn.click()
        time.sleep(random.randint(1,3))
        reCAPTCHA=is_reCAPTCHA_present()
        reloginsign=is_reLOGINSIGN_present()
        if reCAPTCHA is True:
            print('遭遇谷歌验证,请在三十秒内完成验证')
            time.sleep(30)
            reCAPTCHA2=is_reCAPTCHA_present()
            if reCAPTCHA2 is True:
                print('超时，程序自动退出')
                sys.exit(0)
        elif reloginsign is True:
            print('账号密码错误，重启程序来重新输入')
            sys.exit(0)
        else:
            pass
    except SystemExit :
        sys.exit().exit()
    except requests.exceptions.ProxyError:
        print("代理失效了，请更换节点重试")
        sys.exit()
    except:
        print('遇到未知错误，退出')
        sys.exit()
    cookies = driver.get_cookies()
    print('成功获取到cookie')
    driver.quit()
    return cookies

def validateTitle(title):#-----------------------#用于把文件名中不能使用的符号替换掉
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

class PixivSpider:
    def __init__(self):
        self.url ='https://www.pixiv.net/ajax/search/illustrations/{}?word={}&order=date_d&mode={}&p={}&s_mode=s_tag&type=illust_and_ugoira&lang=zh'
        self.Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                        'referer': 'https://accounts.pixiv.net/login?return_to=https://www.pixiv.net/&lang=zh&source=pc&view_type=page'}  # referer用于对付防盗链
        self.Cookies = {}
        self.proxies= {'http': 'http://127.0.0.1:8000',
                      'https': 'http://127.0.0.1:8000'}  # 这里也是代理地址

    def save_html(self,filepath,filename,filesuffix,imgData,id,title):#-------------#保存图片到本地
        try:
            fixfilepath=filepath+filename+filesuffix
            finalpath=fixfilepath.format(id,title)
            with open(finalpath, 'wb') as f:
                f.write(imgData)  # 将图片的二进制数据流写入文件
        except FileNotFoundError:
            try:
                os.makedirs(filepath)  # 没有则创建文件夹
                with open(finalpath, 'wb') as f:
                    f.write(imgData)
            except OSError:
                print('创建文件夹失败')
                sys.exit()

    def download_picture(self,finalname,mode):
        try:
            startpagenum = int(input('请输入起始页(数字)：'))
            endpagenum = int(input('请输入终止页(数字)：'))
        except:
            print("未知错误，重启")
            sys.exit()
        print("开始下载。。。。")
        params = parse.quote(finalname)
        session = requests.Session()  #创建session来存储cookie
        for cookie in self.Cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        for page in range(startpagenum, endpagenum + 1):
            pn = page
            i = 0
            newurl = 'https://www.pixiv.net/tags/{}/illustrations?mode={}&p={}&s_mode=s_tag'.format(params, mode, page)
            print('当前图片预览合集：' + newurl)
            self.Headers.update({'referer': 'https://www.pixiv.net/tags/{}/illustrations?mode={}&p={}&s_mode=s_tag'.format(params, mode, pn)})
            url = self.url.format(params, params, mode, pn)
            print('第{}页的下载地址:'.format(pn) + url)
            try:
                req1 = session.get(url=url, headers=self.Headers, proxies=self.proxies)
            except requests.exceptions.ProxyError:
                print('代理失效了，请更换节点再试')
                sys.exit()
            except:
                print('未知错误，重启')
                sys.exit()
            html1 = req1.text
            data = json.loads(html1)
            data_list = data['body']['illust']["data"]
            self.tag_list = data['body']['relatedTags']
            if len(data_list) == 0:
                print('未搜索到任何图片，请重启之后输入新关键词')
                sys.exit()
            for item in data_list:  #遍历列表中所有图片有关的信息
                i = i + 1
                oldtitle = item['title']
                title = validateTitle(oldtitle)
                id = item['id']
                bigimgurl = 'https://www.pixiv.net/artworks/{}'.format(id)
                print('第{}页第{}张图片地址：'.format(pn,i) + bigimgurl)
                req2 = session.get(url=bigimgurl, headers=self.Headers, proxies=self.proxies)
                html2 = req2.text
                try:
                    picture = re.search("\"original\":\"(.+?)\"},\"tags\"", html2)
                    print('第{}页第{}张图片源：'.format(pn,i) + picture.group(1))
                    pictureurl = (picture.group(1))
                    req = session.get(pictureurl, headers=self.Headers, proxies=self.proxies)
                    imgData = req.content  # 图片的二进制数据流
                    filepath = 'D:\PIXIV\{} {}'.format(finalname, mode)  #这里可以修改存储路径和文件夹名称
                    filename = '/{}{}'
                    filesuffix = '.jpg'
                    self.save_html(filepath, filename, filesuffix, imgData, id, title)
                except RuntimeError:
                    print("分析得到的图片源少于图片地址，提前结束")
                except:
                    print("遇到未知错误，重启")
                    sys.exit()
                print('第{}页第{}张图片保存成功！'.format(pn,i))
            print('第%d页的图片全部抓取成功！' % page)
            #time.sleep(random.randint(3,5))

    def show_tag_list(self,tag_list):  #遍历展示tag标签
        i=0
        for n in tag_list:
            i=i+1
            print(str(i)+'.'+str(n))

    def chose_tag_list(self,tag_list):
        try:
            num=int(input('选择你的tag标号'))
        except:
            print("未知错误，重启")
            sys.exit()
        truenum=num-1
        chosentag=tag_list[truenum]
        return chosentag

    def handle_name(self,name):  #对关键词的处理
        tepname = name
        addtag = int(input('是否加入关键词 10000users入り  1 or 0 :'))
        tag = ' 10000users入り'
        try:
            if addtag == 1:
                finalname = tepname + tag
            elif addtag == 0:
                finalname = tepname
            else:
                print('输入错误，重启')
                sys.exit()
            print('当前标签为' + finalname)
            return finalname
        except:
            print("未知错误，重启")
            sys.exit()

    def chose_mode(self):
        selectmode = int(input('选择年龄分级:\n1.R18\n2.全年龄\n3.全部\n输入数字!!! ：'))
        try:
            if selectmode == 1:
                mode = "r18"
            elif selectmode == 2:
                mode = "safe"
            elif selectmode == 3:
                mode = "all"
            else:
                print('输入错误，重启')
                sys.exit()
            return mode
        except:
            print("未知错误，重启")
            sys.exit()

    def run(self):  #------------------------------#主程序
        pixiv_id= input('请输入pixiv账号：')  #这里可以填写成自己的账号密码
        pixiv_pwd= input('请输入密码：')
        name = input('请输入关键词：')
        finalname = self.handle_name(name)
        mode=self.chose_mode()
        self.Cookies = getcookies(pixiv_id, pixiv_pwd)
        self.download_picture(finalname,mode)
        print('全部抓取完成')
        while True:
            print("1.退出 2.继续下载其他页 3.浏览其他标签")
            choice=int(input('请选择一个数字'))
            try:
                if choice==1:
                    break
                elif choice==2:
                    self.download_picture(finalname,mode)
                elif choice==3:
                    self.show_tag_list(self.tag_list)
                    newtagname=self.chose_tag_list(self.tag_list)
                    finalname=self.handle_name(newtagname)
                    mode=self.chose_mode()
                    self.download_picture(finalname, mode)
                else:
                    print("输入错误，重启")
            except:
                print(("未知错误，重启"))
        sys.exit()
test = PixivSpider()
test.run()
