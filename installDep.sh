python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app chess_app run --debug