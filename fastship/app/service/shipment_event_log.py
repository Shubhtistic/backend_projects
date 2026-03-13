from app.database.db_models import ShipmentEvent


class ShipmentEventService:
    async def log_event(
        self,
        session,
        shipment_id,
        desc: str | None,
        current_location: str,
        current_location_zip: str,
    ):
        new_event = ShipmentEvent(
            shipment_id=shipment_id,
            description=desc,
            current_location=current_location,
            current_location_zip=current_location_zip,
        )
        session.add(new_event)
        await session.flush()
