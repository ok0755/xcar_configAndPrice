#coding=utf-8
#author:zhoubin
#python2.7
'''
程序功能：按指定字段，爬取爱卡汽车车型配置、报价，存入d:\xcar.csv
使用方法：双击执行xcar_configAndPrice.exe,运行过程中不能打开xcar.csv，否则发生写入错误
执行结果：生成 d:\xcar.csv文件
'''
import sys
reload(sys)
sys.setdefaultencoding('GB2312')
import csv
import requests
from lxml import etree
import time
import gevent
from gevent import monkey,pool
monkey.patch_socket()

class Xcar(object):                                                         #定义类

    def __init__(self):
          #伪装成浏览器访问
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}

    #获取各分页列表
    def get_page_lists(self):
        url='http://newcar.xcar.com.cn/car/0-0-0-0-0-0-6_7_10-0-0-0-0-1/'    #初始页
        print 'Start page:>> ',url
        html = requests.get(url,headers=self.header)                        #发起网络请求
        response = html.text                                                #网页源码
        html.close()                                                        #断开网络请求
        selector = etree.HTML(response)
        end_page = selector.xpath('.//a[@class="page"][last()]/text()')[0] #解析获取总网页数
        print 'Total Pages:>> ',end_page
        pages = int(end_page)+1
        for i in range(1,pages):
            page_lists='http://newcar.xcar.com.cn/car/0-0-0-0-0-0-6_7_10-0-0-0-0-{}'.format(i) #各分页
            yield page_lists

    #解析获取各车型ID
    def target_url(self,url):
        target_lists = ''
        time.sleep(1)                                                       #等候1秒，防止访问网站太快IP被封
        res = requests.get(url,headers=self.header)                         #发起网络请求
        res.encoding = 'gb2312'                                             #中文编码
        html = res.text                                                     #网页源码
        res.close()                                                         #断开网络请求
        resource = etree.HTML(html)
        txt_list = resource.xpath('.//a/@data-mids')                        #解析获取各车型ID
        id_string = '|'.join(txt_list)
        id_lists = id_string.split('|')
        yield id_lists                                                     #返回车型ID列表

#解析配置、经销商报价
def detail(car_id):
    gevent.sleep(2)                                                         #访问网站等候2秒，防止IP被封
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    config_url = 'http://newcar.xcar.com.cn/m{}/config.htm'.format(car_id)

    # 报价url，cityid=348=深圳,order=1=从低到高
    price_url = 'http://newcar.xcar.com.cn/auto/index.php?r=newcar/ModelPrice/GetDealerListAjax&mid={}&cityid=348&iss=1&order=1'.format(car_id)

    # 设定目标字段
    fit_result = [u'厂商指导价：',u'品牌：',u'级别：',u'发动机：',u'动力类型：',u'变速箱：',\
    u'长×宽×高(mm)：',u'车长(mm)：',u'车宽(mm)：',u'车高(mm)：',u'车身结构：',u'上市年份：',\
    u'0-100加速时间(s)：',u'工信部油耗(L/100km)：',u'保修政策：',u'车长(mm)：',u'车宽(mm)：',\
    u'车高(mm)：',u'轴距(mm)：',u'车重(kg)：',u'座位数：',u'排量(L)：',u'最大马力(Ps)：',\
    u'最大功率(kW/rpm)：',u'最大扭矩(Nm/rpm)：',u'燃油标号：',u'供油方式：',u'环保标准：',\
    u'发动机自动启/停：',u'挡位个数：',u'变速箱类型：',u'变速箱名称：',u'驱动方式：',\
    u'助力类型：',u'前悬挂类型：',u'后悬挂类型：',u'前制动器类型：',u'后制动器类型：',\
    u'驻车制动类型：',u'主/副驾驶座安全气囊：',u'头部气囊(气帘)：',u'侧气囊：',\
    u'胎压监测装置：',u'零胎压继续行驶：',u'车内中控锁：',u'遥控钥匙：',u'ABS防抱死：',\
    u'制动力分配(EBD/CBC等)：',u'刹车辅助(EBA/BAS/BA等)：',u'牵引力控制(ASR/TCS等)：',\
    u'车身稳定控制(ESP/DSC等)：',u'上坡辅助：',u'陡坡缓降：',u'自动驻车：',u'电动天窗：',\
    u'全景天窗：',u'方向盘调节：',u'多功能方向盘：',u'方向盘电动调节：',u'泊车雷达：',\
    u'倒车视频影像：',u'定速巡航：',u'自适应巡航：',u'无钥匙进入系统：', u'无钥匙启动系统：',\
    u'座椅材质：',u'座椅高低调节：',u'远光灯：',u'近光灯：',u'前雾灯：',u'日间行车灯：',\
    u'大灯高度可调：',u'自动头灯：',u'电动车窗：',u'车窗防夹手功能：',u'电动后视镜：',\
    u'后视镜加热：',u'后视镜电动折叠：',u'手动空调：',u'自动空调：',u'后排独立空调：',\
    u'后排出风口：',u'温度分区控制：']

    ar = []
    br = []
    cr = []
    car_price = get_price(price_url)                                        #调用get_price函数，获取车商报价
    res = requests.get(config_url,headers=header)
    res.encoding = 'gb2312'                                                  #中文编码
    html = res.text
    res.close()
    resource = etree.HTML(html)
    try:
        car_name = resource.xpath('.//div[@class="place"]/a/text()')        #车名
        ar.append('=hyperlink("{}","{}")'.format(config_url,config_url))    #创建链接
        ar.append(car_name[2])                                              #车型
        ar.append(car_name[3])                                              #款式
        ar.append(car_price)                                                #车商报价

        selector = resource.xpath('.//tr')
        for td in selector:
            bg3 = td.xpath('normalize-space(./td[@class="bg3"])')
            bg4 = td.xpath('normalize-space(./td[@class="bg4"])')
            ar.append(bg3)
            br.append(bg4)

        cr.append(ar[0])
        cr.append(ar[1])
        cr.append(ar[2])
        cr.append(ar[3])
        for a in ar:
            if a in fit_result:
                index = ar.index(a)-4
                cr.append(a)
                cr.append(br[index])

    except Exception as e:
        print config_url,e                                                  # 打印出错信息
        cr.append('{} is empty'.format(url))
    with open(r"d:\xcar.csv",'ab+') as f:                                   # 追加写入 d:\xcar.csv
        wf =csv.writer(f)
        wf.writerow(cr)

#获取经销商报价
def get_price(price_url):
    try:
        resp = requests.get(price_url,headers=header)
        price_html = resp.text
        resp.close()
        price_results = etree.HTML(price_html)
        price_car = float(price_results.xpath('.//em[@class="red"]/text()')[0])*10000  #报价转换成整数
    except:
        price_car = 0    # 如无报价则设为 "0"
    return price_car


if __name__=="__main__":                                                # 主程序入口
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    xcar = Xcar()
    p = pool.Pool(30)                                                   #协程数30，并发执行
    for page in xcar.get_page_lists():
        print 'Get page:>> ',page
        for target_url_lists in xcar.target_url(page):
            for url in target_url_lists:
                p.spawn(detail,url)
            p.join()