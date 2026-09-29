from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
Session = sessionmaker(bind=engine)
db = Session()

db.execute(text('UPDATE transport_requests SET status="PENDING"'))
db.execute(text('UPDATE transport_matches SET status="PENDING"'))
db.commit()
print('Reset all loads to PENDING')
