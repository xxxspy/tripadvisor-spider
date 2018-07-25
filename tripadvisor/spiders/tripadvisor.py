from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from ..items import CityItem, AttractionItem, UserItem, ReviewItem, NeighborItem
from scrapy.http import Request
import re 
import time

def one(lst:list):
    if not isinstance(lst, (list, tuple)):
        return lst
    if len(lst)== 0:
        return ''
    else:
        return lst[0].strip()

def review_next_page(url, total):
    '''
    url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or10-Aqua_Luna-Hong_Kong.html'
    url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-Aqua_Luna-Hong_Kong.html'
    '''
    if total <= 10:
        next_url =  None
    fmt = re.compile(r'\-Reviews\-or(\d*)\-')
    # fmt = re.compile('Reviews')
    m = fmt.search(url)
    if m is None:
        pre, suf = url.split('-Reviews-')
        next_url = pre + '-Reviews-' + 'or10-' + suf
    else:
        m = int(m.group(1))
        cha = total - m
        if cha <= 10:
            next_url = None
        else:
            n = int(m/10+1)*10
            r = f'-Reviews-or{n}-'
            next_url = fmt.sub(r, url)
    return next_url
        




class Trip(CrawlSpider):

    name = 'tripadvisor'
    start_urls = [
        'https://www.tripadvisor.cn/Attractions-g294211-Activities-oa20-China.html']
    url = 'https://www.tripadvisor.cn'
    allowed_domains = ['tripadvisor.cn']

    def parse(self, response):

        selector = Selector(response)
        lst = selector.css('div#LOCATION_LIST>ul.geoList')
        for link in lst.xpath('.//li'):
            city = CityItem()
            name = link.xpath('.//a/text()').extract()
            url = link.xpath('.//a/@href').extract()
            # city = City(name=name, url=url)
            city['name'] = name
            city['url'] = url
            city['belong'] = link.xpath('.//span/text()').extract()
            yield city
            assert len(url) == 1
            url = self.url + url[0]
            yield Request(url, callback=self.parse_attraction)
        nextlink = selector.css('a.sprite-pageNext').xpath('@href').extract()
        if len(nextlink)>=1:
            for nl in nextlink:
                next_ = self.url + str(nl)
                yield Request(next_, callback=self.parse)
        # else:
        #     raise ValueError

    def parse_attraction(self, response):
        sel = Selector(response)
        # lst = sel.css('div#FILTERED_LIST > div.listing_info')
        lst = sel.css('div.listing_info')
        
        for info in lst:
            attraction = AttractionItem()
            link = info.xpath('.//div[@class="listing_title "]/a')
            href = link.xpath('.//@href').extract()
            name = link.xpath('.//text()').extract()
            list_rating = info.xpath('.//div[@class="listing_rating"]')
            rate = list_rating.xpath(
                './/div[@class="rs rating"]/span[1]/@alt').extract()
            n_review = list_rating.xpath(
                './/div[@class="rs rating"]/span[2]/a/text()').extract()
            description = list_rating.xpath(
                './/div[@class="popRanking wrap"]/text()').extract()
            review_url = list_rating.xpath(
                './/div[@class="rs rating"]/span[2]/a/@href').extract()
            attraction['name'] = one(name)
            attraction['href'] = one(href)
            attraction['n_review'] = one(n_review)
            attraction['rate'] = one(rate)
            attraction['description'] = one(description)
            # yield attraction
            if review_url:
                yield Request(self.url + one(review_url), callback=self.parse_reviews(attraction))
        next_url = sel.xpath('div.pagination > a.next').xpath('.//@href').extract()
        for nu in next_url:
            yield Request(self.url + nu, callback=self.parse_attraction)


    def _extract_neighbors(self, container:Selector):
        rtn = []
        infos = container.css('div.poiInfo')
        for info in infos:
            neighbor = NeighborItem()
            name = info.xpath('.//div[@class="poiName"]/text()').extract()
            n_review = info.xpath('.//div[@class="reviewCount"]/text()').extract()
            distance = info.xpath('.//div[@class="distance"]/text()').extract()
            rating = info.xpath(
                './/div[@class="prw_rup prw_common_bubble_rating rating"]/span/@alt').extract()
            neighbor['name'] = one(name)
            neighbor['n_review'] = one(n_review)
            neighbor['distance'] = one(distance)
            neighbor['rating'] = one(rating)
            rtn.append(neighbor)
        return rtn
        
        
    def parse_neighbors(self, response):
        '''附近的酒店/景点/餐厅'''
        sel = Selector(response)
        containers = sel.css(
            'div.poiGrid')
        self.logger.debug(containers)
        for con in containers:
            category = con.xpath('.//span[@class="sectionTitle"]/text()').extract()
            nbs = self._extract_neighbors(con)
            for nb in nbs:
                nb['category'] = one(category)
                yield nb




    
    def parse_reviews(self, attraction: AttractionItem):
        
        def callback(response):
            sel = Selector(response)

            # 下一页
            # 中文评论的评论数
            rfiter = sel.css('div.language').xpath(
                './/label[@class="filterLabel "]')[1].xpath('.//span/text()').extract()
            n_review = sel.xpath('//label[@for="taplc_location_review_filter_controls_0_filterLang_zhCN"]/span/text()').extract()
            if not n_review:
                n_review = sel.xpath(
                    '//label[@for="taplc_location_review_filter_controls_responsive_0_filterLang_zhCN"]/span/text()').extract()
            n_review = one(n_review)
            
            if n_review == '':
                self.logger.info('No chinese review count')
                n_review = 0
            else:
                n_review = int(n_review.strip('(').strip(')'))
            next_page = review_next_page(response.url, n_review)

            containers = sel.css('div.review-container')
            
            # attraction info extration
            # rating
            chart = sel.css('ul.ratings_chart')[0]
            ratings = chart.xpath('.//span[@class="row_count row_cell"]/text()').extract()
            # category
            category = sel.xpath('//div[@class="rating_and_popularity"]/div[@class="detail"]/a/text()').extract()
            # address
            address = sel.xpath(
                '//div[@class="prw_rup prw_common_atf_header_bl headerBL"]').css('div.address').xpath('.//span/text()').extract()
            attraction['ratings_table']=ratings
            attraction['category'] = category
            attraction['address'] = address
            if not next_page:
                yield attraction
            ## 提取附近的酒店/景点等信息
            for nb in self.parse_neighbors(response):
                nb['attraction'] = attraction['name']
                nb['attraction_href'] = attraction['href']
                yield nb
            for c in containers:
                review = ReviewItem()
                user_name = c.css('div.username > span').xpath('.//text()')[0].extract()
                location = c.xpath('span.location > span').xpath(
                    './/text()').extract()
                title = c.css('div.quote > a').xpath('.//text()').extract()
                content = c.css('div.prw_rup.prw_reviews_text_summary_hsx').css(
                    'p.partial_entry').xpath('.//text()').extract()
                point = c.css('div.rating.reviewItemInline').xpath('.//span[1]/@class').extract()
                self.logger.debug('-----------------------------------@@@@@@@@@')
                point = one(point).split('_')[-1]
                self.logger.debug(point)
                review['content'] = one(content)
                review['title'] = one(title)
                review['user_name'] = user_name
                feedback = c.css('div.memberBadgingNoText')
                likes = feedback.xpath(
                    './/span[@class="ui_icon pencil-paper"]/following-sibling::*[1]/text()').extract()
                shares = feedback.xpath(
                    './/span[@class="ui_icon thumbs-up-fill"]/following-sibling::*[1]/text()').extract()
                review['likes'] = one(likes)
                review['shares'] = one(shares)
                review['point'] = point

                if len(location) >0:
                    location = location[0]
                review['location'] = location or ''
                review['attraction'] = attraction['name']
                review['attraction_href'] = attraction['href']
                yield review

                user_url = 'https://www.tripadvisor.cn/members/' + review['user_name']
                user = UserItem()
                user['name'] = user_name
                yield Request(user_url, callback=self.parse_user(user))

            if next_page:
                yield Request(next_page, callback=self.parse_reviews(attraction))



        return callback

    def parse_user(self, user):
        '''用户信息'''
        def callback(response):
            sel = Selector(response)
            profile = sel.css('div.leftProfile')
            register_time = profile.xpath('.//div[@class="ageSince"]/text()').extract()
            hometown = profile.xpath('.//div[@class="hometown"]/p/text()').extract()
            about = profile.xpath('.//div[@class="aboutMeDesc padded"]/text()').extract()
            n_review = profile.xpath('.//a[@name="reviews"]/text()').extract()
            n_rating = profile.xpath('.//a[@name="ratings"]/text()').extract()
            tags = profile.css('div.tagBlock').xpath(
                './/div[@class="tagBubble unclickable"]/text()').extract()
            infos = sel.css('div.memberPointInfo')
            point = infos.xpath('.//div[@class="points"]/text()').extract()
            level = infos.xpath('.//div[@class="level tripcollectiveinfo"]/span/text()').extract()
            review_location = sel.xpath('//div[@class="cs-review-location"]/a/@href').extract()
            user['register_time'] = one(register_time)
            user['hometown'] = one(hometown)
            user['about'] = one(about)
            user['n_review'] = one(n_review)
            user['n_rating'] = one(n_rating)
            user['tags'] = tags
            user['level'] = one(level)
            user['point'] = one(point)
            # user['shares'] = review_location
            yield user
        return callback






