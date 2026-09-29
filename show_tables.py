from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
with engine.connect() as con:
    tables = con.execute(text('SHOW TABLES')).fetchall()
    for t in tables:
        print(t[0])
