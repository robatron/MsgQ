#!/usr/bin/env python

import sys
import random
import string
from thread import start_new_thread
from msgq import *

'''
Tests for for the MsgQ class. 

By Rob McGuire-Dale, November 2010
Licensed under the GPLv2 (http://www.gnu.org/licenses/gpl-2.0.html)
'''

# -------------------
# main test function
# -------------------
def main():
	''' Runs all tests '''
	mq = MsgQ()
	pushTest(mq)
	popTest(mq)
	waitTest(mq)
	
# -----------
# MsgQ tests
# -----------
def pushTest(mq):
	'''
	Test push functionality by creating five queues, and randomly placing 20 
	random messages of lengh up-to 2 into these queues.
	'''
	declare("Testing basic push functionality")
	print "Creating 5 queue names of length up to 2..."
	QList = []
	for i in range(5):
		QList.append(genString(2))
	print "Placing 20 random messages randomly amongst the queues..." 
	for i in range(20):
		q = random.choice(QList)
		m = genString(3)
		print"Pushing '%s' onto queue '%s'"%(m,q)
		mq.push(q,m)
		status(mq)

def popTest(mq):
	'''
	Test pop functionality by poping off every message in every queue in the 
	message queue. It will also clear empty queues.
	'''
	declare("Testing basic pop functionality")
	Qs = mq.getQueues()
	print("MsgQ status:")
	for q in Qs.keys():
		nrMsgs = len(Qs[q].messages)
		print "There are %d messages in queue '%s'"%(nrMsgs,q)
		for i in range(nrMsgs):
			print "Popping message '%s' off of queue '%s'"%(mq.pop(q),q)
			status(mq)
		try:
			mq.pop(q)
		except messageListEmpty:
			print "Empty message list exception caught successfully"
		print "Cleared %s empty queues"%mq.clearEmpty()
		try:
			mq.pop(q)
		except queueDoesNotExist:
			print "Non-existant-queue exception caught successfully"

def waitTest(mq):
	'''
	Test the blocking capabilities of pop.
	'''
	declare("Testing blocking capabilities")
	print "Calling pop with a wait time of 1000 ms..."
	try:
		mq.pop("foo", wait=1000);
	except timeOut:
		print "Successfully caught a time-out exception."
	
	print "Forking a new thread and having a pop wait inside for 5 seconds..."
	def tempPrint():
		print mq.pop("foo", wait=5000)
	start_new_thread(tempPrint, ())
	print "Pushing onto the waiting queue in the other thread"
	mq.push("foo", "If you're seeing this message, we're cool.")
	
# --------
# helpers
# --------
def declare(s):
	'''
	Output the specified string between two rows of '=' characters.
	'''
	for i in range(len(s)+2):
		sys.stdout.write('=')
		if i >= len(s)+1:
			print
	print " " + s + " "
	for i in range(len(s)+2):
		sys.stdout.write('=')
		if i >= len(s)+1:
			print
	
def genString(maxLen=10, alphabet=string.letters+string.digits):
	'''
	Generate a random string containing characters from the specified alphabet,
	with a maximum lenght of maxLen.
	'''
	maxLen += 2
	if maxLen < 3:
		maxLen = 3
	s = ""
	for i in range(1,random.choice(range(2,maxLen))):
		s += random.choice(alphabet)
	return s
		
def status(mq):
	'''
	Prints out all of queues and their messages in the message queue.
	'''
	Qs = mq.getQueues()
	print("MsgQ status:")
	for q in Qs.keys():
		print("	Queue '%s': %s"%(q,Qs[q].messages))

# -----------
# start prog
# -----------
if __name__ == "__main__":
	main()
