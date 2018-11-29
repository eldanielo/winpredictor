from bs4 import BeautifulSoup
import urllib                                       
import base64
from googleapiclient import discovery
import json
from oauth2client.client import GoogleCredentials
import re
import sys
import requests
import webapp2
from google.appengine.api import urlfetch
import jinja2
import os
import json
from pprint import pprint
from rapidconnect import RapidConnect

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

credentials = GoogleCredentials.get_application_default()
ml_service = discovery.build('ml', 'v1', credentials=credentials)




class MainPage(webapp2.RequestHandler):

	def get_prediction(self, instance, project, model, version):
		name = 'projects/{}/models/{}'.format(project, model)
		if version:
			name += '/versions/{}'.format(version)
			request_dict = {'instances': [instance]}
			request = ml_service.projects().predict(name=name, body=request_dict)
			return request.execute()  # waits till request is returned

	def get_webcams(self):
		print("fetching webcams")
		response = urlfetch.fetch("https://webcamstravel.p.mashape.com/webcams/list/nearby=36.0063,-5.6026,20?lang=en&show=webcams%3Aimage%2Clocation",
		  headers={
		    "X-Mashape-Key": "eZ2vSr20A7mshAoxov8PDGhXvx6gp16y70xjsnGfgKDofQQQ8a",
		    "X-Mashape-Host": "webcamstravel.p.mashape.com"}).content
		return json.loads(response)



	def get(self):

		camlist = []
		for webcam in self.get_webcams()["result"]["webcams"]:
			camlist.append((webcam["title"], webcam["image"]["current"]["preview"]))

		print(camlist)

		url = camlist[0][1]
		project = "dev-dpfeller"
		model = "windpredict2"
		version = "windpredict2_201806190808_base"
		scores = []
		labels = []
		urls = []
		predictlist = []
		for cam in camlist: 	
			instance = {'key': '0', 'image_bytes': {'b64': base64.b64encode(urlfetch.fetch(cam[1]).content)}}
			prediction = self.get_prediction(instance, project,  model, version)
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

		

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))
app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
