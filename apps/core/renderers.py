"""
Custom JSON renderer for Kiwi Trails.
Wraps successful API responses in a standardized success payload.
"""

from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and "response" in renderer_context:
            status_code = renderer_context["response"].status_code
            if status_code >= 400:
                return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and "success" in data:
            return super().render(data, accepted_media_type, renderer_context)

        wrapped_data = {
            "success": True,
            "data": data,
        }
        return super().render(wrapped_data, accepted_media_type, renderer_context)
