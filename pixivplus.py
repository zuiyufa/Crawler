import json
import requests
from urllib import parse
import time
import random
import re

class BaiduTiebaSpider:
    def __init__(self):
        self.url ='https://www.pixiv.net/ajax/search/artworks/%E5%8E%9F%E7%A5%9E10000users%E5%85%A5%E3%82%8A?word=%E5%8E%9F%E7%A5%9E10000users%E5%85%A5%E3%82%8A&order=date_d&mode=r18&p=1&s_mode=s_tag_full&type=all&lang=zh' #'https://www.pixiv.net/ajax/search/illustrations/{}?word={}&order=date_d&mode={}&p={}&s_mode=s_tag_full&type=illust_and_ugoira&lang=zh'
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                        'referer': 'https://accounts.pixiv.net/login?return_to=https://www.pixiv.net/&lang=zh&source=pc&view_type=page'}
        self.Cookies = {}
    def get_html(self, url):
        self.proxies = {'http': 'http://127.0.0.1:8000',
                   'https': 'http://127.0.0.1:8000'}
        # requests.DEFAULT_RETRIES = 5
        # session.keep_alive = False
        params = {'lang': 'en',
                  'source': 'pc',
                  'view_type': 'page',
                  'ref': 'wwwtop_accounts_index'
                  }
        form_data = {'login_id': '1140122356@qq.com',
                     'password': 'Zlt.1140122356',
                     'source': 'pc',
                     'app_ios': '0',
                     'ref': 'wwwtop_accounts_indes',
                     'captcha': '',
                     'g_recaptcha_response': '',
                     # 'post_key': '',
                     'tt': '5d2d02b09c76ff6ae59b919e3958ca1b',

                     'return_to': 'https://www.pixiv.net/',
                     }
        login_url = 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page'
        post_url = 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page'
        #res = requests.get(login_url1, params=params, proxies=proxies, headers=self.headers)
        # print(res)
        # print(res.text)
        # pattern = re.compile(r'name="post_key" value="(.*?)">')
        # r = pattern.findall(res.text)
        # print(r)
        # form_data['post_key'] = r[0]
        session = requests.Session()
        result = session.post(url=post_url, data=form_data, proxies=self.proxies, headers=self.headers)
        print("登陆后的cookies是:", result.cookies)

        self.Cookies = result.cookies
        #print(result.cookies)
        #print(type(result.cookies))
        #for k, v in result.cookies.items():
            #print(k + ':' + v)

        Proxy = {'http': 'http://127.0.0.1:8000', 'https': 'http://127.0.0.1:8000'}
        #proxy_handler = urllib.request.ProxyHandler(Proxy)
        #cookie_handler = urllib.request.HTTPCookieProcessor(Cookies)
        #opener = urllib.request.build_opener(proxy_handler,cookie_handler)
        #urllib.request.install_opener(opener)
        req =session.get(url=url, headers=self.headers,proxies=self.proxies,cookies=self.Cookies)
        #print(req.text)
        #print(req)
        #res = request.urlopen(req)
        html = req.text

        return html


    def parse_html(self, url):
        pass

    def save_html(self, filename, img):
        with open(filename, 'wb+') as f:
            f.write(img)  # 将图片的二进制数据流写入文件
        # with open(filename, 'w', encoding='utf8') as f:
        # f.write(html)




    def run(self):




        name = '原神10000users入り' #input('请输入关键词名字：')+'10000users入り'
        #mode= input('年龄分级: r18 or safe or all')
        start = 1 #int(input('请输入起始页：'))
        end = 1 #int(input('请输入终止页：'))
        params = parse.quote(name)
        # 1.拼接url地址
        for page in range(start, end + 1):
            pn = page
            self.headers.update({'referer': 'https://www.pixiv.net/tags/{}/illustrations?p={}'.format(params, pn)})
            #url = self.url.format(params,params,mode,pn)
            #print('筛选结果地址：'+url)
            html = self.get_html(self.url)
            #print(html)
            data=json.loads(html)
            data_list=data['body']['illustManga']["data"]
            for item in data_list:
                title=item['title']
                #imgurl=item['url']
                id=item['id']
                #print(id)
                bigimgurl='https://www.pixiv.net/artworks/{}'.format(id)
                print('图片地址：'+bigimgurl)
                html = self.get_html(bigimgurl)

                picture = re.search("\"original\":\"(.+?)\"},\"tags\"", html)
                print('图片源：'+picture.group(1))
                pictureurl=(picture.group(1))




                #print(html)
                #soup = BeautifulSoup(html, 'lxml')
                #print(soup.txt)
                #all_result = soup.find_all('div', role='presentation')  #<div role="presentation" class="sc-1qpw8k9-0 gTFqQV"><a href="https://i.pximg.net/img-original/img/2022/08/28/20/17/40/100828202_p0.jpg" class="sc-1qpw8k9-3 eFhoug gtm-expand-full-size-illust" target="_blank" rel="noopener"><img alt="#GenshinImpact 申鹤 - 咖卡CAthenal的插画" src="https://i.pximg.net/img-master/img/2022/08/28/20/17/40/100828202_p0_master1200.jpg" width="2480" height="3508" class="sc-1qpw8k9-1 jOmqKq" style="height: 849px;"></a></div>
                #print(all_result)

                #tree = etree.HTML(html)
                #print(tree.txt)
                #li_list = tree.xpath('//*[@id="root"]/div[2]/div/div[3]/div/div[1]/main/section/div[1]/div/figure/div/div[1]/div/a/img')  # /html/body/div[1]/div[2]/div/img #/html/body/div[1]/div[2]/div/img
                #print(li_list)

                #print((html))

                #print(bigimgurl)
                #print(imgurl)
                #print(title)
                #request = urllib.request.Request(pictureurl,headers=self.headers)
                #response = urllib.request.urlopen(request)
                req =requests.get(pictureurl,headers=self.headers,cookies=self.Cookies,proxies=self.proxies)
                print(req)
                #res =req.content.decode('gbk')
                #print(res)
                imgData = req.content # 图片的二进制数据流
                filename = 'picture/id{} {}.jpg'.format(id,title)
                self.save_html(filename, imgData)
                print('保存成功')
            print('第%d页抓取成功' % page)
            # 控制数据抓取的频率
            time.sleep(random.randint(2, 4))




test = BaiduTiebaSpider()
test.run()