from rest_framework.response import Response

def success_response(message="Success", data=None, status_code=200):
    return Response(
        {
            "isSuccess": True,
            "message": message,
            "statusCode": status_code,
            "data": data,
        },
        status=status_code,
    )


def error_response(message="Error", status_code=400, errors=None):
    return Response(
        {
            "isSuccess": False,
            "message": message,
            "statusCode": status_code,
            "errors": errors,
        },
        status=status_code,
    )
