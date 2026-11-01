import urllib.request
import re

url = "https://agritech.tnau.ac.in/crop_protection/rice_diseases.html"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        # Find all disease links & images
        links = re.findall(r'<a\s+href=[\'"]([^\'"]+)[\'"]>([^<]+)</a>', html)
        print("TNAU links count:", len(links))
        for l, t in links:
            if any(k in l.lower() for k in ["dis", "prot", "paddy", "rice"]):
                print(f"{t.strip()} -> {l}")
        imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+\.(?:jpg|png|gif|jpeg))[\'"]', html, re.I)
        print("TNAU images:", len(imgs))
        for img in imgs[:10]:
            print("  IMG:", img)
except Exception as e:
    print("Error:", e)
