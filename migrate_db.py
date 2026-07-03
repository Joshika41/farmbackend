from database import engine
from models import Base

print("Creating new tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
