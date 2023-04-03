from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import memcache

varlist = ['TimeStamp','ElapsedTime',
           'LaserTSetpoint','LaserTAct','GasTemp', 'GasPress',
           'AmbientTemp', 'AmbientHumidity','AmbientPressure',
           'Methane','Ringdown','intensity', 'baseline','Water', 'FlowRate',
           'GPSTime','Latitude','Longitude','Speed']

namelist = ["Time", "Elapsed Time [s]",
            "Laser Setpoint [V]", "Actual Laser T [V]", "Gas Temp. [C]", "Gas Press. [hPa]",
            "Amb. Temp. [C]", "Amb. Humidity [%]", "Amb. Press. [hPa]",
            "CH4 Conc. [ppb]", "Ringdown Time [us]", "Intensity [mV]", "Baseline [mV]",
            "Water Conc. [ppm]", "Flow Rate [SLPM]",
            "GPS Time", "Latitude", "Longitude", "Speed"]


shared = memcache.Client(['127.0.0.1:11211'], debug=0)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        data = shared.get_multi(varlist)
        self.wfile.write(json.dumps(data, default=str))

def run(server_class=HTTPServer, handler_class=Handler, port=8008):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()


shared = memcache.Client(['127.0.0.1:11211'], debug=0)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        data = shared.get_multi(varlist)
        self.wfile.write(json.dumps(data))

def run(server_class=HTTPServer, handler_class=Handler, port=8008):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
