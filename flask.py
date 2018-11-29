#!/usr/bin/env python
import requests
import json
import base64
from oauth2client.client import GoogleCredentials
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2


from http.server import BaseHTTPRequestHandler, HTTPServer

credentials = GoogleCredentials.get_application_default()

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def get_prediction(self, content, project_id, model_id):
        
        prediction_client = automl_v1beta1.PredictionServiceClient()
        name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
        payload = {'image': {'image_bytes': content }}
        params = {}
        request = prediction_client.predict(name, payload, params)
        return request  # waits till request is returned

    def get_webcams(self):
        print("fetching webcams")

        response = requests.get("https://webcamstravel.p.mashape.com/webcams/list/nearby=36.0063,-5.6026,20?lang=en&show=webcams%3Aimage%2Clocation",
		  headers={
		    "X-Mashape-Key": "eZ2vSr20A7mshAoxov8PDGhXvx6gp16y70xjsnGfgKDofQQQ8a",
		    "X-Mashape-Host": "webcamstravel.p.mashape.com"}).content.decode('utf-8')
        return json.loads(response)
        
  # GET
    def do_GET(self):
        camlist = []
        for webcam in self.get_webcams()["result"]["webcams"]:
            camlist.append((webcam["title"], webcam["image"]["current"]["preview"]))
       
        url = camlist[0][1]
        project = "dev-dpfeller"
        model = "ICN1520060372971093389"
        scores = []
        labels = []
        urls = []
        predictlist = []
        for cam in camlist: 	
            instance = requests.get(cam[1]).content
            #instance = {'key': '0', 'image_bytes': {'b64': base64.b64encode(requests.get(cam[1]).content)}}   
            prediction = self.get_prediction(instance, project,  model)
            score = prediction["predictions"][0]["scores"]
            description = ""
            if(float(score[0]) >= float(score[1])):
                description = "no wind :("
            else:
                description = "GO KITE!!!1!"
            predictlist.append((cam[0], cam[1],prediction["predictions"][0]["scores"], prediction["predictions"][0]["labels"], description ))
            
        template_values = {
            'predictlist': predictlist,
            }

	
        
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return
        
def run():
    print('starting server...')
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()


run()