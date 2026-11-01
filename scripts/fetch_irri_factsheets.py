import urllib.request
import re

url = "http://www.knowledgebank.irri.org/decision-tools/rice-doctor/rice-doctor-fact-sheets"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        matches = re.findall(r'<a\s+href=[\'"](/decision-tools/rice-doctor/rice-doctor-fact-sheets/[^\'"]+)[\'"]>([^<]+)</a>', html)
        print("Total IRRI Fact Sheets found:", len(matches))
        for link, title in matches:
            t = title.strip()
            if True or any(w in t.lower() for w in ["streak", "rot", "stunt", "zinc", "nitrogen", "potassium", "iron", "discoloration", "blight", "smut"]):
                print(f"{t} -> http://www.knowledgebank.irri.org{link}")
except Exception as e:
    print("Error:", e)
