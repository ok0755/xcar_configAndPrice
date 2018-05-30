#coding=utf-8
import requests
from lxml import etree
import time
import pandas as pd
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
    ar=[]
    car_price=get_price(price_url)
    global k
    gevent.sleep(3)
    res=requests.get(url,headers=header)
    res.encoding='gb2312'
    html=res.text
    res.close()
    resource=etree.HTML(html)
    try:
        car_name=resource.xpath('.//div[@class="place"]/a/text()')
        ar.append('=hyperlink("{}","{}")'.format(url,url))
        ar.append(car_name[2].encode('gb2312'))
        ar.append(car_name[3].encode('gb2312'))
        ar.append(car_price)
        selector=resource.xpath('.//tr')
        for td in selector:
            for txt in td.xpath('./td[@id]//text()[normalize-space()]'):
                wr_txt=txt.replace('\n','').replace(' ','').strip()
                ar.append(wr_txt.encode('gb2312','ignore'))
    except Exception,e:
        print e,url,'is empty'
    finally:
        dic[k]=ar
    k+=1

def get_price(price_url):
    try:
        resp=requests.get(price_url,headers=header)
        price_html=resp.text
        resp.close()
        price_results=etree.HTML(price_html)
        price_car=float(price_results.xpath('.//em[@class="red"]/text()')[0])*10000
    except:
        price_car=0
    return price_car

if __name__=="__main__":
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    xcar=Xcar()
    k=0
    p=pool.Pool(30)
    th=[]
    outputfile='d:\\xcar.csv'
    for url in xcar.page_lists:
        dic={}
        for u in xcar.target_url(url):
            ur='http://newcar.xcar.com.cn/m{}/config.htm'.format(u)
            print 'downloading',ur
            price_url='http://newcar.xcar.com.cn/auto/index.php?r=newcar/ModelPrice/GetDealerListAjax&mid={}&cityid=348&iss=1&order=1'.format(u)
            th.append(p.spawn(detail,ur,price_url))
        df=pd.DataFrame.from_dict(dic,orient='index')
        df.to_csv(outputfile,mode='a',header=0,index=0)
    gevent.joinall(th)

#http://newcar.xcar.com.cn/auto/index.php?r=ajax/GetDealerPrice2&is_pre_sale=1&city_id=348&pserid=3109
#http://newcar.xcar.com.cn/m37384/baojia/
#http://newcar.xcar.com.cn/auto/index.php?r=newcar/ModelPrice/GetDealerListAjax&mid=37384&cityid=348&iss=1&order=1