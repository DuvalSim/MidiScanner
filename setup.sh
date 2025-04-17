python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo apt-get install python3-tk
# on wsl:
export QT_QPA_PLATFORM="xcb"
sudo apt install libxcb-xinerama0 libqt5x11extras5
