from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ici, on utilise SQLite, la base sera créée automatiquement si elle n'existe pas
engine = create_engine('sqlite:///bot.db', echo=True)
Session = sessionmaker(bind=engine)
