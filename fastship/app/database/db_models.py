from sqlmodel import SQLModel,Field
from datetime import datetime
from uuid import uuid4, UUID

class Shipment(SQLModel,table=True):
    __tablename__="shipment"


    id:UUID=Field(default_factory=uuid4)
    content:str=Field(max_length=50)
    weight:float
    destination:int
    estimated_delivery:datetime
