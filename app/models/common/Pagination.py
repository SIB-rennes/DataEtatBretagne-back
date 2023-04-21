import dataclasses

from app.models.utils import _InstrumentForFlaskRestx


@dataclasses.dataclass
class Pagination(metaclass=_InstrumentForFlaskRestx):
    totalRows: int
    page: int
    pageSize:int

    def to_json(self):
        """Returns a JSON  representation of the pagination object.

        Returns:
            dict: The dictionary representation of the pagination object.
        """
        return {
            'totalRows': self.totalRows,
            'page': self.page,
            'pageSize': self.pageSize
        }