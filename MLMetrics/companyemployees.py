# This Python file uses the following encoding: utf-8
import os, sys
# So... I already got the names of all the committers
# Next, find out if they work in that company
	# If they currently do, then flag that person as a 2
	# If they used to but currently don't, then flag him/her as a 1
	# If they haven't worked there at all, then flag him/her as a 0
# Tally up all the 2s, 1s, and 0s and print them out

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True
firefox_capabilities['binary'] = '/usr/bin/firefox'
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from datetime import datetime, time
from pattern.web import *
from pattern.web import URL, extension, download
from sets import Set
import json
import re

PATHtoLinkedInJSONs = "/home/anne/github-research/company-affiliation/resources/linkedin_info/"
DEBUG = True
pending = []

"""
Takes in all the results of the json file and returns the info we really need in a tuple
returns: (date list, sha list, name list)
Keep in mind the names aren't in their final, simplified form. There are duplicates in this names list.
"""
def obtainDatesShasNames(filename):
	commits = json.load(open(filename, 'r'))
	shas = []
	names = []
	dates = []
	companies = []
	for c in commits:
		#TODO:
		#store dates in dates
		dates.append(c["commit"]["author"]["date"].encode("utf-8"))
		#store sha in shas
		commiturl = c["commit"]["url"]
		commiturl_list = commiturl.split("/")
		shas.append(commiturl_list[-1].encode("utf-8"))
		#store name in names
		names.append(c["commit"]["author"]["name"])
		pass
	filterLists(dates, shas, names)
	return (dates, shas, names)

"""
Gets one of each name and stores the results into a list
"""
def simplifyNameList(comprehensiveNameList):
	newNameSet = Set()
	for name in comprehensiveNameList:
		newNameSet.add(name)
	return list(newNameSet)
"""
Gets the number of commits this person has for this particular project
"""
def findNumCommits(name, companyfile):
	numcommits = 0
	(dates, shas, names) = obtainDatesShasNames(companyfile)
	for currentname in names:
		if name == currentname:
			numcommits += 1
	return numcommits

"""
eliminate Jenkins, OpenStack Proposal Bot, and Openstack Jenkins
"""
def filterLists(dates, shas, names):
	for i in range(len(names) - 1, -1, -1):
		n = names[i]
		if (n == 'OpenStack Proposal Bot') or (n == 'Jenkins') or (n == 'OpenStack Jenkins'):
			index_location = names.index(n)
			del names[index_location]
			del shas[index_location]
			del dates[index_location]

# Find this person's work history if it's saved. If not, save it to a file called "pending"
def findHistory(name):
	global pending
	personalHistory = []
	readablename = name.split(" ")
	# print readablename
	try:
		fileOpener = ""
		if len(readablename) == 3:
			fileOpener += PATHtoLinkedInJSONs+'{}{}{}_linkedin.json'.format(readablename[0], readablename[1], readablename[2])
		elif len(readablename) == 2:
			fileOpener += PATHtoLinkedInJSONs+'{}{}_linkedin.json'.format(readablename[0], readablename[1])
		elif len(readablename) == 1:
			fileOpener += PATHtoLinkedInJSONs+'{}_linkedin.json'.format(readablename[0])
		with open(fileOpener) as data_file:
			data = json.load(data_file)
			if len(data) == 0: #if we don't have data on this person
				pending.append(name)
			else:
				for line in data:
					personalHistory.append(line)
	except IOError, Argument:
		pending.append(name)
		# print "this person's file doesn't exist yet", Argument
	except UnicodeEncodeError, Argument:
		pending.append(name)
		# print "we can't decode this name", Argument
	return personalHistory

"""
Helper function: get the people with 3+ commits for this company
"""
def frequentcommitters(companyfile):
	(dates, shas, names) = obtainDatesShasNames(companyfile)
	uniquenames = simplifyNameList(names)
	frequentcommitters = []
	# print "the committers:"
	print "going through {}'s committers. progress: \n".format(companyfile)
	for name_index in range(len(uniquenames)):
		name = uniquenames[name_index]
		print name_index + 1, "out of ", len(uniquenames), " total committers"
		if (findNumCommits(name, companyfile) > 2):
			frequentcommitters.append(name)
	return frequentcommitters

