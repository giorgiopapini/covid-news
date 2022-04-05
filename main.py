from flask import Flask, jsonify, request
from selenium import webdriver
from threading import Thread
from github import Github
import constants
import json

from article_class import Article

app = Flask(__name__)


@app.route('/', methods=["GET"])
def get_news():

    news = {}
    for name in constants.REGIONI_NAME:
        fixed_name = name.replace(" ", "").replace("'", "").replace("P.A.", "")
        data = scrape(f"https://news.google.com/search?for=covid+{fixed_name}&hl=it&gl=IT&ceid=IT:it")
        news[name] = data
        pass

    json_data = json.dumps(news)
    load_articles(json_data)
    return jsonify(news)


def scrape(url):

    PATH = "C:\Program Files (x86)/chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    driver.get(url)

    buttons = driver.find_elements_by_tag_name("button")
    webdriver.ActionChains(driver).click(buttons[len(buttons) - 1]).perform()

    raw_articles = driver.find_elements_by_tag_name("article")
    images = driver.find_elements_by_tag_name("figure")

    articles = get_articles(raw_articles, images)

    driver.close()
    print("=====================================================")
    print(articles)
    return articles


def get_articles(raw_articles, images):
    complete_articles = []
    index = 0
    while len(complete_articles) < 20:
        try:
            if raw_articles[index].text != "":
                elements = raw_articles[index].text.split("\n")
                url = raw_articles[index].find_element_by_xpath("./a").get_attribute("href")
                image_url = images[index].find_element_by_xpath("./img").get_attribute("src")
                complete_articles.append(
                    Article(
                        title=elements[0],
                        author=elements[1],
                        date=elements[2],
                        url=url,
                        image_url=image_url,
                    ).__dict__
                )
            index += 1
        except IndexError:
            get_articles(raw_articles, images)
    return complete_articles


def load_articles(json_data):
    git = Github(constants.TOKEN)
    repo = git.get_repo("news-dev/news-data")
    print(repo.name)
    contents = repo.get_contents("news.json")
    repo.update_file(contents.path, json_data, json_data, contents.sha)


if __name__ == "__main__":
    app.run()
