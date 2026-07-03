#!/bin/bash
set -e

python -m venv venv

if [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install -r requirements.txt

python seed.py

echo "Setup complete. Run 'python app.py' to start the server."
