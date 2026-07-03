# B207 Final Assessment - Password Manager

This is a simple password manager web app made with Flask for my B207 final assessment. You can register an account, log in, and store your website passwords safely. The passwords are encrypted before they go into the database.

## Requirements

- Python 3 (I used 3.11 while making this, but anything recent should work)
- pip

## How to run it

Just run the setup script, it does everything for you:

```bash
bash setup.sh
```

This will:
1. Create a virtual environment (`venv` folder)
2. Install everything from `requirements.txt`
3. Run `seed.py` which creates the database and adds a demo user

The venv gets activated inside the script, but that doesn't carry over to your terminal once it finishes, so activate it again before starting the app:

```bash
source venv/bin/activate      # on Mac/Linux
venv\Scripts\activate         # on Windows
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

If `bash setup.sh` doesn't work for some reason (e.g. on Windows without git bash), you can do it manually:

```bash
python -m venv venv
venv\Scripts\activate      # on Windows
source venv/bin/activate   # on Mac/Linux
pip install -r requirements.txt
python seed.py
python app.py
```

## Demo account

The seed script creates a demo account so you don't have to register first:

- username: `demo`
- password: `DemoPass123!`

It also comes with one example password entry already saved (for "Example Site").

## Features

- Register / login with hashed passwords (bcrypt)
- Each user's vault passwords are encrypted with a key derived from their own master password (PBKDF2), so even I can't see them in the database
- Add, view, edit and delete saved passwords
- Random password generator
- CSRF protection on forms

## Notes

- The database file (`instance/vault.db`) is not included in git, it gets created when you run the setup/seed script.
- If you re-run `seed.py` it won't duplicate the demo user, it just skips seeding if it already exists.
