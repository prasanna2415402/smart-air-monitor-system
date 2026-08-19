from rest_framework.response import Response


def success_response(data=None, message="Success", status=200, **extra):
    """Uniform success envelope: { success, message, data, ...extra }."""
    payload = {"success": True, "message": message, "data": data}
    payload.update(extra)
    return Response(payload, status=status)


def error_response(message="Request failed", errors=None, status=400):
    return Response({"success": False, "message": message, "errors": errors}, status=status)
