import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # print(f'{request.body=}')
        # print(f'{request.headers=}')
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each response after the view is called
        #
        # print(f'{response.content=}')

        return response
