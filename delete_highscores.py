"""
Script to delete all highscores from Firebase.
Run this to reset the online leaderboard.
"""

from system.online_highscore import get_online_manager

def delete_all_highscores():
    """Delete all online highscores from Firebase"""
    manager = get_online_manager()
    
    if not manager or not manager.is_connected():
        print("❌ Firebase not connected!")
        return
    
    print("🗑️  Deleting all online highscores...")
    
    try:
        # Get all documents
        docs = manager.db.collection('survivor_highscores').stream()
        
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        
        print(f"✅ Deleted {count} highscores from Firebase")
        
    except Exception as e:
        print(f"❌ Error deleting highscores: {e}")

if __name__ == "__main__":
    import sys
    
    print("⚠️  WARNING: This will delete ALL online highscores!")
    response = input("Are you sure? (yes/no): ")
    
    if response.lower() == "yes":
        delete_all_highscores()
    else:
        print("Cancelled.")
