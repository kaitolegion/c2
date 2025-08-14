#!/bin/bash
#####################################
#  Installation of C2               #
#  Coded by Kaito Coding            #
#  Team: Purexploit                 #
#####################################
set -e
# Color codes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
RED="\033[1;31m"
RESET="\033[0m"

# Detect if running on Termux
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
    # Termux environment
    INSTALL_DIR="$HOME/.local/share/c2"
    BIN_LINK="$PREFIX/bin/c2"
    SUDO=""
    PYTHON=python
else
# Running on standard Linux
    INSTALL_DIR="/usr/local/share/c2"
    BIN_LINK="/usr/local/bin/c2"
    SUDO=sudo
    PYTHON=python3
fi

echo -e "${BLUE}[*] Installing to ${INSTALL_DIR}...${RESET}"

$SUDO mkdir -p "$INSTALL_DIR"
$SUDO cp -r assets "$INSTALL_DIR/"
$SUDO cp -r clients "$INSTALL_DIR/"
$SUDO cp -r scripts "$INSTALL_DIR/"
$SUDO cp main.py "$INSTALL_DIR/"
$SUDO chmod +x "$INSTALL_DIR/main.py"
# $SUDO chmod 666 "$INSTALL_DIR/session.json"

# Create launcher script
LAUNCHER="#!/bin/bash
cd \"$INSTALL_DIR\"
$PYTHON main.py \"\$@\"
"

if [ -e "$BIN_LINK" ]; then
    echo -e "[!] A file already exists at $BIN_LINK.${RESET}"
    read -p "$(echo -e "${YELLOW}[?] Do you want to overwrite it? [y/N]: ${RESET}")" yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
        $SUDO rm -f "$BIN_LINK"
        echo "$LAUNCHER" | $SUDO tee "$BIN_LINK" > /dev/null
        $SUDO chmod +x "$BIN_LINK"
        echo -e "${GREEN}[+] Replaced $BIN_LINK with new launcher script.${RESET}"
    else
        echo -e "${RED}[-] Keeping existing $BIN_LINK. Installation cancelled.${RESET}"
        exit 1
    fi
else
    echo "$LAUNCHER" | $SUDO tee "$BIN_LINK" > /dev/null
    $SUDO chmod +x "$BIN_LINK"
fi

echo -e "${GREEN}[+] Installation complete!${RESET} You can now run '${BLUE}c2${RESET}' from anywhere."