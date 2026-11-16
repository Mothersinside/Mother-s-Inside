import os, json, urllib.request, urllib.parse
from datetime import datetime, timedelta

TOKEN   = os.environ['FB_ACCESS_TOKEN']
IG_ID   = os.environ['IG_USER_ID']
PAGE_ID = os.environ['FB_PAGE_ID']
API     = 'https://graph.facebook.com/v18.0'

def get(path, params):
    params['access_token'] = TOKEN
    with urllib.request.urlopen(f"{API}{path}?{urllib.parse.urlencode(params)}") as r:
        return json.load(r)

def fmt(n):
    n = int(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M+"
    if n >= 1_000:     return f"{n/1_000:.1f}K+"
    return f"{n}+"

since = int((datetime.utcnow() - timedelta(days=30)).timestamp())
until = int(datetime.utcnow().timestamp())

try:
    ig      = get(f"/{IG_ID}",   {"fields": "followers_count"})
    ig_ins  = get(f"/{IG_ID}/insights", {"metric": "views", "period": "day",
                    "since": since, "until": until})
    ig_views = sum(d['values'][0]['value'] for d in ig_ins.get('data', [])
                   if d.get('values'))
except Exception as e:
    print("IG fetch error:", e)
    ig, ig_views = {}, 0

try:
    fb      = get(f"/{PAGE_ID}", {"fields": "followers_count"})
    fb_ins  = get(f"/{PAGE_ID}/insights", {"metric": "page_views_total",
                    "period": "day", "since": since, "until": until})
    fb_views = sum(d['values'][0]['value'] for d in fb_ins.get('data', [])
                   if d.get('values'))
except Exception as e:
    print("FB fetch error:", e)
    fb, fb_views = {}, 0

out = {
    "igFollowers": fmt(ig.get("followers_count")),
    "igViews":     fmt(ig_views),
    "fbViews":     fmt(fb_views),
    "fbFollowers": fmt(fb.get("followers_count")),
    "updatedAt":   datetime.utcnow().isoformat() + "Z"
}

with open("stats.json", "w") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2))