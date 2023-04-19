from enum import Enum


class AllowedCountries(str, Enum):
    UK = 'UK'
    FRANCE = 'FRANCE'
    GERMANY = 'GERMANY'


class OrderStatus(str, Enum):
    REQUESTING = 'REQUESTING'
    ACCEPTED = 'ACCEPTED'
    IN_PROGRESS = 'IN_PROGRESS'
    DISPATCHED = 'DISPATCHED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
