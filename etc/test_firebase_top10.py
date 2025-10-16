#!/usr/bin/env python3
"""Test script to check if Firebase Normal Mode top 10 can be retrieved"""

import sys
sys.path.insert(0, '.')

from manager.highscore_manager import HighscoreManager

# Initialize manager
manager = HighscoreManager()

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
        print(f"{'Rank':<6} {'Name':<20} {'Score':<10} {'Kills':<8} {'Level':<6} {'Timestamp':<20}")
        print("-" * 87)

        for i, entry in enumerate(top_10, 1):
            name = entry.get('name', 'Unknown')
            score = entry.get('score', 0)
            kills = entry.get('kills', 0)
            level = entry.get('level', 1)
            timestamp = entry.get('timestamp', 'N/A')
            print(f"{i:<6} {name:<20} {score:<10} {kills:<8} {level:<6} {timestamp:<20}")
    else:
        print("✗ No scores (Normal Mode) found or error occurred")

    for i in range(1, 5):
        print(f"\nFetching Survivor Top 10 (stage={i})...")
        top_10 = manager.get_top_scores(stage=i, limit=10)

        if top_10:
            print(f"\n✓ Retrieved {len(top_10)} scores from Firebase:\n")
            print(f"{'Rank':<6} {'Name':<20} {'Time (s)':<10} {'Kills':<8} {'Stage':<6} {'Timestamp':<20}")
            print("-" * 87)

            for j, entry in enumerate(top_10, 1):
                name = entry.get('name', 'Unknown')
                time = entry.get('time', 0)
                kills = entry.get('kills', 0)
                stage = entry.get('stage', 0)
                timestamp = entry.get('timestamp', 'N/A')
                print(f"{j:<6} {name:<20} {time:<10.2f} {kills:<8} {stage:<6} {timestamp:<20}")
        else:
            print(f"✗ No scores found (Survivor Top 10 (stage={i})) or error occurred")


else:
    print("✗ Not connected to Firebase")
    print("Check your Firebase credentials and internet connection")

print("\n" + "="*87)
