import pathlib, shutil
p = pathlib.Path(r"C:\Users\keert\paddy_dataset\app\app.py")
shutil.copy(p, str(p) + ".bak")
s = p.read_text(encoding="utf-8-sig")
a = s.index("def severity(")
b = s.index("def grade(")
new = '''def severity(img_rgb, sat_min, lesion_hue_max):
    # Leaf region = largest green area, closed and filled so lesions inside it stay inside.
    # Lesion = non-green pixels inside the leaf region. Background outside is ignored.
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hue, sat, val = cv2.split(hsv)
    green = ((hue >= lesion_hue_max + 2) & (hue <= 95) & (sat >= sat_min) & (val >= 40)).astype(np.uint8) * 255
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    closed = cv2.morphologyEx(green, cv2.MORPH_CLOSE, k)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    leaf = np.zeros_like(closed)
    if contours:
        c = max(contours, key=cv2.contourArea)
        cv2.drawContours(leaf, [c], -1, 255, thickness=-1)
    lesion = (leaf > 0) & (green == 0)
    lesion = cv2.morphologyEx(lesion.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    total = int(np.count_nonzero(leaf))
    pct = 100.0 * int(np.count_nonzero(lesion)) / total if total else 0.0
    overlay = img_rgb.copy()
    overlay[lesion] = (0.5 * overlay[lesion] + 0.5 * np.array([255, 0, 0])).astype(np.uint8)
    return pct, overlay
'''
s = s[:a] + new + "\n\n" + s[b:]
p.write_text(s, encoding="utf-8")
print("Patched OK")
