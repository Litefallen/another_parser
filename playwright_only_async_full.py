
from playwright.async_api import async_playwright

import csv
import datetime
import asyncio

# Lists to store product objects and parsed data
product_list = []
parsed_data = []
start = datetime.datetime.now()


# Asynchronous function to get product objects from a specific page
async def getting_objects(context, page_num, timeout):
    page = await context.new_page()
    await page.goto(
        f'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?p={page_num}')
    await page.wait_for_load_state()
    await page.wait_for_timeout(timeout)  # required for JS content to load
    prod_objects = await page.query_selector_all('div[data-id="product"]')
    product_list.extend(prod_objects)
    
# Asynchronous function to parse data from a product object
async def async_parse(object, *selectors):
    obj_list = []
    for selector in selectors:
        obj = await object.query_selector(selector)
        obj = await obj.inner_text()
        obj_list.append(obj)
    parsed_data.append(obj_list)

# Function to write parsed data to a CSV file
def csv_wrtr(*fieldnames):
    print('Writing data to a csv file..')
    with open('prod_list_async_full.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)
        writer.writerows(parsed_data)

# Main asynchronous function
async def main():
    async with async_playwright() as async_pl:
        # Launch a headless Firefox browser
        browser = await async_pl.firefox.launch(headless=True)
        context = await browser.new_context()
        new_page = await browser.new_page()
        # if NoneType AttributeError is raised - increase timeout value(+500 miliseconds incrementally)
        time_for_js = 7000
        print('going to the site..')
        # Navigate to the main page to extract the last page number
        await new_page.goto(
            'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/')

        last_page = await new_page.query_selector('.pagination-widget__page-link_last')
        last_page = await last_page.get_attribute('href')
        last_page = int(last_page.split('=')[1])
        await browser.close()
        print('getting objects from pages...')
        # chromium loads pages much faster(30-40% gains), but doesnt render JS in headless idk
        browser = await async_pl.chromium.launch(headless=False)
        # chromium could create multiple table in one window, but firefox couldnt.
        context = await browser.new_context()
        await asyncio.gather(*[getting_objects(context, page_num, time_for_js) for page_num in range(1, last_page+1)])
        print('parsing data..')
        await asyncio.gather(*[async_parse(i, 'a>span', 'div.product-buy__price') for i in product_list])
asyncio.run(main())
print('parsing finished')
csv_wrtr('Name', 'Price')
print(datetime.datetime.now()-start)
