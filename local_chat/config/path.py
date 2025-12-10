from pathlib import Path

ASSETS_DIR      =   Path('assets')
DATA_DIR        =   Path('data')
DATABASE_DIR    =   DATA_DIR / 'database.json'
SOUND_DIR       =   ASSETS_DIR / 'sound'
FONT_DIR        =   ASSETS_DIR / 'font'

DEFAULT_DATABASE_STRUCTURE = {
  "users": [],
  "conversations": []
}
