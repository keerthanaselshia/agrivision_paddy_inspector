from pathlib import Path
from datetime import datetime
import shutil

app = Path("app/app.py")
source = app.read_text(encoding="utf-8")

# Find and validate every insertion point before changing anything.
if 'from app.history_db import init_db, save_inspection' in source:
    raise SystemExit("History imports already exist. No changes made.")

if 'st.title("AgriVision Paddy Inspector")' not in source:
    raise SystemExit("Could not find the app title. No changes made.")

if 'uncertain = label is not None and conf < conf_min' not in source:
    raise SystemExit("Could not find the prediction confidence check. No changes made.")

if 'import streamlit as st' not in source:
    raise SystemExit("Could not find the Streamlit import. No changes made.")

lines = source.splitlines(keepends=True)

# Add imports after the existing Streamlit import.
import_index = next(
    i for i, line in enumerate(lines)
    if line.strip() == "import streamlit as st"
)
lines[import_index + 1:import_index + 1] = [
    "import hashlib\n",
    "from app.history_db import init_db, save_inspection\n",
    "from app.history_dashboard import show_history_dashboard\n",
    "\n",
    "init_db()\n",
]

# Add navigation immediately after the app's introductory caption.
title_index = next(
    i for i, line in enumerate(lines)
    if 'st.title("AgriVision Paddy Inspector")' in line
)
caption_index = next(
    (i for i in range(title_index + 1, len(lines))
     if "st.caption(" in lines[i]),
    None
)
if caption_index is None:
    raise SystemExit("Could not find the introductory caption. No changes made.")

navigation = [
    "\n",
    'page = st.sidebar.radio(\n',
    '    "Navigation", ["Inspect Leaf", "Inspection History"]\n',
    ")\n",
    'if page == "Inspection History":\n',
    "    show_history_dashboard()\n",
    "    st.stop()\n",
    "\n",
]
lines[caption_index + 1:caption_index + 1] = navigation

# Save a completed prediction once per image within the current session.
uncertain_index = next(
    i for i, line in enumerate(lines)
    if line.strip() == "uncertain = label is not None and conf < conf_min"
)
saving_code = [
    "\n",
    "if label is not None:\n",
    "    image_hash = hashlib.sha256(img.tobytes()).hexdigest()\n",
    '    if image_hash != st.session_state.get("last_saved_image_hash"):\n',
    '        saved_label = ADVICE.get(label, {}).get("name", label)\n',
    "        if uncertain:\n",
    '            saved_label = f"Uncertain - {saved_label}"\n',
    "        save_inspection(\n",
    "            disease=saved_label,\n",
    "            confidence=conf,\n",
    "            severity=sev,\n",
    "            severity_grade=grade(sev),\n",
    "            location=location,\n",
    "        )\n",
    '        st.session_state["last_saved_image_hash"] = image_hash\n',
]
lines[uncertain_index + 1:uncertain_index + 1] = saving_code

updated = "".join(lines)

# Verify Python syntax before writing.
compile(updated, str(app), "exec")

backup = app.with_name(
    "app.py.backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
shutil.copy2(app, backup)
app.write_text(updated, encoding="utf-8")

print("Patch successful.")
print("Backup:", backup)
print("Updated:", app)
print("Python syntax: OK")
