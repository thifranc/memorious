import logging
from newspaper import Article

from memorious.helpers.rule import Rule

log = logging.getLogger(__name__)

def parse_article(context: object, data: dict, article: Article) -> None:
    with context.http.rehash(data) as result:
        if result.html is not None:  
            properties = context.params.get("properties")
            data["schema"] = "Article"
            data["properties"] = {
                "title": result.html.xpath(properties["title"]) if properties.get("title") else getattr(article, "title", None),
                "description": result.html.xpath(properties.get("description")) if properties.get("description") else getattr(article, "description", None),
                "author": result.html.xpath(properties.get("author")) if properties.get("author") else getattr(article, "authors", None),
                "publishedAt": result.html.xpath(properties.get("publishedAt")) if properties.get("publishedAt") else getattr(article, "publish_date", None),
                "bodyText": result.html.xpath(properties.get("bodyText")) if properties.get("bodyText") else getattr(article, "text", None)
            }


def parse(context, data):
    with context.http.rehash(data) as result:
        news_article = Article(url=data["url"])
        news_article.download()
        news_article.parse()
        parse_article(context, data, news_article)

        if news_article.is_parsed == True:
            rules = context.params.get("match") or {"match_all": {}}
            if Rule.get_rule(rules).apply(result):
                context.emit(rule="store", data=data)

