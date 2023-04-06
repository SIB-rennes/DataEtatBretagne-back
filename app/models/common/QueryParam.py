from flask_restx.reqparse import RequestParser


class QueryParam():
    """
       Represents a query parameter object used to extract and store query parameters from a Flask request.

       Attributes:
           query_search (str or None): The search query string.
           page_number (int or None): The page number to retrieve.
           limit (int or None): The maximum number of results to retrieve.
    """

    def __init__(self, request_parser: RequestParser):
        """
            Initializes a new instance of the QueryParam class.

            Args:
                request_parser (RequestParser): The Flask RequestParser object used to parse the request arguments.
        """
        p_args = request_parser.parse_args()

        self.query_search = p_args.get("query") if p_args.get("query") is not None else None
        self.page_number = p_args.get("pageNumber")
        self.limit = p_args.get("limit")


    def get_search_like_param(self):
        """
            Returns a SQL LIKE expression for searching the query_search parameter in a database.

            Returns:
                A string representing a SQL LIKE expression, or None if the query_search parameter is not set.
        """
        return f'%{self.query_search}%' if self.query_search is not None else None


    def is_query_search(self) -> bool:
        """
        Determines if the query_search parameter is set.
        Returns:
            True if the query_search parameter is set, False otherwise.
        """
        return self.query_search is not None
