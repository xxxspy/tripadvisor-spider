# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class CityItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    url = Field()
    belong = Field()


class UserItem(scrapy.Item):
    name = Field()
    n_review = Field()
    point = Field()
    register_time = Field()
    hometown = Field()
    about = Field()
    n_rating = Field()
    tags = Field()
    level = Field()


class AttractionItem(scrapy.Item):
    name = Field()
    href = Field()
    n_review = Field()
    rate = Field()
    description = Field()
    category = Field()
    ratings_table = Field()
    address = Field()


class ReviewItem(scrapy.Item):
    attraction = Field()
    attraction_href = Field()
    title = Field()
    user_name = Field()
    location = Field()
    content = Field()
    likes = Field()
    shares = Field()


class NeighborItem(scrapy.Item):
    attraction = Field()
    attraction_href = Field()
    category = Field()
    distance = Field()
    rating = Field()
    n_review = Field()
    name = Field()
