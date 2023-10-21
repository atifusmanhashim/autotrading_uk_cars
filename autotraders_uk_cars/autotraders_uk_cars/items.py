# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutotradersUkCarsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    car_name=scrapy.Field()
    car_details_url=scrapy.Field()
    car_engine=scrapy.Field()
    car_fuel_type=scrapy.Field()
    car_mileage=scrapy.Field()
    car_registration=scrapy.Field()
    car_body_type=scrapy.Field()
    car_gearbox=scrapy.Field()
    car_seats=scrapy.Field()
    car_emission_class=scrapy.Field()
    car_description_details=scrapy.Field()
    car_experts_reviews=scrapy.Field()
    car_buyer_reviews=scrapy.Field()
    car_images=scrapy.Field()
    car_price=scrapy.Field()
