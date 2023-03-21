import dataclasses

from app.models.utils import _AddMarshmallowAndJsonSchema


@dataclasses.dataclass
class Pagination(metaclass=_AddMarshmallowAndJsonSchema):
    total_rows: int
    page: int
    page_size:int

    def to_json(self):
        """Returns a JSON  representation of the pagination object.

        Returns:
            dict: The dictionary representation of the pagination object.
        """
        return {
            'totalRows': self.total_rows,
            'page': self.page,
            'pageSize': self.page_size
        }