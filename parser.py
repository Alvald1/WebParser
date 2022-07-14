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


def makeUrl(url1, url2):
    t = 0
    s = 0
    for i in range(0, len(url2)):
        if url2[i] == '/':
            t += 1
        if t == 2:
            s = i
            break
    return url1[:url1.find(url2[:s])]+url2


def parse_other(url):
    try:
        res = requests.get(url, proxies=proxies)
        all_refs = []
        soup = BeautifulSoup(res.text, "html.parser")
        all_refs = soup.findAll(
            lambda tag: tag.name == "a" and
            tag.has_attr("href") and
            re.fullmatch(r'http.*', tag["href"]))
        all_refs_2 = soup.findAll(
            lambda tag: tag.name == "a" and
            tag.has_attr("href") and
            re.fullmatch(r'/.*', tag["href"]))
        clear_refs = []
        for parent in all_refs:
            clear_refs.append(requests.utils.unquote((parent["href"])))
        clear_refs_2 = []
        for parent in all_refs_2:
            clear_refs_2.append(
                makeUrl(url, requests.utils.unquote((parent["href"]))))
        return clear_refs + clear_refs_2
    except Exception:
        return []


def parse_google(url):
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
        tmp.extend(parse_other(ref))
    return clear_refs + tmp


def parse_deep(url, lvl):
    url = url.replace('https', 'http')
    if lvl == 0:
        return []
    refs = parse_other(url)
    tmp = []
    for ref in refs:
        ref = ref.replace('https', 'http')
        if ref == url:
            continue
        tmp += parse_deep(ref, lvl - 1)
    return refs + tmp


def main():
    t = parse_deep('https://www.ebay.com/', 2)
    file_name_r = ["dict.txt", "words.txt"]
    file_name_w = "refs.txt"
    start = 0
    end = 10
    with open(file_name_r[0], "r") as file:
        for line in file:
            word = line.replace('\n', '').replace(' ', '+')
            for num_page in range(start, end, 10):
                url = 'http://www.google.com/search?q=' + \
                    word + '&ie=UTF-8&start=' + str(num_page)
                clear_refs = parse_google(url)
                with open(file_name_w, "a", encoding="utf-8") as file:
                    for line in clear_refs:
                        file.write(line + '\n')
    print("OK")


if __name__ == "__main__":
    main()
