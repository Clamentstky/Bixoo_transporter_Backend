from sqlalchemy import create_engine
from app.db.base import Base
import app.modules.auth.models
import app.modules.transporter.trips.models
import app.modules.transporter.chats.models

engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
Base.metadata.create_all(bind=engine)
print("Chat table created!")
