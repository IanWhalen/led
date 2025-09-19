#!/bin/bash
UNAME=$(uname -s)

if [ "$UNAME" = "Linux" ]
then
    echo "Installing venv on Linux"
    sudo apt-get install -y python3-venv
    sudo apt-get install -y swig liblgpio-dev
fi
if [ "$UNAME" = "Darwin" ]
then
    echo "Installing venv on Darwin"
    brew install python3-venv
fi
mkdir dist
python3 -m pip install --upgrade --force-reinstall adafruit-blinka Adafruit-PlatformDetect
python3 -m venv .venv && . .venv/bin/activate && pip3 install -r requirements.txt && python3 -m PyInstaller --onefile --hidden-import="googleapiclient" --path="/home/weatherbox/led-animate-module/src" src/main.py
tar -czvf dist/archive.tar.gz dist/main
