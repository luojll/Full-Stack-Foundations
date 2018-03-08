import cgi

from http.server import BaseHTTPRequestHandler, HTTPServer
from models import Base, Restaurant
from sqlalchemy import create_engine

engine = create_engine('sqlite:///restaurant.db')

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parameters = self.path.strip('/').split('/')
        if len(parameters) == 2 and parameters[0] == 'delete':
            isDeleted = Restaurant.delete(parameters[1])
            output = ""
            output += "<html><body>"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if isDeleted:
                output += "<h1>Delete Successfully</h1>"
            else:
                output += "<h1>Fail to delete</h1>"
            output += "<body></html>"
            self.wfile.write(bytes(output, 'utf-8'))
            return
        elif len(parameters) == 2 and parameters[0] == 'rename':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1> Change the restaurant name!</h1>"
            output += '''<form method='POST' enctype='multipart/form-data' action='/rename/%s'><h2>Name: </h2><input name="name" type="text" ><input type="submit" value="Submit"> </form>''' % parameters[1]
            output += "</body></html>"
            self.wfile.write(bytes(output, 'utf-8'))
            return
        elif self.path.endswith("/all"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            restaurants = Restaurant.query_all()
            output = ""
            output += "<html><body>"
            output += "<h1>All Restaurants: </h1>"
            output += "<ul>"
            for r in restaurants:
                output += "<li>%s, " % r.name
                output += "<a href=\"/delete/%s\">Delete</a>" % str(r.id)
                output += ", "
                output += "<a href=\"/rename/%s\">Edit</a>" % str(r.id)
                output += "</li>"
            output += "</ul>"
            output += "</body></html>"
            self.wfile.write(bytes(output, 'utf-8'))
            return
        elif self.path.endswith("/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1> Please enter the new restaurant name!</h1>"
            output += '''<form method='POST' enctype='multipart/form-data' action='/new'><h2>Name: </h2><input name="name" type="text" ><input type="submit" value="Submit"> </form>'''
            output += "</body></html>"
            self.wfile.write(bytes(output, 'utf-8'))
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        parameters = self.path.strip('/').split('/')
        if len(parameters) == 2 and parameters[0] == 'rename':
            ctype, pdict = cgi.parse_header(
                self.headers.get('Content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8') # ???
            restaurant_name = None
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict) # How does this work?
                new_name = fields.get('name')[0].decode('utf-8')
            Restaurant.rename(parameters[1], new_name)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Rename Successfully</h1>"
            output += "</body></html>"
            self.wfile.write(bytes(output, 'utf-8'))
        if self.path.endswith("/new"):
            ctype, pdict = cgi.parse_header(
                self.headers.get('Content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8') # ???
            restaurant_name = None
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict) # How does this work?
                restaurant_name = fields.get('name')[0].decode('utf-8')
            try:
                Restaurant.insert(restaurant_name)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += " <h2> Insert Successfully, Name: %s </h2>" % restaurant_name
                output += "</body></html>"
                self.wfile.write(bytes(output, 'utf-8'))
            except ValueError:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += " <h2> Failed to Insert, Name: %s </h2>" % restaurant_name
                output += "</body></html>"
                self.wfile.write(bytes(output, 'utf-8'))

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
