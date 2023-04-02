from playwright.sync_api import sync_playwright
import csv
import datetime

product_list = []
start = datetime.datetime.now()

# adding objects for future data scraping to the list


def getting_objects(site, timeout):
    print('adding items to a list...')
    while True:
        product_list.extend(
            site.query_selector_all('div[data-id="product"]'))
        if site.locator('.pagination-widget__page-link_next').get_attribute('href') == 'javascript:':
            break
        site.click('.pagination-widget__page-link_next')
        site.wait_for_timeout(timeout)  # required for JS content to load


def parse_data(object, selector):
    return object.query_selector(selector).inner_text()


# rendering required source
with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    print('going to the site..')
    page.goto('https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/')
    # if NoneType AttributeError is raised - increase timeout value(+100-200 miliseconds incrementally)
    timeout = 1200
    page.wait_for_timeout(timeout)

    getting_objects(page, timeout)
    with open('prod_list_sync.csv', 'w') as file:
        writer = csv.DictWriter(
            file, fieldnames=['Title', 'Price'])
        writer.writeheader()
        print('Writing data to a csv file..')

        for i in product_list:
            title = parse_data(i, 'a>span')
            price = parse_data(i, 'div.product-buy__price')
            writer.writerow({'Title': title, 'Price': price})

print(datetime.datetime.now()-start)
