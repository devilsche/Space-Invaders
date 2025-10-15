#!/usr/bin/env python3
"""Test script to check if Firebase Normal Mode top 10 can be retrieved"""

import sys
sys.path.insert(0, '.')

from system.online_highscore import OnlineHighscoreManager

# Initialize manager
manager = OnlineHighscoreManager()

print("="*60)
print("Testing Firebase Normal Mode Top 10 Retrieval")
print("="*60)

# Check connection
if manager.is_connected():
    print("✓ Connected to Firebase")
    
    # Get Normal Mode top 10 (stage=0)
    print("\nFetching Normal Mode Top 10 (stage=0)...")
    top_10 = manager.get_top_scores(stage=0, limit=10)
    
    if top_10:
        print(f"\n✓ Retrieved {len(top_10)} scores from Firebase:\n")
        print(f"{'Rank':<6} {'Name':<20} {'Score':<10} {'Kills':<8} {'Level':<6}")
        print("-" * 60)
        
        for i, entry in enumerate(top_10, 1):
            name = entry.get('name', 'Unknown')
            score = entry.get('score', 0)
            kills = entry.get('kills', 0)
            level = entry.get('level', 1)
            print(f"{i:<6} {name:<20} {score:<10} {kills:<8} {level:<6}")
    else:
        print("✗ No scores found or error occurred")
else:
    print("✗ Not connected to Firebase")
    print("Check your Firebase credentials and internet connection")

print("\n" + "="*60)
