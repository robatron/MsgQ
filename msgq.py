#!/usr/bin/env python

from threading import Event

# ---------------
# The MsgQ class
# ---------------
class MsgQ:
	'''	MsgQ (short for "Message Queue") is a simple queue that allows one to 
	push/pop messages on/off of a queue, with an optional blocking mechanism, 
	i.e., if you call a pop on an empty queue, you can have it wait until a new
	message arrives.
	
	Example usage:
	==============
	>>> from msgq import *		# import MsgQ module
	>>> mq = MsgQ()				# create a new message queue
	>>> mq.push('q', 'a')		# push messages onto queue 'q'
	>>> mq.push('q', 'b')
	>>> mq.push('q', 'c')
	>>> mq.push('q2', 'A')		# push messages onto queue 'q2'
	>>> mq.push('q2', 'B')
	>>> mq.getMessages('q')		# return the message list of q
	['a', 'b', 'c']
	>>> mq.getMessages('q2')	# return the message list of q2
	['A', 'B']
	>>> mq.pop('q')				# pop messages off of q
	'a'
	>>> mq.getMessages('q')
	['b', 'c']
	>>> mq.pop('q')
	'b'
	>>> mq.pop('q')
	'c'
	>>> mq.pop('q')				# attempt to pop empty q, receive exception
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "msgq.py", line 94, in pop
		raise messageListEmpty
	msgq.messageListEmpty
	
	Note that if a value is provided for the 'wait' parameter for pop, it will
	block the current thread until a message appears on the queue.
	
	By Rob McGuire-Dale, November 2010
	Licensed under the GPLv2 (http://www.gnu.org/licenses/gpl-2.0.html)
	'''
	
	# -----------
	# Class data
	# -----------
	__Qs = None			# a dictionary of all the queues
	__debugMode = None	# if debug messages are to be reported or not
	
	# -----
	# init
	# -----
	def __init__(self, debug=False):
		self.__debugMode = debug
		self.__debug("MsgQ initializing...")
		self.__debug("Debug mode ENABLED.")
		self.__Qs = {}

	
	# -------------------
	# Queue manipulation
	# -------------------		
	def push(self, q, msg):
		''' Push a new message onto the specified queue. If the queue does not
		yet exist, create it.
		'''
		self.__debug("Attempting to push message '%s' to queue '%s'"%(msg,q))
		if not q in self.__Qs: # create queue if it doesn't exist
			self.__debug("Uh oh. Queue '%s' doesn't exist."%q)
			self.resetQueue(q)
		self.__Qs[q].messages.append(msg)
		self.__announcePush(q)
		self.__debug("Queue '%s' now looks like: %s"%(q,self.__Qs[q].messages))

	def pop(self, q, wait=None):
		''' Pop a message from the front of the specified queue. If the
		specified queue doesn't exist, it will raise a queueDoesNotExist
		exception. If the message list is empty, it will raise a
		messageListEmpty exception.
		
		Optionally, you can specify an amount of time, in milliseconds, to wait 
		for for the queue to have a message pushed into it. If in that time a 
		message is pushed, it will return with the message immediatly. During 
		this time MsgQ will block the thread. If a message does not arrive 
		within that time, it will raise a timeOut exception.
		
		If you specify '-1' for the wait time, it will wait indefinitly.
		'''
		def waitAndTryAgain():
			self.__debug("Being patient and waiting.")
			self.__waitForAnnouncement(q, float(wait)/1000)
			self.__debug("Either got a signal to coninue, or I'm board with "\
					+"waiting.")
			try:
				self.__debug("Attempting to pop one last time.")
				return self.__Qs[q].messages.pop(0)
			except IndexError:
				self.__debug("The queue is still empty. Raising exception.")
				raise timeOut("Timeout! I'm not waiting anymore.")
			
		try:
			self.__debug("Attempting to pop a message off of queue '%s'"%q)
			msg = self.__Qs[q].messages.pop(0)
			self.__debug("Returning message '%s'"%msg)
			self.__debug("Queue '%s' now looks like: %s"%\
					(q,self.__Qs[q].messages))
			return msg
		except KeyError:
			self.__debug("Uh oh. Queue '%s' does not exist."%q)
			if wait:
				self.resetQueue(q)
				return waitAndTryAgain()
			else:
				self.__debug("Raising queue does not exist exception.")
				raise queueDoesNotExist
		except IndexError:
			self.__debug("Uh oh. Queue '%s' has no messages."%q)
			if wait:
				return waitAndTryAgain()
			else:
				self.__debug("Raising message-list-empty exception.")
				raise messageListEmpty

	def getQueues(self):
		''' Return all the queues '''
		return self.__Qs
			
	def getMessages(self, q):
		''' Return all of the messages in the specified queue. If the queue does
		not exist, it will raise a queueDoesNotExist exception.
		'''
		try:
			return self.__Qs[q].messages
		except KeyError:
			raise queueDoesNotExist

	def clearEmpty(self):
		''' Deletes all of the empty queues, return the number it deleted. If
		you're using this in a loop based off of the queue size, use queue.keys
		to avoid getting a runtime error for changing the queue size in a loop.
		'''
		nrDeleted = 0
		try:				
			for k in self.__Qs.keys():
				if len(self.__Qs[k].messages) == 0:
					del self.__Qs[k]
					nrDeleted += 1
		except KeyError:
			raise QueueDoesNotExist("Queue not found")
		return nrDeleted
	
	def resetQueue(self, q):
		''' Resets the specified queue. If it doesn't exist, it creates a new 
		one.
		'''
		self.__debug("Resetting queue '%s'"%q)
		self.__Qs[q] = Queue()
		
	# --------------------------
	# Thread blocking/signaling
	# --------------------------
	def __announcePush(self, q):
		''' Announces that the queue is executing a push command. This
		announcement will notify any waiting __waitForAnnouncement()s'''
		try:
			self.__debug("Announcing a push event to the queue.")
			self.__Qs[q].event.set()
		except KeyError:
			raise queueDoesNotExist("Attempted to write to a queue that "\
					+"doesn't exist yet.")
		self.__Qs[q].event.clear()
		
	def __waitForAnnouncement(self, q, timeout):
		''' Pauses thread excecution until either a push event announcement
		happens, or it times out. A negative timeout will cause it to wait
		indefinitly.
		'''
		self.__debug("Waiting for a push announcement...")
		if timeout < 0:
			self.__debug("I'll never get bored. I'm waiting forever.")
			self.__Qs[q].event.wait()
		else:
			self.__debug("I'm only waiting for %d milliseconds."%timeout)
			self.__Qs[q].event.wait(timeout)
		self.__Qs[q].event.clear()
		
	# --------
	# Helpers
	# --------
	def __debug(self, msg):
		''' For reporting debug messages in a standard way '''
		if self.__debugMode:
			print "MSGQ DEBUG: %s"%msg

# ---------------
# Helper classes 
# ---------------
class Queue():
	''' A simple queue object that holds a list of its messages and an Event 
	object for pop thread blocking and push signaling.
	'''
	event = None
	messages = None
	def __init__(self):
		self.event = Event()	# for the blocking mechanism
		self.messages = []		# the list of messages in the queue
	
# -----------
# Exceptions
# -----------
class queueDoesNotExist(Exception):
	''' Exception for a non-existant queue '''
	def __init__(self, value="The specified queue does not exist"):
		self.value=value

class messageListEmpty(Exception):
	''' Exception for a queue with an empty message list '''
	def __init__(self, value="The specified message list is empty"):
		self.value=value
		
class timeOut(Exception):
	''' Exception for when something has waited too long '''
	def __init__(self, value="Timeout."):
		self.value=value
