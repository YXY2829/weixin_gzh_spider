from requests import Session, Request
from requests import ReadTimeout, ConnectionError
from urllib.parse import urlencode
from queue import Queue
from lxml import etree

config = {
    'timeout': 5,
}

class WeixinRequest(Request):
    def __init__(self, url, callback, method='GET', headers=None, need_proxy=False, fail_time=0, timeout=config['timeout']):
        Request.__init__(self, method, url, headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout

class WeixinSpider(object):
    base_url = 'http://weixin.sogou.com/weixin'
    keyword = 'python'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'IPLOC=CN1100; SUID=6FEDCF3C541C940A000000005968CF55; SUV=1500041046435211; ABTEST=0|1500041048|v1; SNUID=CEA85AE02A2F7E6EAFF9C1FE2ABEBE6F; weixinIndexVisited=1; JSESSIONID=aaar_m7LEIW-jg_gikPZv; ld=Wkllllllll2BzGMVlllllVOo8cUlllll5G@HbZllll9lllllRklll5@@@@@@@@@@; LSTMV=212%2C350; LCLKINT=4650; ppinf=5|1500042908|1501252508|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo1NDolRTUlQjQlOTQlRTUlQkElODYlRTYlODklOEQlRTQlQjglQTglRTklOUQlOTklRTglQTclODV8Y3J0OjEwOjE1MDAwNDI5MDh8cmVmbmljazo1NDolRTUlQjQlOTQlRTUlQkElODYlRTYlODklOEQlRTQlQjglQTglRTklOUQlOTklRTglQTclODV8dXNlcmlkOjQ0Om85dDJsdUJfZWVYOGRqSjRKN0xhNlBta0RJODRAd2VpeGluLnNvaHUuY29tfA; pprdig=ppyIobo4mP_ZElYXXmRTeo2q9iFgeoQ87PshihQfB2nvgsCz4FdOf-kirUuntLHKTQbgRuXdwQWT6qW-CY_ax5VDgDEdeZR7I2eIDprve43ou5ZvR0tDBlqrPNJvC0yGhQ2dZI3RqOQ3y1VialHsFnmTiHTv7TWxjliTSZJI_Bc; sgid=27-27790591-AVlo1pzPiad6EVQdGDbmwnvM; PHPSESSID=mkp3erf0uqe9ugjg8os7v1e957; SUIR=CEA85AE02A2F7E6EAFF9C1FE2ABEBE6F; sct=11; ppmdig=1500046378000000b7527c423df68abb627d67a0666fdcee; successCount=1|Fri, 14 Jul 2017 15:38:07 GMT',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    session = Session()
    q = Queue()

    def start(self):
        self.session.headers.update(self.headers)
        start_url = self.base_url + '?' + urlencode({'query': self.keyword, 'type': 2})
        weixin_request = WeixinRequest(url=start_url, callback=self.parse_index)
        self.q.put(weixin_request)

    def parse_index(self, response):
        html = etree.HTML(response.text)
        items = html.xpath('//ul[@class="news-list"]/li//h3/a')
        for item in items:
            url = item.xpath('@href')[0]
            weixin_request = WeixinRequest(url=url, callback=self.parse_detail)
            yield weixin_request
        next_page = html.xpath('//a[@id="sogou_next"]')
        if next_page:
            next_page = self.base_url + str(next_page[0].xpath('@href')[0])
            weixin_request = WeixinRequest(url=next_page, callback=self.parse_index, need_proxy=True)
            yield weixin_request

    def parse_detail(self, response):
        html = etree.HTML(response.text)
        all_p = html.xpath('//div[@class="rich_media_content "]//p')
        data = {
            'title': html.xpath('//h2[@id="activity-name"]/text()')[0].strip(),
            'content': '\n'.join([' '.join(i.xpath('.//text()')) for i in all_p]),
            'date': html.xpath('//em[@id="publish_time"]/text()')[0],
            'nickname': html.xpath('//strong[@class="profile_nickname"]/text()')[0],
            'wechat': html.xpath('//div[@class="profile_inner"]/p[1]/span/text()')[0]
        }

    def request(self, weixin_request):
        try:
            return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False

    def error(self, weixin_request):
        """
        错误处理
        :param weixin_request: 请求
        :return:
        """
        weixin_request.fail_time = weixin_request.fail_time + 1
        print('Request Failed', weixin_request.fail_time, 'Times', weixin_request.url)
        if weixin_request.fail_time < 3:
            self.q.put(weixin_request)

    def schedule(self):
        """
        调度请求
        :return:
        """
        while not self.q.empty():
            weixin_request = self.q.get()
            callback = weixin_request.callback
            print('Schedule', weixin_request.url)
            response = self.request(weixin_request)
            if response and response.status_code in [200]:
                results = list(callback(response))
                if results:
                    for result in results:
                        print('New Result', type(result))
                        if isinstance(result, WeixinRequest):
                            self.q.put(result)
                        if isinstance(result, dict):
                            print('articles', result, '\n','-'*30)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)

    def run(self):
        self.start()
        self.schedule()

if __name__ == '__main__':
    wx_spider = WeixinSpider()
    wx_spider.run()
