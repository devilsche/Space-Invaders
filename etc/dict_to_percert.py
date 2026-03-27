def percent_table(d):
    # Keys wie 'start' ignorieren
    items = {k: v for k, v in d.items() if k != 'start' and isinstance(v, (int,float))}
    total = sum(items.values()) or 1.0
    rows = [
        (k, v, round(v / total * 100, 2))
        for k, v in sorted(items.items(), key=lambda x: x[1], reverse=True)
    ]
    print(f"Gesamt: {total:.4f} s")
    print(f"{'Kategorie':<14} {'Sekunden':>9} {'%':>7}")
    for k, v, p in rows:
        print(f"{k:<14} {v:9.4f} {p:7.2f}")



