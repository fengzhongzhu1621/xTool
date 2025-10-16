from drf_yasg.inspectors import SwaggerAutoSchema


class BkResourceSwaggerAutoSchema(SwaggerAutoSchema):
    def should_page(self):
        if "enable_paginator" not in self.overrides.keys():
            return super().should_page()
        return self.overrides["enable_paginator"]
