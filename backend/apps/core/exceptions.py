import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler so every error response (validation,
    auth, permission, not-found, throttling, or unhandled server errors) uses
    one consistent JSON envelope:

        {
            "success": false,
            "message": "...",
            "errors": {...} | [...] | null
        }
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception -> don't leak internals, but do log them.
        logger.exception("Unhandled exception in %s", context.get("view"))
        return Response(
            {
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
                "errors": None,
            },
            status=500,
        )

    message = "Request failed."
    errors = response.data

    if isinstance(exc, drf_exceptions.ValidationError):
        message = "Validation failed."
    elif isinstance(exc, (drf_exceptions.AuthenticationFailed, drf_exceptions.NotAuthenticated)):
        message = "Authentication failed. Please log in again."
    elif isinstance(exc, (drf_exceptions.PermissionDenied, PermissionDenied)):
        message = "You do not have permission to perform this action."
    elif isinstance(exc, (drf_exceptions.NotFound, Http404)):
        message = "The requested resource was not found."
    elif isinstance(exc, drf_exceptions.Throttled):
        message = "Too many requests. Please slow down and try again shortly."
    elif isinstance(response.data, dict) and "detail" in response.data:
        message = str(response.data["detail"])

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return response
