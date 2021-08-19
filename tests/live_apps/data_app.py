import json

from werkzeug.wrappers import Request, Response


@Request.application
def app(request):
    return Response(
        json.dumps(
            {
                "environ": request.environ,
                "form": request.form,
                "files":
                {k: v.read().decode("utf8")
                 for k, v in request.files.items()},
            },
            default=lambda x: str(x),
        ),
        content_type="application/json",
    )
