# Firebase Credentials sicher teilen

## ⚠️ WICHTIG: Was NICHT tun!

❌ **NIEMALS:**
- Via Discord/Slack/Teams unverschlüsselt senden
- In E-Mail als Klartext anhängen
- Via GitHub/GitLab hochladen
- In öffentliche Cloud ohne Verschlüsselung
- Per WhatsApp/SMS senden
- Screenshot machen und teilen

---

## ✅ Sichere Methoden (vom sichersten zum einfachsten)

### 1. Password Manager Share (EMPFOHLEN) ⭐⭐⭐

**Mit 1Password:**
```
1. Öffne 1Password
2. Erstelle neuen "Secure Note"
3. Füge firebase-credentials.json Inhalt ein
4. Klicke "Share" → "Copy Secure Link"
5. Link hat Ablaufdatum und kann nur 1x verwendet werden
6. Sende Link via E-Mail/Discord
```

**Mit Bitwarden:**
```
1. Öffne Bitwarden → "Send"
2. Wähle "File" → firebase-credentials.json hochladen
3. Setze Ablaufdatum (z.B. 7 Tage)
4. Setze maximale Zugriffe (z.B. 1)
5. Optional: Passwort hinzufügen
6. Kopiere Link und sende via E-Mail/Discord
```

**Mit LastPass:**
```
1. Security Challenge → Emergency Access
2. Oder: Shared Folder für Team
```

---

### 2. Verschlüsselte Datei (SEHR SICHER) ⭐⭐⭐

#### Option A: 7-Zip mit Passwort
```bash
# Datei verschlüsseln (Windows/Linux/Mac)
7z a -p -mhe=on firebase-creds.7z firebase-credentials.json

# Wird nach Passwort fragen (mind. 16 Zeichen!)
# Sende firebase-creds.7z via E-Mail/Cloud
# Sende Passwort via separatem Kanal (z.B. SMS/Anruf)

# Empfänger entschlüsselt mit:
7z x firebase-creds.7z
```

#### Option B: GPG Verschlüsselung
```bash
# Empfänger's Public Key importieren
gpg --import empfaenger-public-key.asc

# Datei verschlüsseln für Empfänger
gpg --encrypt --recipient empfaenger@email.com firebase-credentials.json

# Sendet firebase-credentials.json.gpg via E-Mail/Cloud
# Nur Empfänger kann mit Private Key entschlüsseln
```

#### Option C: OpenSSL (überall verfügbar)
```bash
# Verschlüsseln mit Passwort
openssl enc -aes-256-cbc -salt -in firebase-credentials.json -out firebase-creds.enc

# Sendet firebase-creds.enc + Passwort via separate Kanäle
# Empfänger entschlüsselt mit:
openssl enc -d -aes-256-cbc -in firebase-creds.enc -out firebase-credentials.json
```

---

### 3. Sichere File-Sharing Dienste (SICHER) ⭐⭐

**Firefox Send (empfohlen, wenn verfügbar):**
```
1. Gehe zu https://send.vis.ee/ (Firefox Send Alternative)
2. Wähle firebase-credentials.json
3. Setze:
   - 1 Download
   - 1 Tag Ablauf
   - Passwort erforderlich
4. Kopiere Link + Passwort
5. Sende Link via Discord, Passwort via SMS
```

**Tresorit Send:**
```
1. Gehe zu https://send.tresorit.com/
2. Upload firebase-credentials.json
3. Ende-zu-Ende verschlüsselt
4. Setze Ablaufdatum
5. Sende Link
```

**WeTransfer Pro (mit Passwort):**
```
1. Upload auf wetransfer.com
2. Aktiviere Passwortschutz
3. Sende Link + Passwort separat
```

---

### 4. Cloud mit Verschlüsselung (GUT) ⭐⭐

**Dropbox mit Cryptomator:**
```bash
# Einmalig: Cryptomator installieren
1. Download Cryptomator (https://cryptomator.org/)
2. Erstelle verschlüsselten Vault in Dropbox
3. Lege firebase-credentials.json in Vault
4. Teile Vault-Passwort mit Entwickler
5. Entwickler installiert Cryptomator + mountet Vault
```

**Google Drive mit Passwort-geschützem ZIP:**
```bash
# Windows: 7-Zip
7z a -p firebase-creds.zip firebase-credentials.json

# Mac: Terminal
zip -e firebase-creds.zip firebase-credentials.json

# Upload zu Google Drive, teile Link
# Passwort separat per SMS/Signal
```

---

### 5. Direct Transfer über sichere Verbindung (OK) ⭐

