from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.modules.transporter.chats.models as chat_models

engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
Session = sessionmaker(bind=engine)
db = Session()

msg = chat_models.ChatMessage(
    trip_id=11,
    sender_id=3,
    sender_type="TRANSPORTER",
    message="test message"
)
db.add(msg)
db.commit()
print("Success!")
