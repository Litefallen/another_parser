
from playwright.async_api import async_playwright

import csv
import datetime
import asyncio
product_list = []
parsed_data = []
start = datetime.datetime.now()


async def getting_objects(site, timeout):
    print('adding items to a list...')
    prod_objects = await site.query_selector_all('div[data-id="product"]')
    product_list.extend(prod_objects)
    while True:
        prod_objects = await site.query_selector_all('div[data-id="product"]')
        product_list.extend(prod_objects)
        next_p = site.locator(
            '.pagination-widget__page-link_next')
        if await next_p.get_attribute('href') == 'javascript:':
            break
        await site.click('.pagination-widget__page-link_next')
        await site.wait_for_timeout(timeout)  # required for JS content to load

# rendering required source


async def async_parse(object, *selectors):
    obj_list = []
    for selector in selectors:
        obj = await object.query_selector(selector)
        obj = await obj.inner_text()
        obj_list.append(obj)
    parsed_data.append(obj_list)


def csv_wrtr(*fieldnames):
    print('Writing data to a csv file..')
    with open('prod_list_async_partial.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)
        writer.writerows(parsed_data)


async def main():
    async with async_playwright() as async_pl:
        browser = await async_pl.firefox.launch()
        page = await browser.new_page()
        # if NoneType AttributeError is raised - increase timeout value(+100-200 miliseconds incrementally)
        timeout_for_js = 1200
        print('going to the site..')
        await page.goto(
            'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/')
        await getting_objects(page, timeout_for_js)
        print('parsing data..')
        await asyncio.gather(*[async_parse(i, 'a>span', 'div.product-buy__price') for i in product_list])

asyncio.run(main())
csv_wrtr('Name', 'Price')
print(datetime.datetime.now()-start)
