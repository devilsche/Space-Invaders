#!/usr/bin/env python3
"""
Synchronisiert Firebase Highscores zur lokalen Datei.
Lädt alle Online-Scores und speichert sie lokal.
"""

import sys
import json
sys.path.insert(0, '.')

from ..manager.highscore_manager import HighscoreManager

HIGHSCORE_FILE = "data/highscore.json"

# Initialize manager
manager = HighscoreManager()

print("="*70)
print("Firebase → Local Highscore Synchronization")
print("="*70)

# Check connection
if manager.is_connected():
    print("✓ Connected to Firebase")
    
    # Get ALL Normal Mode scores from Firebase
    print("\nFetching ALL Normal Mode scores (stage=0) from Firebase...")
    try:
        online_scores = manager.get_top_scores(stage=0, limit=1000)  # Hole viele
        print(f"✓ Retrieved {len(online_scores)} scores from Firebase")
        
        if online_scores:
            # Lade existierende lokale Scores
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        local_scores = data
                    else:
                        local_scores = []
                print(f"✓ Loaded {len(local_scores)} existing local scores")
            except:
                local_scores = []
                print("ℹ No existing local scores found")
            
            # Kombiniere beide Listen und entferne Duplikate
            all_scores = []
            seen = set()  # Track (name, score, kills, level) um Duplikate zu vermeiden
            
            for score in online_scores + local_scores:
                # Stelle sicher, dass alle Felder vorhanden sind
                if "kills" not in score:
                    score["kills"] = 0
                if "level" not in score:
                    score["level"] = 1
                    
                key = (
                    score.get('name', ''), 
                    score.get('score', 0), 
                    score.get('kills', 0),
                    score.get('level', 1)
                )
                if key not in seen:
                    seen.add(key)
                    all_scores.append(score)
            
            # Sortiere nach Score (primär) und Kills (sekundär)
            all_scores.sort(key=lambda x: (x.get('score', 0), x.get('kills', 0)), reverse=True)
            
            # Speichere ALLE Scores lokal (nicht nur Top 10)
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    json.dump(all_scores, f, indent=2)
                print(f"\n✓ Saved {len(all_scores)} unique scores to {HIGHSCORE_FILE}")
                print(f"  - {len(online_scores)} from Firebase")
                print(f"  - {len(local_scores)} from local")
                print(f"  - {len(all_scores)} unique total")
                
                # Zeige Top 10
                print("\nTop 10:")
                print(f"{'Rank':<6} {'Name':<20} {'Score':<10} {'Kills':<8} {'Level':<6}")
                print("-" * 60)
                for i, entry in enumerate(all_scores[:10], 1):
                    name = entry.get('name', 'Unknown')
                    score = entry.get('score', 0)
                    kills = entry.get('kills', 0)
                    level = entry.get('level', 1)
                    print(f"{i:<6} {name:<20} {score:<10} {kills:<8} {level:<6}")
                    
            except Exception as e:
                print(f"✗ Failed to save: {e}")
        else:
            print("ℹ No scores found in Firebase")
            
    except Exception as e:
        print(f"✗ Failed to fetch scores: {e}")
else:
    print("✗ Not connected to Firebase")
    print("Check your Firebase credentials and internet connection")

print("\n" + "="*70)
