#!/bin/bash
set -e
sudo apt update
sudo apt install -y python3-pip git espeak-ng ffmpeg portaudio19-dev
pip3 install -r requirements.txt
mkdir -p models scripts
echo "✓ Alles installiert. Leg die .gguf-Datei in models/ und starte mit python3 nira.py"
chmod +x scripts/install.sh
