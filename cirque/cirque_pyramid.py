from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from hendrix.deploy import HendrixDeploy



def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')
    app = config.make_wsgi_app()


class PyramidDeploy(HendrixDeploy):
  application = app

deploy = PyramidDeploy()
deploy.start()
