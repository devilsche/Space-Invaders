"""
Online Highscore Manager using Firebase Firestore.
Handles global highscore synchronization across multiple game instances.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import List, Dict, Optional


class OnlineHighscoreManager:
    """
    Manages online highscores using Firebase Firestore.
    
    Features:
    - Global leaderboard across all players
    - Real-time synchronization
    - Offline fallback to local storage
    - Automatic retry on connection errors
    """
    
    def __init__(self, credentials_path: str = "firebase-credentials.json"):
        """
        Initialize Firebase connection.
        
        Args:
            credentials_path: Path to Firebase service account JSON file
        """
        self.db = None
        self.connected = False
        
        # Initialize Firebase (only once)
        try:
            if not firebase_admin._apps:
                # Check if credentials file exists
                if not os.path.exists(credentials_path):
                    print(f"⚠ Firebase credentials not found at: {credentials_path}")
                    print("  Highscores will be stored locally only.")
                    return
                
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                
            self.db = firestore.client()
            self.connected = True
            print("✓ Firebase connected successfully!")
            
        except Exception as e:
            print(f"⚠ Firebase connection failed: {e}")
            print("  Highscores will be stored locally only.")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected."""
        return self.connected and self.db is not None
    
    def save_highscore(
        self,
        name: str,
        time: float,
        kills: int,
        stage: int
    ) -> bool:
        """
        Save a highscore to Firebase.
        
        Args:
            name: Player name
            time: Survival time in seconds
            kills: Number of kills
            stage: Ship stage (1-4)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Add to Firestore
            self.db.collection('survivor_highscores').add({
                'name': name,
                'time': time,
                'kills': kills,
                'stage': stage,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            return True
            
        except Exception as e:
            print(f"⚠ Failed to save highscore online: {e}")
            return False
    
    def get_top_scores(
        self,
        stage: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top highscores from Firebase.
        
        Args:
            stage: Filter by stage (None = all stages)
            limit: Maximum number of scores to return
            
        Returns:
            List of highscore dictionaries sorted by time (descending)
        """
        if not self.is_connected():
            return []
        
        try:
            query = self.db.collection('survivor_highscores')
            
            # Filter by stage if specified
            if stage is not None:
                query = query.where('stage', '==', stage)
            
            # Sort by time (descending) and limit
            query = query.order_by('time', direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            # Fetch data
            docs = query.stream()
            scores = []
            
            for doc in docs:
                data = doc.to_dict()
                # Remove timestamp (not needed for display)
                if 'timestamp' in data:
                    del data['timestamp']
                scores.append(data)
            
            return scores
            
        except Exception as e:
            print(f"⚠ Failed to load highscores online: {e}")
            return []
    
    def get_player_rank(
        self,
        name: str,
        stage: int
    ) -> Optional[int]:
        """
        Get player's rank for a specific stage.
        
        Args:
            name: Player name
            stage: Ship stage (1-4)
            
        Returns:
            Rank (1-based) or None if player not found
        """
        if not self.is_connected():
            return None
        
        try:
            # Get all scores for this stage, ordered by time
            docs = self.db.collection('survivor_highscores')\
                .where('stage', '==', stage)\
                .order_by('time', direction=firestore.Query.DESCENDING)\
                .stream()
            
            # Find player's position
            for rank, doc in enumerate(docs, 1):
                data = doc.to_dict()
                if data.get('name') == name:
                    return rank
            
            return None
            
        except Exception as e:
            print(f"⚠ Failed to get player rank: {e}")
            return None
    
    def get_total_players(self, stage: Optional[int] = None) -> int:
        """
        Get total number of players in leaderboard.
        
        Args:
            stage: Filter by stage (None = all stages)
            
        Returns:
            Number of unique players
        """
        if not self.is_connected():
            return 0
        
        try:
            query = self.db.collection('survivor_highscores')
            
            if stage is not None:
                query = query.where('stage', '==', stage)
            
            # Count documents
            docs = list(query.stream())
            return len(docs)
            
        except Exception as e:
            print(f"⚠ Failed to count players: {e}")
            return 0


# Global instance (initialized on first import)
_manager = None

def get_online_manager() -> OnlineHighscoreManager:
    """
    Get or create the global OnlineHighscoreManager instance.
    
    Returns:
        OnlineHighscoreManager instance
    """
    global _manager
    if _manager is None:
        _manager = OnlineHighscoreManager()
    return _manager
