#!/bin/bash
BACKUP_DIR="/home/pi/nira_backups"
mkdir -p
BACKUP
D
​
IRcpmemory.jsonl"
BACKUP_DIR/memory_$(date +%F_%H-%M-%S).jsonl"
Optional: rsync zu externem NAS
rsync -avz $BACKUP_DIR user@nas:/backups/nira/
chmod +x scripts/backup.sh
Cron-Eintrag: 0 3 * * * /home/pi/nira-starter/scripts/backup.sh