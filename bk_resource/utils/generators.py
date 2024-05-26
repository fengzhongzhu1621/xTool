from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class BKResourceOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_path_item(self, path, view_cls, operations):
        """Get a :class:`.PathItem` object that describes the parameters and operations related to a single path in the
        API.

        :param str path: the path
        :param type view_cls: the view that was bound to this path in urlpatterns
        :param dict[str,openapi.Operation] operations: operations defined on this path, keyed by lowercase HTTP method
        :rtype: openapi.PathItem
        """
        path_parameters = self.get_path_parameters(path, view_cls)

        # 移除get参数中与path_parameters重复的项
        if operations.get("get"):
            paths_params = [param["name"] for param in path_parameters]
            query_params = []
            for path_param in operations["get"]["parameters"]:
                if path_param.name not in paths_params:
                    query_params.append(path_param)
            operations["get"]["parameters"] = query_params
        return openapi.PathItem(parameters=path_parameters, **operations)
