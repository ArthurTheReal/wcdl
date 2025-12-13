from bs4 import BeautifulSoup
from wcdl import tools
from wcdl.settings import *

"""
fetch.py - handles the scrapping part such as search and retrieving download links
"""


def search(query: str) -> list[dict]:
    """
    searches and returns the results of it in a list

    Args:
        query(str): query for search

    Returns:
        list[dict]: the search result, each one has these keys: manga_id, title, url, poster, year, status, type, authors, tags

    if connection fails it retrys for 5 times (with some delay between them) and if problem still remains, it will exit with code 1
    """

    headers = tools.random_headers(SEARCH_URL)
    params = {
        "author": "",
        "text": query,
        "sort": "Best Match",
        "order": "Descending",
        "official": "Any",
        "anime": "Any",
        "adult": "Any",
        "display_mode": "Full Display",
    }
    response = tools.safe_request(SEARCH_URL, params=params, headers=headers)
    if response == None:
        exit(1)

    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for article in soup.find_all("article", recursive=False):
        # poor me and anyone who is going to read this part of the code in feature T.T
        sections = article.find_all("section", recursive=False)

        url = sections[0].find("a").get("href")
        title = sections[1].find("div").find("a").string
        poster = (
            sections[0].find("a").find("article").find("picture").find("img").get("src")
        )
        manga_id = url.split("/")[4]
        year = sections[1].find_all("div")[1].find("span").string
        status = sections[1].find_all("div")[2].find("span").string
        type_ = sections[1].find_all("div")[3].find("span").string

        authors = []
        tags = []

        for span in sections[1].find_all("div")[4].find_all("span", recursive=False):
            authors.append(span.find("a").string)

        del span
        for span in sections[1].find_all("div")[5].find_all("span", recursive=False):
            tags.append(span.string.replace(",", ""))

        results.append(
            {
                "manga_id": manga_id,
                "title": title,
                "url": url,
                "poster": poster,
                "year": year,
                "status": status,
                "type": type_,
                "authors": authors,
                "tags": tags,
            }
        )

    return results


def get_chapters(manga_id: str) -> list[dict]:
    """
    gets the list of chapters

    Args:
        manga_id(str): you can get this id from the search() functions result

    Returns:
        list[dict]: each item of this list has these keys: title, url, date_added, chapter_id

    if connection fails it retrys for 5 times (with some delay between them) and if problem still remains, it will exit with code 1
    """

    url = CHAPTER_LIST_URL.format(manga_id)
    headers = tools.random_headers(url)
    response = tools.safe_request(url, headers=headers)

    if response is None:
        exit(0)

    soup = BeautifulSoup(response.text, "html.parser")

    reuslts = []

    for div in soup.find_all("div", {"class": "flex items-center"}, recursive=False):
        link = div.find("a").get("href")
        name = div.find("a").find_all("span", recursive=False)[1].find("span").string
        date = div.find("a").find("time").string.split("T")[0]
        reuslts.append(
            {
                "title": name,
                "url": link,
                "date_added": date,
                "chapter_id": link.split("/")[-1],
            }
        )

    reuslts.reverse()
    return reuslts


def get_chapter_images(chapter_id: str) -> list[str]:
    """
    gets the urls for images of the chapter

    Args:
        chapter_id(str): you can get this from get_chapter() functions result

    Returns:
        list[str]: a ordered list of urls for the images of the chapter

    if connection fails it retrys for 5 times (with some delay between them) and if problem still remains, it will exit with code 1
    """

    url = CHAPTER_IMAGES_URL.format(chapter_id)
    headers = tools.random_headers(url)
    params = {
        "is_prev": "False",
        "current_page": "1",
        "reading_style": "long_strip",
    }

    response = tools.safe_request(url, headers=headers, params=params)
    if response is None:
        exit(1)

    soup = BeautifulSoup(response.text, "html.parser")

    result = []
    for img in soup.find("section").find_all("img", recursive=False):
        result.append(img.get("src"))

    return result
