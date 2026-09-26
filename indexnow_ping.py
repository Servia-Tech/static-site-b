"""Submit every URL in sitemap.xml to IndexNow (Bing, Yandex, Seznam, Naver...).

Run AFTER the site is deployed:  py -3.12 indexnow_ping.py
Standard library only. The key file must be live at https://uaesettlement.com/<KEY>.txt
"""
import json
import re
import sys
import urllib.error
import urllib.request

HOST = "uaesettlement.com"
KEY = "d011935629dad9143fc3cbe52682655b"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
SITEMAP = f"https://{HOST}/sitemap.xml"
ENDPOINT = "https://api.indexnow.org/IndexNow"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "indexnow-ping/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", fetch(SITEMAP))
    urls = [u for u in urls if u.startswith(f"https://{HOST}/")]
    if not urls:
        sys.exit("No URLs found in sitemap")
    live_key = fetch(KEY_LOCATION).strip()
    if live_key != KEY:
        sys.exit(f"Key file at {KEY_LOCATION} does not match KEY")
    payload = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": urls}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=payload, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")
    except urllib.error.HTTPError as e:
        print(f"IndexNow: HTTP {e.code} {e.reason}: {e.read().decode('utf-8', 'replace')[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
