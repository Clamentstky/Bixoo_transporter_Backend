from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
Session = sessionmaker(bind=engine)
db = Session()

trip10 = db.execute(text('SELECT status FROM trips WHERE id=10')).first()
print(f"Trip 10 status is: {trip10[0]}")
