import urllib.request
import re

url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_diseases_cereals_paddy.html"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        # Find all images
        imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+\.(?:jpg|png|gif|jpeg))[\'"]', html, re.I)
        print("TNAU total images found:", len(imgs))
        for img in imgs:
            print("  IMG:", img)
except Exception as e:
    print("Error:", e)
