# Nira – offline Sprachassistent für Raspberry Pi 5

Ein schlankes, lokal laufendes Sprachmodell (TinyLLaMA 1.1 B) auf Basis von llama.cpp, das auf einem Raspberry Pi 5 in Echtzeit antwortet.  
Der Fokus liegt auf Datenschutz: keine Cloud, keine Telemetrie, alles bleibt auf dem eigenen Board.

## Funktionen
- Text- und Sprach-Chat (Deutsch, USB-Mikrofon & Lautsprecher)
- Persistentes Langzeit-Gedächtnis (JSONL)
- Tägliche Backups via Cron
- Modular erweiterbar (Kamera, Servos, ROS 2 …)

## Schnellstart
1. Raspberry Pi OS Lite (64-bit) auf SD-Karte flashen.  
2. Repo klonen und ins Verzeichnis wechseln:  
   ```bash
   git clone https://github.com/KaynDeLunaris/nira.git
   cd nira
3. Einmalig installieren:
./scripts/install.sh
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -P models/
4. Starten:
Nur Text: python3 nira.py
Mit Sprache: python3 nira_voice.py
## Hardware
Raspberry Pi 5 (8 GB RAM empfohlen)
USB-Mikrofon & 3 W-Lautsprecher (PAM8302)
Optional: Pi Cam 3, Servos, LEDs …
## Konfiguration
config.yaml anpassen: Model-Pfad, Temperatur, Backup-Ziel, System-Prompt.
## Backup
Cron-Beispiel für tägliche Sicherung:
(crontab -l 2>/dev/null; echo "0 3 * * * /home/pi/nira/scripts/backup.sh") | crontab -

## Lizenz
Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).