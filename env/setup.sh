#!/data/data/com.termux/files/usr/bin/bash
pkg update && pkg upgrade -y
pkg install python git tree -y
pip install -r ~/sonoluminescence/env/requirements.txt
echo "✅ Environment ready"
