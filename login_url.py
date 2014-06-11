#!/usr/bin/python3
# 
# Simple script that automatic login to (in this case dyndns).
# Lazy way to make host-update.. Run as cronjob.
# <michael.lofvenberg@cvoid.se>
#
import urllib.parse
import urllib.request
import http.cookiejar
import logging
import os
import sys
import re
import time
import datetime
import ssl

# Logging setup
instPath =  os.getcwd()
# Ugly fix for crontab, /root/ is cwd when running from cron...
logging.basicConfig(filename=instPath + '/script/dyndns/login_url.log',level=logging.DEBUG)

class urlChecker:
	"""
	Dyndns parser class, automatic update dyndns with help from cron.
	"""
	def __init__(self, urlInp='https://account.dyn.com/entrance/', myID="", myPass=""):
		self.urlInp = urlInp
		self.user_agent ='Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/0.0.0 (KHTML, like Gecko) Version/0.0.0 Safari/0.0.0'
		self.headers = {'User-Agent' : self.user_agent}
		self.myID = myID
		self.myPass = myPass
		self.form = {'username' : self.myID, 'password' : self.myPass, 'iov_id'   : '', 'multiform' : ''}

	def printHttp(self):
		"""
		Print output to screen, debugging..
		"""
		# Content of webpage
		print(self.response.info())
		# Human readable
		print(self.response.read().decode('utf-8'))

	def logHttp(self, headData, info, headers='no'):
		"""
		Log information.
		"""
		today = str(datetime.datetime.now().replace(microsecond=0))
		logging.info(today + " \nLog info from " + self.urlInp)
		if headers == 'yes':
			logging.info(info)
			logging.info(headData)
			logging.info("********************************************")
			return
		logging.info(info)
		logging.info("********************************************")

	def makeReq(self, url):
		"""
		Method that builds an object for handling https cookie post
		"""
		self.urlInp = url
		# We handle cookies
		self.cookieJ = http.cookiejar.CookieJar()
		
		# We must create a custom handler if we are using https..
		preForm = re.findall(re.compile(r'https'), self.urlInp)
		if preForm[0] == 'https':
			preForm[0] = 'https'
		else:
			preForm[0] = 'http'
		
        # We build our handler and opener, cookie and https..
		self.logHttp('',"Building handler and opener for %s" % self.urlInp)
		if preForm[0] == 'https':
			handler = urllib.request.HTTPSHandler(debuglevel=0)
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookieJ), handler)
		else:
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookieJ))
		
		# Make this as a default, install opener..
		urllib.request.install_opener(opener)
		
		# Make our first request
		self.request = urllib.request.Request(self.urlInp)
		self.response = opener.open(self.request)
		content = self.response.read().decode('utf-8')
		self.logHttp('', "Cookie values: %s" % self.cookieJ._cookies)
		# Get multiform value for this session
		if len(self.form) > 3:
			multiReg = re.compile(r"multiform\'\s+value=\'(\w+)\'")
			multiForm = re.findall(multiReg, content)
			self.form['multiform'] = str(multiForm[0])
			self.logHttp('', "Multiform value = %s" % self.form['multiform'])
		
		# We update payload
		self.data = urllib.parse.urlencode(self.form)
		self.data = self.data.encode('utf-8')
		
		# We try to log in with method POST..
		self.headers['Content-type'] = 'application/x-www-form-urlencoded'
		self.request = urllib.request.Request(self.urlInp, self.data, self.headers)
		self.resonse = opener.open(self.request)
		#self.response = urllib.request.urlopen(self.request)
		
		# Alternative way of handling cookie from response
		#self.headers['Cookie'] = [i[1] for i in self.response.getheaders() if i[0]=="Set-Cookie"]	
		
		# We haved login, hopefully.. try to get a url check for pattern (username).
		self.headers['Content-type'] = 'text/html'
		self.urlInp = 'https://account.dyn.com/'
		self.request = urllib.request.Request(self.urlInp, data=None, headers=self.headers)
		self.response = opener.open(self.request)
		
		# For debugging, handle output..
		self.logHttp(self.response.info(), "GET headers response from %s" % self.urlInp, headers='yes')
		self.loginCheck(self.myID)
		
	def loginCheck(self, userPatt):
		"""
		Method that check for a pattern that hopfully matches your username.
		This is specific for dyndns.
		"""
		matchPatt = re.findall(re.compile(userPatt), self.response.read().decode('utf-8'))
		if matchPatt:
			self.logHttp('', "Login Success: Found match for username %s" % userPatt)
		else:
			self.logHttp('', "Login Failure: Could not get match for username %s" % userPatt)

	def logOut(self, logOut):
		"""
		We make a friendly logout
		"""
		# Make some sleeptime
		time.sleep(3)
		# We log out clean from site..
		self.urlInp = logOut
		self.request = urllib.request.Request(self.urlInp, self.data, self.headers)
		self.resonse =  urllib.request.urlopen(self.request)
		self.logHttp(self.response.info(), "Headers: Logout from site %s" % self.urlInp, headers='yes')


# ************************************* MAIN ******************************************
mReq = urlChecker('https://account.dyn.com/entrance/', 'USERNAME', 'PASSWORD')
mReq.makeReq('https://account.dyn.com/entrance/')
mReq.logOut('https://account.dyn.com/entrance/?__logout=1')
