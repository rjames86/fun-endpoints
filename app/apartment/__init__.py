from flask import Blueprint
from ..lib.decorators import gen_route_decorator
from app.models.models import ApartmentUnits, Permission

apartment = Blueprint('apartment', __name__)
route = gen_route_decorator(apartment)

from . import views


@apartment.app_context_processor
def inject_apartments():
    return dict(
        ApartmentUnits=ApartmentUnits,
        Permission=Permission
    )