**Via SSH/SCP:**
```bash
# Empfänger startet SSH Server
# Sender kopiert direkt:
scp firebase-credentials.json user@empfaenger-ip:/path/to/Space-Invaders/

# Oder umgekehrt:
# Empfänger holt Datei:
scp sender@sender-ip:/path/to/firebase-credentials.json .
```

**Via Magic Wormhole (empfohlen!):**
```bash
# Installieren
pip install magic-wormhole

# Sender:
wormhole send firebase-credentials.json
# Gibt Code aus: "7-crossword-something"

# Empfänger:
wormhole receive 7-crossword-something

# Ende-zu-Ende verschlüsselt, kein Server speichert Datei!
```

---

## 🎯 Empfehlung nach Situation

### Für Team-Projekt (mehrere Entwickler):
→ **1Password Shared Vault** oder **Bitwarden Organization**
- Zentrale Verwaltung
- Automatische Updates
- Audit Trail

### Für einzelnen Entwickler:
→ **Bitwarden Send** oder **Magic Wormhole**
- Schnell
- Einmalig
- Automatisches Ablaufdatum

### Für Anfänger (einfach):
→ **7-Zip mit Passwort** + **Google Drive**
- Keine Software-Installation nötig (nur 7-Zip)
- Verständlich
- Ausreichend sicher

### Für Profis:
→ **GPG Verschlüsselung** oder **Magic Wormhole**
- Maximum Security
- Best Practices

---

## 📝 Schritt-für-Schritt: Bitwarden Send (EMPFOHLEN)

```bash
# 1. Sender: Gehe zu https://vault.bitwarden.com/#/send
# 2. Klicke "New Send"
# 3. Wähle "File"
# 4. Uploade firebase-credentials.json
# 5. Einstellungen:
#    - Name: "Space Invaders Firebase Credentials"
#    - Deletion Date: +7 days
#    - Expiration Date: After 1 access
#    - Password: (optional aber empfohlen)
#    - Hide email: Yes
# 6. Klicke "Save"
# 7. Kopiere Link

# 8. Sende Nachricht an Entwickler:
```

**Discord/Slack Message Template:**
```
Hey! Hier sind die Firebase Credentials für Space Invaders:

🔗 Link: [Bitwarden Send Link]
🔒 Passwort: [falls gesetzt, via separatem Kanal]
⏰ Link läuft ab: in 7 Tagen / nach 1 Download

Speichere die Datei als `firebase-credentials.json` im Projekt-Root.
Die Datei ist in .gitignore, wird also nicht committed.

Zum Testen: python test_firebase_top10.py
```

---

## 🚨 Nach dem Teilen

### Checkliste für Empfänger:
```bash
# 1. Datei speichern
cd Space-Invaders
# Speichere als firebase-credentials.json

# 2. Berechtigungen setzen (Linux/Mac)
chmod 600 firebase-credentials.json

# 3. Testen
python test_firebase_top10.py

# 4. Prüfen ob in .gitignore
git status
# firebase-credentials.json sollte NICHT erscheinen!

# 5. Backup erstellen (verschlüsselt)
7z a -p -mhe=on ~/backup-firebase-creds.7z firebase-credentials.json
```

### Checkliste für Sender:
- [ ] Link gesendet
- [ ] Passwort via separatem Kanal gesendet (falls vorhanden)
- [ ] Empfänger bestätigt Erhalt
- [ ] Empfänger kann Firebase erreichen
- [ ] Nach 7 Tagen: Link automatisch ungültig
- [ ] Bei Problemen: Neue Credentials in Firebase Console erstellen

---

## 🔄 Credentials rotieren (alle 6-12 Monate)

```bash
# 1. Firebase Console öffnen
# https://console.firebase.google.com/

# 2. Projekt auswählen
# 3. Settings → Service Accounts
# 4. "Generate new private key"
# 5. Alte Keys löschen (nach Übergangszeit)
# 6. Neue Credentials an alle Team-Mitglieder verteilen
```

---

## 📞 Support

Bei Problemen:
1. Prüfe `.gitignore` enthält `firebase-credentials.json`
2. Prüfe Dateiname ist exakt `firebase-credentials.json`
3. Prüfe JSON Syntax mit: `python -m json.tool firebase-credentials.json`
4. Teste Verbindung: `python test_firebase_top10.py`

**Emergency**: Falls Credentials geleakt → Siehe `CREDENTIALS_SETUP.md` → "Was tun bei Credentials-Leak"

---

**Letzte Aktualisierung:** October 15, 2025
