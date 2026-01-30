from django.http import HttpRequest, JsonResponse
from django.views import View
from django.db import connection


class HealthView(View):
    """
    Health check endpoint.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """Check application health."""
        health = {
            "status": "healthy",
            "version": "1.0.0",
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health["database"] = "connected"
        except Exception as e:
            health["database"] = f"error: {str(e)}"
            health["status"] = "degraded"

        status_code = 200 if health["status"] == "healthy" else 503

        return JsonResponse(health, status=status_code)
