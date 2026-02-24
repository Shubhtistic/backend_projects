from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    DELIVERY_PARTNER = "delivery_partner"
    ADMIN = "admin"


class ShipmentStatus(str, Enum):  # using str, enum makes it behave like enum
    Pending = "Pending"
    InTransit = "InTransit"
    Delivered = "Delivered"
