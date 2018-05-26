#coding=utf-8
import requests
from lxml import etree
import os
import gc
import time
import xlsxwriter
import gevent
from gevent import monkey,pool
monkey.patch_socket()

class Xcar(object):

    def __init__(self):
        self.page_lists=[]
        self.header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
        self.get_page_lists()

    def get_page_lists(self):
        url='http://newcar.xcar.com.cn/car/0-0-0-0-0-0-0-0-0-0-0-1/'
        html=requests.get(url,headers=self.header)
        response=html.text
        html.close()
        selector=etree.HTML(response)
        end_page=selector.xpath('.//a[@class="page"][last()]/text()')[0] #总页数
        pages=int(end_page)+1
        for i in range(1,pages):
            self.page_lists.append(url[:-2]+'{}/'.format(i))   #分页lists

    def target_url(self,url):
        ar=[]
        target_lists=''
        time.sleep(1)
        res=requests.get(url,headers=self.header)
        res.encoding='gb2312'
        root_url='http://newcar.xcar.com.cn'
        html=res.text
        res.close()
        resource=etree.HTML(html)
        txt_list=resource.xpath('.//a/@data-mids')
        for t in txt_list:
            target_lists+='|{}'.format(t)
        ar=target_lists.split('|')
        ar.remove('')
        return ar

def detail(url,price_url):
    car_price=get_price(price_url)
    global k
    gevent.sleep(3)
    i=4
    res=requests.get(url,headers=header)
    res.encoding='gb2312'
    html=res.text
    res.close()
    resource=etree.HTML(html)
    car_name=resource.xpath('.//div[@class="place"]/a/text()')
    xl_sheet.write(k,0,url)
    xl_sheet.write(k,1,car_name[2])
    xl_sheet.write(k,2,car_name[3])
    xl_sheet.write(k,3,car_price)
    selector=resource.xpath('.//tr')
    for td in selector:
        for txt in td.xpath('./td[@id]//text()[normalize-space()]'):
            xl_sheet.write(k,i,txt.replace('\n','').replace(' ','').strip())
            i+=1
    k+=1

def get_price(price_url):
    try:
        resp=requests.get(price_url,headers=header)
        price_html=resp.text
        resp.close()
        price_results=etree.HTML(price_html)
        price_car=price_results.xpath('.//em[@class="red"]/text()')[0]
    except:
        price_car='Null'
    return price_car

if __name__=="__main__":
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    xcar=Xcar()
    xls=xlsxwriter.Workbook('x_car.csv')
    xl_sheet=xls.add_worksheet('sh')
    k=0
    p=pool.Pool(30)
    th=[]
    for url in xcar.page_lists:
        for u in xcar.target_url(url):
            ur='http://newcar.xcar.com.cn/m{}/config.htm'.format(u)
            price_url='http://newcar.xcar.com.cn/auto/index.php?r=newcar/ModelPrice/GetDealerListAjax&mid={}&cityid=348&iss=1&order=1'.format(u)
            th.append(p.spawn(detail,ur,price_url))
    gevent.joinall(th)
    xls.close()

#http://newcar.xcar.com.cn/auto/index.php?r=ajax/GetDealerPrice2&is_pre_sale=1&city_id=348&pserid=3109
#http://newcar.xcar.com.cn/m37384/baojia/
#http://newcar.xcar.com.cn/auto/index.php?r=newcar/ModelPrice/GetDealerListAjax&mid=37384&cityid=348&iss=1&order=1