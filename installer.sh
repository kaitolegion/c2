#!/bin/bash
set -e

INSTALL_DIR="/usr/local/share/c2"
BIN_LINK="/usr/local/bin/c2"
echo "Installing $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r assets "$INSTALL_DIR/"
sudo cp -r clients "$INSTALL_DIR/"
sudo cp -r scripts "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/assets/c2.py"
sudo ln -sf "$INSTALL_DIR/assets/c2.py" "$BIN_LINK"
sudo chmod +x "$BIN_LINK"

echo "Installation complete! You can now run 'c2' from anywhere."