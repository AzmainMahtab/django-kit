"""Shared JSON renderer."""

from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """Standardizes the top-level JSON envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        success = response is not None and 200 <= response.status_code < 300

        if data is not None and isinstance(data, dict) and ("results" in data or "detail" in data):
            envelope = {"success": success, "data": data}
        else:
            envelope = {"success": success, "data": data}

        return super().render(envelope, accepted_media_type, renderer_context)
