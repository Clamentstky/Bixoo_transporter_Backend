from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:Realme30122026@localhost:3306/bixoo_transportation')
Session = sessionmaker(bind=engine)
db = Session()

# Check what trips the user has and manually force them to COMPLETED and add payout
trips = db.execute(text('SELECT id, transporter_id, transport_request_id, trip_code FROM trips WHERE id=10')).fetchall()

for t in trips:
    # Force trip to COMPLETED
    db.execute(text('UPDATE trips SET status="COMPLETED" WHERE id=:id'), {'id': t[0]})
    print(f"Set trip {t[0]} to COMPLETED")

    # Check if wallet transaction exists
    exists = db.execute(text('SELECT id FROM wallet_transactions WHERE trip_id=:trip_id'), {'trip_id': t[0]}).first()
    if not exists:
        req = db.execute(text('SELECT offered_amount FROM transport_requests WHERE id=:req_id'), {'req_id': t[2]}).first()
        if req and req[0]:
            import uuid
            amount = req[0]
            ref = f"TRIP-PAY-{str(uuid.uuid4())[:8].upper()}"
            desc = f"Trip payout for {t[3] or 'TRIP-'+str(t[0])}"
            db.execute(text('''
                INSERT INTO wallet_transactions 
                (transporter_id, trip_id, transaction_type, amount, reference_number, status, description) 
                VALUES (:tid, :trip_id, 'CREDIT', :amount, :ref, 'COMPLETED', :desc)
            '''), {'tid': t[1], 'trip_id': t[0], 'amount': amount, 'ref': ref, 'desc': desc})
            print(f"Added payout of {amount} for trip {t[0]}")

db.commit()
print("Done processing payouts")
