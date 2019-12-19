import asyncio
from pyppeteer import launch
import requests

oa_url = "https://id.sspu.edu.cn/cas/login"
sport_url = "https://tygl.sspu.edu.cn/SportScore/default.aspx"
username = "20171130314"
password = "19990206lyz"

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    # await page.goto(oa_url)
    #
    # await page.type('#username', username)
    # await page.type('#password', password)
    #
    # await page.click('.submit_button')

    await page.goto(sport_url)

    # await page.click('#Button1')

    # cookie_list = await page.cookies()
    #
    # for cookie in cookie_list:
    #     if cookie["name"] == "JSESSIONID":
    #         return cookie["value"]
    #
    # return None

    await page.screenshot({'path': 'gmail-login.png', 'quality': 100, 'fullPage': True})


asyncio.get_event_loop().run_until_complete(main())

