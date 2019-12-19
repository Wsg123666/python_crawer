import asyncio
from pyppeteer import launch

eams_url = "https://jx.sspu.edu.cn/eams/login.action"
username = "1432"
password = "010022"

# 经济与管理学院: 27
# 国际交流学院（外国留学生事务办公室）: 31
# 工程训练中心: 32
# 体育部: 33
# 应用艺术设计学院: 34
# 文理学部: 491
# 工学部: 476
# 高等职业技术（国际）学院: 473
department = "27"

# 电子商务*: 1311
major = "1311"

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    await page.goto(eams_url)

    await page.type('#username', username)
    await page.type('#password', password)

    await page.click(".ip1")

    await page.goto("https://jx.sspu.edu.cn/eams/teach/grade/course/term-report.action")

    await page.select("#s1department", department)
    await page.select("#s1major", major)
    await page.click('input[value="查询"]')

    await page.screenshot({'path': 'login1.png', 'quality': 100, 'fullPage': True})
    print(await page.content())

    await page.click('#stu.code')

    await page.screenshot({'path': 'login.png', 'quality': 100, 'fullPage': True})
    # print(await page.content())
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
