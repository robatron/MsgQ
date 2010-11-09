#!/usr/bin/env python

from os import path
import cherrypy
from msgq import *

'''
This is an HTTP interface for MsgQ. Run this as a stand-alone Python program,
and it will be accessable at http://localhost:8080. See the README file for more
details.

By Rob McGuire-Dale, November 2010
Licensed under the GPLv2 (http://www.gnu.org/licenses/gpl-2.0.html)
'''

# --------
# M A I N
# --------
def main():
	''' Configure and run the CherryPy server '''
	
	# configure the static files/directories
	demoPath = path.join(path.dirname(path.abspath(__file__)), "demo")
	conf = {
		'/demo': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': demoPath,
			'tools.staticfile.on': True,
			'tools.staticfile.filename': path.join(demoPath, "index.html") 
		}
	}
	
	# start the CherryPy server with the MsgQ doc root map
	cherrypy.quickstart(msgq_serv(), config=conf)

# -------------
# MsgQ doc map
# -------------
class msgq_serv(object):
	''' Document map that CherryPy will mount when started '''
	
	# -----
	# init
	# -----
	__Qs = None # the message queue
	def __init__(self):
		self.__Qs = MsgQ(debug=True)
	
	# ------
	# index
	# ------
	@cherrypy.expose
	def index(self):
		''' default to the demo if no commands are supplied '''
		raise cherrypy.HTTPRedirect("/demo")
	
	# ---------------
	# push/pop stuff
	# ---------------
	@cherrypy.expose
	def push(self, queue=None, msg=None):
		'''
		Pushes a new message onto the specified queue. If successful, a '0' will
		be returned. If unsuccessful, an error message will be returned.
		'''
		if queue == None or msg == None:
			return "Fail! Queue and msg must both be defined."
		self.__Qs.push(queue, msg)
		return '0'
		
	@cherrypy.expose
	def pop(self, queue=None, wait=None):
		'''
		Returns the message at the front of the specified queue. If the queue is
		empty, it will return "{{empty queue}}". 
		
		Optionally, you can specify an amount of time, in milliseconds, to wait 
		for for the queue to have a message pushed into it. If in that time a 
		message is pushed, it will return with the message immediatly. While 
		it's waiting, the server will appear to clients as "busy." If you 
		specify '-1' for the wait time, it will wait indefinitly.
		
		If the specified queue does not exist, it will return 
		"{{queue does not exist}}".
		'''
		try:
			self.__debug("Attempting to pop a message off of queue '%s'"%queue)
			return self.__Qs.pop(queue, wait)
		except (messageListEmpty, queueDoesNotExist):
			return "{{empty queue}}"
		except timeOut:
			return "{{timed out}}"

	def __debug(self, msg):
		print "MSGQ SERVER DEBUG: %s"%msg

# -----------
# start prog
# -----------
if __name__ == "__main__":
	main()
