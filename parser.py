import requests
import re
from bs4 import BeautifulSoup

proxies = {
    'http': '',
}


def getUrl(url):
    s = url.find('=') + 1
    e = url.find('&')
    return requests.utils.unquote(url[s:e])


def parse(url, lvl):
    if lvl == 0:
        return []
    res = requests.get(url, proxies=proxies)
    all_refs = []
    soup = BeautifulSoup(res.text, "html.parser")
    all_refs = soup.findAll(
        lambda tag: tag.name == "a" and
        tag.has_attr("href") and
        re.fullmatch(r'/url\?q=.*', tag["href"]))
    clear_refs = []
    for parent in all_refs:
        for child in parent.contents:
            if child.name == "h3":
                clear_refs.append(getUrl(parent["href"]))
    tmp = []
    for ref in clear_refs:
        tmp.append(parse(ref, lvl - 1))
    return clear_refs + tmp


def main():
    file_name_r = ["dict.txt", "words.txt"]
    file_name_w = "refs.txt"
    start = 0
    end = 100
    with open(file_name_r[0], "r") as file:
        for line in file:
            word = line.replace('\n', '').replace(' ', '+')
            for num_page in range(start, end, 10):
                url = 'http://www.google.com/search?q=' + \
                    word + '&ie=UTF-8&start=' + str(num_page)
                clear_refs = parse(url, 3)
                with open(file_name_w, "a") as file:
                    for line in clear_refs:
                        file.write(line + '\n')
    print("OK")


if __name__ == "__main__":
    main()
