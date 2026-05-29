class MediaBypassWhiteNoise:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/media/"):
            from django.views.static import serve
            from django.conf import settings

            path = request.path.replace("/media/", "")
            return serve(request, path, document_root=settings.MEDIA_ROOT)

        return self.get_response(request)