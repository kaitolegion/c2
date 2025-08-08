#!/bin/bash
set -e

# Color codes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
RED="\033[1;31m"
RESET="\033[0m"

INSTALL_DIR="/usr/local/share/c2"
BIN_LINK="/usr/local/bin/c2"

echo -e "${BLUE}[*] Installing to ${INSTALL_DIR}...${RESET}"

sudo mkdir -p "$INSTALL_DIR"
sudo cp -r assets "$INSTALL_DIR/"
sudo cp -r clients "$INSTALL_DIR/"
sudo cp -r scripts "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/assets/c2.py"

# Create launcher script
LAUNCHER="#!/bin/bash
cd /usr/local/share/c2
exec python3 ./assets/c2.py \"\$@\"
"

if [ -e "$BIN_LINK" ]; then
    echo -e "[!] A file already exists at $BIN_LINK.${RESET}"
    read -p "$(echo -e "${YELLOW}[?] Do you want to overwrite it? [y/N]: ${RESET}")" yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
        sudo rm -f "$BIN_LINK"
        echo "$LAUNCHER" | sudo tee "$BIN_LINK" > /dev/null
        sudo chmod +x "$BIN_LINK"
        echo -e "${GREEN}[+] Replaced $BIN_LINK with new launcher script.${RESET}"
    else
        echo -e "${RED}[-] Keeping existing $BIN_LINK. Installation cancelled.${RESET}"
        exit 1
    fi
else
    echo "$LAUNCHER" | sudo tee "$BIN_LINK" > /dev/null
    sudo chmod +x "$BIN_LINK"
fi

echo -e "${GREEN}[+] Installation complete!${RESET} You can now run '${BLUE}c2${RESET}' from anywhere."