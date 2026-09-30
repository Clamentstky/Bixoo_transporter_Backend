from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app  # Register all models before creating the test schema.
from app.db.base import Base
from app.modules.auth.models import User
from app.modules.transporter.dashboard.router import get_dashboard
from app.modules.transporter.loads.models import TransportRequest
from app.modules.transporter.settlements.models import Settlement
from app.modules.transporter.trips.models import Trip


def test_dashboard_counts_all_active_trips_and_scopes_settlements_to_user():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(name="Owner", email="owner@example.com", mobile="9000000001", password_hash="unused")
        other = User(name="Other", email="other@example.com", mobile="9000000002", password_hash="unused")
        db.add_all([owner, other])
        db.flush()
        assert get_dashboard(owner, db).data["stats"]["active_trips"] == 0

        yesterday = datetime.now() - timedelta(days=1)
        statuses = ["ACCEPTED", "IN_TRANSIT", "COMPLETED", "COMPLETED", "CANCELLED"]
        trips = []
        for index, status in enumerate([*statuses, "IN_TRANSIT"]):
            request = TransportRequest(
                request_code=f"LOAD-{index}", source_type="TEST",
                pickup_address="Pickup", pickup_city="Chennai", pickup_state="Tamil Nadu",
                delivery_address="Delivery", delivery_city="Salem", delivery_state="Tamil Nadu",
                goods_name="Goods", quantity=1, quantity_unit="unit", weight=1, weight_unit="ton",
                required_vehicle_type="Truck", pickup_date=yesterday, required_delivery_date=yesterday,
                offered_amount=1000,
            )
            trip = Trip(
                trip_code=f"TRIP-{index}", request=request,
                transporter_id=owner.id if index < len(statuses) else other.id,
                status=status, completed_at=yesterday if status == "COMPLETED" else None,
            )
            db.add(trip)
            trips.append(trip)
        db.flush()
        for trip, status, amount in [(trips[2], "PENDING", 1000), (trips[3], "PROCESSING", 2000),
                                     (trips[4], "SETTLED", 4000), (trips[5], "PENDING", 8000)]:
            db.add(Settlement(trip_id=trip.id, transporter_id=trip.transporter_id,
                              trip_amount=amount, net_amount=amount, status=status))
        db.commit()

        dashboard = get_dashboard(owner, db).data
        assert dashboard["stats"]["active_trips"] == 2
        assert dashboard["stats"]["total_completed"] == 2
        assert dashboard["stats"]["today_completed"] == 0
        assert dashboard["stats"]["pending_settlement"] == Decimal("3000")
        assert dashboard["active_trip"]["internal_id"] in [trip.id for trip in trips[:2]]
    engine.dispose()
