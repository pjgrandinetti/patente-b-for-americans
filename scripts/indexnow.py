#!/usr/bin/env python3
"""Tell the IndexNow search engines (Bing, Yandex, Seznam, Naver and others)
which pages of patente.physyapps.com changed, so they recrawl them soon.

Run AFTER the upload, since the engines fetch the pages and the key file:

    python3 scripts/indexnow.py            # pages whose sitemap lastmod is today
    python3 scripts/indexnow.py --all      # every page in the sitemap
    python3 scripts/indexnow.py URL ...    # just these addresses

The key is public by design: it is served at the site root as KEY.txt, which
is how the engines confirm the submission comes from the site's owner. A
change to the key is a new file at the root and a change to KEY below.
Google does not take part in IndexNow; Search Console covers Google.
"""
import datetime, json, pathlib, re, sys, urllib.request, urllib.error

KEY = "7f998e14198e70f01ce729f5e8272ca0"
HOST = "patente.physyapps.com"
SITE = "https://" + HOST
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "public_html" / "sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"

def sitemap_urls(only_today):
    text = SITEMAP.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    out = []
    for loc, mod in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", text):
        if not only_today or mod == today:
            out.append(loc)
    return out

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if args:
        urls = args
    else:
        urls = sitemap_urls(only_today="--all" not in argv)
    urls = [u for u in urls if u.startswith(SITE + "/")]
    if not urls:
        print("Nothing to submit: no page in the sitemap is dated today. "
              "Use --all for every page.")
        return 0
    body = json.dumps({"host": HOST, "key": KEY,
                       "keyLocation": f"{SITE}/{KEY}.txt",
                       "urlList": urls}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    meaning = {200: "accepted", 202: "accepted, key not yet confirmed",
               400: "bad request", 403: "key not valid or key file not found",
               422: "an address does not belong to the host",
               429: "too many requests"}.get(status, "unexpected")
    print(f"IndexNow: {len(urls)} address(es), HTTP {status} ({meaning})")
    return 0 if status in (200, 202) else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
