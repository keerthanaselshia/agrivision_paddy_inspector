import urllib.request
import re

urls = [
    "http://rkb-odisha.in/crop-problems",
    "http://rkb-odisha.in/diseases",
    "http://rkb-odisha.in/nutrient-management",
    "http://rkb-odisha.in/rice-doctor"
]

for url in urls:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+\.(?:jpg|png|jpeg))[\'"]', html, re.I)
            print(f"[{url}] found {len(imgs)} images:")
            for img in imgs[:8]:
                print("   ", img)
    except Exception as e:
        print(f"[{url}] error: {e}")
