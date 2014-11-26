# -*- codeing: utf-8 -*-
def wsgi_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!']


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 9999

    # from web.wsgiserver import CherryPyWSGIServer
    # server = CherryPyWSGIServer(('0.0.0.0', port), wsgi_app)
    # print 'wsgi server start to listen on port %s...' % port
    # server.start()
    from simple_server import make_server
    server = make_server('0.0.0.0', port, wsgi_app)
    print 'wsgi server start to listen on port %s...' % port
    server.serve_forever()