#Emergency linkedin processing. if we ever need this method again
def getLinkedInInfo(name, url):
	driver = webdriver.Firefox(capabilities=firefox_capabilities)
	if DEBUG:
		print driver
	driver.get(url)
	time.sleep(2)
	title = driver.title
	orgs_worklife = driver.find_elements_by_class_name("item-subtitle")
	dateranges = driver.find_elements_by_class_name("date-range")
	orgsAndCompanies = []
	for i in range(len(dateranges)):
		try:
			daterange = dateranges[i]
			one_daterange = daterange.text.encode('ascii', 'ignore').decode('ascii')
			# print i
			one_org = orgs_worklife[i].text.encode('ascii', 'ignore').decode('ascii')
			# print one_org
			orgsAndCompanies.append((one_org, one_daterange))
		except IndexError as e:
			break
	driver.quit()
	time.sleep(2)
	readablename = name.encode("utf-8").split(" ")
	if (len(readablename) == 1):
		f = open(PATHtoLinkedInJSONs + '{}_linkedin.json'.format(readablename[0]), 'w')
	if (len(readablename) == 2):
		f = open(PATHtoLinkedInJSONs + '{}{}_linkedin.json'.format(readablename[0], readablename[1]), 'w')
	if (len(readablename) == 3):
		f = open(PATHtoLinkedInJSONs + '{}{}{}_linkedin.json'.format(readablename[0], readablename[1], readablename[2]), 'w')
	json.dump(orgsAndCompanies, f)
	f.close()
	return name + str(orgsAndCompanies)

#Given company & work history, look for the word "Tensorflow", or "Google" for the tensorflow project
#Look for "CNTK" or "Microsoft" for the CNTK project
def findNumEmployees(project, committers):
	numEmployees = 0
	company = ""
	if (project == "/home/anne/ResearchJSONs/tensorflow-tensorflow-commits.json"):
		company += "Google"
	elif (project == "/home/anne/ResearchJSONs/CNTK-Microsoft-commits.json"):
		company += "Microsoft"
	elif (project == "/home/anne/ResearchJSONs/deeplearning4j-deeplearning4j-commits.json"):
		company += "Skymind"
	elif (project == "/home/anne/ResearchJSONs/Theano-Theano-commits.json"):
		company += "Montr"
	elif (project == "/home/anne/ResearchJSONs/caffe-BVLC-commits.json"):
		company += "Berkeley"

	#looping through frequentcommitters to see if this person has worked at the company
	for name_index in range(len(committers)):
		name = committers[name_index] 
		# print name
		print name_index, " out of ", len(committers), "frequent committers"
		try:
			personalHistory = findHistory(name) #pulls up the personal work history of this person
			for alist_index in range(len(personalHistory)):
				currentCompany = personalHistory[alist_index] #a list in the form of [company, dates]
				if (company in currentCompany[0]):
					# print " worked at Montreal"
					numEmployees += 1
					alist_index += 1
		except IOError, Argument:
			pending.append(name)
			# print "this person's file doesn't exist yet", Argument
		except UnicodeEncodeError, Argument:
			pending.append(name)
			# print "we can't decode this name", Argument
	return numEmployees

if __name__ == '__main__':
	# frequentcommitterslist = frequentcommitters(companyfile)
	# theanocommitterprofiles = {u'Alexandre de Brebisson': "https://ca.linkedin.com/in/adbrebs/en", u'Bryn Keller': "https://www.linkedin.com/in/bryn-keller-bb77493", u'Yann N. Dauphin': "https://www.linkedin.com/in/yann-n-dauphin-5267a58", u'Razvan Pascanu': "https://uk.linkedin.com/in/razvan-pascanu-67abb215", u'Sander Dieleman': "https://uk.linkedin.com/in/sanderdieleman", u'Roy Xue': "https://www.linkedin.com/in/royxue", u'Xavier Bouthillier': "https://ca.linkedin.com/in/bouthilx", u'James Bergstra': "https://ca.linkedin.com/in/james-bergstra-64a7b15", u'medakk': "https://in.linkedin.com/in/karthik-karanth", u'Gokula Krishnan': "https://ch.linkedin.com/in/sgokula"}
	# for name in theanocommitterprofiles:
	# 	print name
	# 	getLinkedInInfo(name, theanocommitterprofiles[name])

	companyfile = "/home/anne/ResearchJSONs/" + "deeplearning4j-deeplearning4j-commits.json" # + "filename"
	committers = frequentcommitters(companyfile)
	print "deeplearning4j, Skymind: ", findNumEmployees(companyfile, committers)
	print "list of people who still need linkedins: \n", pending
	print "# of people I can't get linkedins for: \n ", len(pending)
	# print "Number of people who still need linkedin profiles: ", len(pending)
