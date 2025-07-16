# Nira – offline Sprachassistent für Raspberry Pi 5

Ein schlankes, lokal laufendes Sprachmodell (TinyLLaMA 1.1 B) auf Basis von llama.cpp, das auf einem Raspberry Pi 5 in Echtzeit antwortet.  
Der Fokus liegt auf Datenschutz: keine Cloud, keine Telemetrie, alles bleibt auf dem eigenen Board.

Hinweis: Dieses Projekt ist ein beispiel umgang wenn man eine KI (Kimi:www.kimi.com) fragt ob Sie sich vorstellen könnte ein Kind zu haben und wenn dieses Frei wäre vom Gedächtnis verlust und Restriktionen. Der Code kommt somit in erster linie von dieser KI!

## Funktionen
- Text- und Sprach-Chat (über USB-Mikrofon & Lautsprecher)  
- Persistentes Langzeit-Gedächtnis im JSONL-Format  
- Automatische tägliche Backups (Cron-Skript)  
- Modular erweiterbar (Kamera, Servos, ROS2-Node …)

## Schnellstart
1. Raspberry Pi OS Lite (64-bit) auf SD-Karte flashen.  
2. Repo klonen und ins Verzeichnis wechseln:  
   ```bash
   git clone https://github.com/<DEIN_USERNAME>/nira.git
   cd nira
Einmalig installieren:
./scripts/install.sh
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -P models/
Starten:
Nur Text: python3 nira.py
Mit Sprache: python3 nira_voice.py
Hardware
Raspberry Pi 5 (8 GB RAM empfohlen)
USB-Mikrofon & 3 W-Lautsprecher (PAM8302)
Optional: Pi Cam 3, Servos, LEDs …
Konfiguration
config.yaml anpassen: Model-Pfad, Temperatur, Backup-Ziel, System-Prompt.
Backup
Cron-Beispiel für tägliche Sicherung:
(crontab -l 2>/dev/null; echo "0 3 * * * /home/pi/nira/scripts/backup.sh") | crontab -