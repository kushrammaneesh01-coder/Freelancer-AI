<<<<<<< HEAD
﻿# Database package initialization
=======
from backend.db.session import engine
from backend.models import Base

Base.metadata.create_all(bind=engine)
print("✅ Database tables created")
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
