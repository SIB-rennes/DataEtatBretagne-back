from dataclasses import dataclass

from ..utils import _InstrumentForFlaskRestx

from app.clients.data_subventions.models import Subvention, RepresentantLegal

@dataclass
class InfoApiSubvention(metaclass=_InstrumentForFlaskRestx):
    """Informations qui proviennent de l'API subvention"""

    subventions: list[Subvention]
    contacts: list[RepresentantLegal]
