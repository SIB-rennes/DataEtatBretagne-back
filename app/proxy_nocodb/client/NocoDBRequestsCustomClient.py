from nocodb.infra.requests_client import NocoDBRequestsClient
from nocodb.nocodb import NocoDBProject, WhereFilter
from typing import Optional

from nocodb.utils import get_query_params


class NocoDBRequestsCustomClient(NocoDBRequestsClient):
    def table_export_csv(
            self,
            project: NocoDBProject,
            table: str,
            filter_obj: Optional[WhereFilter] = None,
            params: Optional[dict] = None,
    ) -> dict:

        response = self._NocoDBRequestsClient__session.get(
            f"{self._NocoDBRequestsClient__api_info.get_table_uri(project, table)}/export/csv",
            params=get_query_params(filter_obj, params),
        )
        return response
