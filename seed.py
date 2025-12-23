from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from models.base import Base
from data.user_data import user_list
from data.venue_data import venue_list
from config.environment import db_URI

engine = create_engine(db_URI)
SessionLocal = sessionmaker(bind=engine)

try:
    print("Recreating database...")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Seeding database...")
    db: Session = SessionLocal()

    db.add_all(user_list)
    db.commit()

    db.add_all(venue_list)
    db.commit()

    db.close()
    print("Database seeding complete 👋")

except Exception as e:
    print("An error occurred:", e)
