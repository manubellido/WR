# -*- coding: utf-8 -*-

from circuits import settings
from circuits.forms import CircuitForm


def circuit_creation_form(request):
    circuit_form = CircuitForm(auto_id=False)
    return {
        'CIRCUIT_CREATION_FORM': circuit_form,
        'CIRCUIT_COLUMN_SIZES': settings.CIRCUIT_COLUMN_SIZES,
        'CIRCUIT_STOP_COLUMN_SIZES': settings.CIRCUIT_STOP_COLUMN_SIZES,
    }
