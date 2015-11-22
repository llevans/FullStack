#
# file: webserver.py
# author: lyn.evans
# date: 09.07.15
#
import cgi
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Era, Composer
from sqlalchemy.orm import relationship
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

engine = create_engine('postgresql://vagrant:vagrant@localhost:5432/vagrant')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
  """ Initial python webserver class to learn CRUD """

    def do_GET(self):
        try:
            if self.path.endswith("/edit"):
                composer_id = self.path.split("/")[2]
                composer = session.query(Composer).filter_by(id = composer_id).first()
                eras  = session.query(Era).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>%s</h1>" % composer.name
                output += '''<form method='POST' enctype='multipart/form-data' action='/update'>'''
                output += '''<div>Name:&nbsp;<input name="composer_name" type="text" value="%s" size="30"></div>''' % composer.name
                output += '''<div>Description:&nbsp;<textarea name="description" type="text" rows="4" cols=32>%s''' % composer.description
                output += "</textarea>"
                output += "<input type='hidden' name='id' value='%s'>" % composer_id
                output += '''<div>Era:&nbsp;<select name="composer_era">'''
                for era in eras:
                  if composer.era.id == era.id:
                      output += "<option value=%s  selected>%s</option>" % (era.id, era.name)
                  else:
                      output += "<option value=%s>%s</option>" % (era.id, era.name)

                output += "</select></div><br>"
                output += '''<input type="submit" value="Update"></div>'''
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
               composer_id = self.path.split("/")[2]
               composer = session.query(Composer).filter_by(id = composer_id).first()
               session.delete(composer)
               session.commit()

               self.send_response(301)
               self.send_header('Location', '/composers')
               self.end_headers()

            if self.path.endswith("/composers"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"

                composers = session.query(Composer).order_by(Composer.name).all()
                for composer in composers:
                    output += "<h3>" + composer.name + "</h3>"
                    output += "<div><a href='/composers/%s/edit'>Edit</a></div>" % composer.id
                    output += "<div><a href='/composers/%s/delete'>Delete</a></div>" % composer.id
                    
                #output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                eras = session.query(Era).all()
                output = ""
                output += "<html><body>"
                output += "<h1>Add a Composer</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/create'>'''
                output += '''<div>Name:&nbsp;<input name="composer_name" type="text" ></div>'''
                output += '''<div>Description:&nbsp;<input name="description" type="text" ><input type="submit" value="Create"></div>'''
                output += '''<div>Era:&nbsp;<select name="composer_era">'''
                for era in eras:
                  output += "<option value=" + str(era.id) + ">" + era.name + "</option>"
                output += "</select></div>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                c_name  = fields.get('composer_name')
                c_era   = fields.get('composer_era')
                c_descr = fields.get('description')

            if self.path.endswith("/new"):
               era = session.query(Era).filter_by(id=c_era[0]).first()
               comp = Composer(name = c_name[0], description = c_descr[0], era = era)
               session.add(comp)
               session.commit()

            if self.path.endswith("/update"):
               c_id = fields.get('id')
               era = session.query(Era).filter_by(id=c_era[0]).first()
               composer = session.query(Composer).filter_by(id=c_id[0]).one()
               composer.name = c_name[0]
               composer.description = c_descr[0] 
               composer.era = era
               session.add(composer)
               session.flush()

            self.send_response(301)
            self.send_header('Location', '/composers')
            self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
