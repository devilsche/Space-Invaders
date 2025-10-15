# Firebase Credentials Setup Guide

## 🔐 Sicherer Umgang mit Firebase Credentials

### Wo speichern?

**Option 1: Im Projekt-Root (aktuell verwendet)**
```
Space-Invaders/
├── firebase-credentials.json  ← HIER (in .gitignore)
├── main.py
└── ...
```

**Option 2: In separatem credentials Ordner (empfohlen)**
```
Space-Invaders/
├── credentials/
│   └── firebase-credentials.json  ← HIER
├── main.py
└── ...
```

**Option 3: Außerhalb des Projekts (am sichersten)**
```
~/
├── .credentials/
│   └── space-invaders-firebase.json  ← HIER
└── projects/
    └── Space-Invaders/
```

---

## 🛡️ Sicherheitsmaßnahmen

### 1. .gitignore prüfen
Die Datei `.gitignore` enthält bereits:
```gitignore
# Firebase credentials (keep local only!)
firebase-credentials.json
```

Wenn du Option 2 nutzen möchtest, füge hinzu:
```gitignore
# Firebase credentials
firebase-credentials.json
credentials/
```

### 2. Niemals committen!
```bash
# Prüfe, ob Credentials im Git sind:
git log --all --full-history --oneline -- firebase-credentials.json

# Falls doch committed, entferne aus History:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch firebase-credentials.json" \
  --prune-empty --tag-name-filter cat -- --all
```

### 3. Backup erstellen
```bash
# Erstelle verschlüsseltes Backup (mit Passwort):
7z a -p -mhe=on firebase-backup.7z firebase-credentials.json

# Oder cloud backup (verschlüsselt):
cp firebase-credentials.json ~/Dropbox/.credentials/
```

---

## 🔧 Code-Anpassungen für verschiedene Speicherorte

### Aktuelle Implementierung:
```python
# system/online_highscore.py
def __init__(self, credentials_path: str = "firebase-credentials.json"):
```

### Für Option 2 (credentials Ordner):
```python
def __init__(self, credentials_path: str = "credentials/firebase-credentials.json"):
```

### Für Option 3 (außerhalb Projekt):
```python
import os
from pathlib import Path

def __init__(self, credentials_path: str = None):
    if credentials_path is None:
        # Versuche verschiedene Speicherorte
        possible_paths = [
            "firebase-credentials.json",  # Projekt-Root
            "credentials/firebase-credentials.json",  # Credentials-Ordner
            Path.home() / ".credentials" / "space-invaders-firebase.json",  # Home-Verzeichnis
        ]
        for path in possible_paths:
            if os.path.exists(path):
                credentials_path = str(path)
                break
```

---

## 📦 Setup für neue Entwickler

### Schritt 1: Credentials von Admin erhalten
Der Projekt-Admin muss dir die `firebase-credentials.json` Datei **sicher** senden:
- ✅ Via verschlüsselte E-Mail
- ✅ Via 1Password / LastPass Share
- ✅ Via sicherer Cloud-Speicher mit Ablaufdatum
- ❌ NICHT via Discord/Slack/unverschlüsselt

### Schritt 2: Datei speichern
```bash
# Option 1: Im Projekt-Root
cd Space-Invaders
# Speichere firebase-credentials.json hier

# Option 2: Credentials-Ordner erstellen
mkdir credentials
# Speichere firebase-credentials.json in credentials/

# Option 3: Home-Verzeichnis
mkdir -p ~/.credentials
# Speichere als ~/.credentials/space-invaders-firebase.json
```

### Schritt 3: Berechtigungen setzen (Linux/Mac)
```bash
chmod 600 firebase-credentials.json
# Nur Owner kann lesen/schreiben
```

### Schritt 4: Testen
```bash
python test_firebase_top10.py
# Sollte "✓ Firebase connected successfully!" zeigen
```

---

## 🚨 Was tun bei Credentials-Leak?

Falls die Credentials versehentlich ins Git committed wurden:

### 1. Sofort Firebase Console öffnen
1. Gehe zu [Firebase Console](https://console.firebase.google.com/)
2. Wähle dein Projekt
3. Settings → Service Accounts
4. **Lösche den alten Service Account**
5. **Erstelle einen neuen Service Account**
6. **Lade neue credentials.json herunter**

### 2. Git History bereinigen
```bash
# WARNUNG: Ändert Git History!
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch firebase-credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (VORSICHT bei Team-Projekten!)
git push origin --force --all
```

### 3. Alle Entwickler informieren
- Neue Credentials verteilen
- Git Repository neu klonen

---

## 📝 Best Practices Zusammenfassung

✅ **DO:**
- Credentials in `.gitignore` eintragen
- Verschlüsselte Backups erstellen
- Berechtigungen einschränken (chmod 600)
- Regelmäßig rotieren (alle 6-12 Monate)

❌ **DON'T:**
- Credentials committen
- In Slack/Discord teilen
- Im Code hardcoden
- Auf öffentlichen Servern speichern

---

## 🔗 Weitere Ressourcen

- [Firebase Security Best Practices](https://firebase.google.com/docs/admin/setup#initialize-sdk)
- [Git Filter-Branch Guide](https://git-scm.com/docs/git-filter-branch)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

**Letzte Aktualisierung:** October 15, 2025  
**Nächste Review:** April 2026
