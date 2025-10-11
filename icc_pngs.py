# list_icc_pngs.py
import os
from PIL import Image

root = "assets"   # anpassen
hits = []
for dirpath, _, files in os.walk(root):
    for name in files:
        if name.lower().endswith(".png"):
            p = os.path.join(dirpath, name)
            try:
                with Image.open(p) as im:
                    if im.info.get("icc_profile"):
                        hits.append(p)
            except Exception as e:
                print("FEHLER:", p, e)

print("\nMit ICC-Profil:")
for p in hits:
    print(p)

    with Image.open(p) as im:
        im.save(p, optimize=True)  # kein icc_profile => entfernt
        print( f"Entfernt aus {p}")
