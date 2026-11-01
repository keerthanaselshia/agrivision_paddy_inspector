import pathlib, re, shutil, sys
p = pathlib.Path(r"C:\Users\keert\paddy_dataset\scripts\merge_and_clean.py")
shutil.copy(p, str(p) + ".bak")
s = p.read_text(encoding="utf-8")
a = "ph = compute_phash(img_path)"
b = "if duplicate_found:"
m = "md5_set.add(md5)"
if s.count(a) != 1 or s.count(b) != 1 or s.count(m) != 1:
    sys.exit("Markers not found exactly once - nothing changed")
start = s.index(a)
end = s.index(b)
ls = s.rfind("\n", 0, start) + 1
indent = s[ls:start]
lines = [
    "ph = compute_phash(img_path)",
    "duplicate_found = False",
    "cur = int(ph, 16) if ph else None",
    "if cur is not None:",
    "    for other in seen_hashes.setdefault(target_class, []):",
    "        if bin(cur ^ other).count('1') <= near_dup_dist:",
    "            duplicate_found = True",
    "            break",
]
new_block = ("\n" + indent).join(lines) + "\n" + indent
s = s[:start] + new_block + s[end:]
s = s.replace(m, m + "\n" + indent + "if ph:\n" + indent + "    seen_hashes.setdefault(target_class, []).append(int(ph, 16))")
s, n = re.subn(r"^([ \t]*)phash_dict: [^\n]*= \{\}[ \t]*$", lambda mo: mo.group(0) + "\n" + mo.group(1) + "seen_hashes = {}", s, count=1, flags=re.M)
if n != 1:
    sys.exit("phash_dict line not found - nothing changed")
p.write_text(s, encoding="utf-8")
print("Patched OK")
