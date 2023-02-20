from flask_restx import reqparse

def get_origin_referrer(request):
    # This function returns the origin of the request if it is present
    # and it is not "localhost", otherwise it returns the referrer
    if request.origin is not None and "localhost" not in request.origin:
        return request.origin
    else:
        return request.host



def get_pagination_parser(default_page_number = 1, default_limit = 100):
    """Returns a request parser for pagination parameters.

       Args:
           default_page_number (int, optional): The default page number. Defaults to 1.
           default_limit (int, optional): The default page size. Defaults to 100.

       Returns:
           RequestParser: The pagination request parser.
    """
    pagination_parser = reqparse.RequestParser()
    pagination_parser.add_argument("pageNumber", type=int, required=True, default=default_page_number, help="Page number of the results.")
    pagination_parser.add_argument("limit", type=int, required=True, default=default_limit, help="Number of results per page.")
    return  pagination_parser