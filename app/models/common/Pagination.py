class Pagination:
    def __init__(self, total_rows: int, page: int, page_size: int):
        """Initializes a pagination instance.

        Args:
            total_rows (int): The total number of rows.
            page (int): The current page number.
            page_size (int): The number of rows per page.
        """
        self.total_rows = total_rows
        self.page = page
        self.page_size = page_size

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