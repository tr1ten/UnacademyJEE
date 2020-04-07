import requests
from bs4 import BeautifulSoup
from pprint import pprint
from functools import reduce
import json
import re
import os
import time
import gdownloader
import argparse

#  For calculating time
def timeme(fn):
	def dfn(*args):
		start = time.time()
		r_value = fn(*args)
		if arguments.verbose:
			print('[#] Total time taken by {} : {:.2f}s'.format(fn.__name__,time.time()-start))
		return r_value
	return dfn

class Unacdemy(object):
	"""Simple Unacdemy Notes Downloading Utility"""

	def __init__(self):
		#  initializing instance variables
		self.classes = [['s2','s21','s23','s30','s24 softmerge','s22 softmerge','s18','s19','s15','s19 softmerge','s10','s10 softmerge','s25'],['s7','s0','s17']]
		self.pattern = re.compile(r'd\/(.*?)\/view')
		self.url = '''https://docs.google.com/spreadsheets/d/e/2PACX-1vQUwyeyCbReMBmABf-Q-XqG40oB5KrDQoUlLMpDZhBu18YasgWI72pAyH4beYolw95ylxQJdPqSWcig/pubhtml'''

	#  Collecting data
	@timeme
	def run(self):
		self.soup = self.getSoup(self.url)
		#  Checking for cache
		if os.path.isfile('db.json'):
			with  open('db.json','r') as f:
				self.db = json.load(f)
		else:
			#  requesting and storing in json file
			self.fetch_links(self.getSoup(self.url),self.classes)
			self.tojson(self.db)


	#  Return Soup Object
	@timeme
	def getSoup(self,url):
		self.r = requests.get(url)
		return BeautifulSoup(self.r.content,'html.parser')

	#  Scraping links with Chapter names
	def fetch_links(self,soup,classes):
		''' Messy code / Worst way to do this'''
		self.db = {'physics':{},'chemistry':{},'maths':{}}
		for elements in soup.find_all('tr'):
			temp_ch = elements.find('td',class_=classes[0])
			temp_link = elements.find('td',class_=classes[1])

			if temp_ch:
				chapter = temp_ch.get_text()
				self.db[subject][chapter] = []

			if temp_link and temp_link.get_text().lower().count('physics'):
				subject = 'physics'
			if temp_link and temp_link.get_text().lower().count('chemistry'):
				subject = 'chemistry'
			if temp_link and temp_link.get_text().lower().count('maths'):
				subject = 'maths'

			try :
				if temp_link:
					self.db[subject][chapter].append(temp_link.find('a').get('href'))
			except :
				pass
		#  list comprehension for printing total Chapters/Notes for different subject
		# print([{(key,len(value.keys())):reduce(lambda acc,nk:acc+len(self.db[key][nk]),value.keys(),0)} for key,value in self.db.items()])

	#  Cacheing

	def  tojson(self,db):
		with open('db.json','w') as f:
			json.dump(db,f,ensure_ascii=False,indent=4)

	#  to unshorten the url
	@timeme
	def _unshorten(self,url):
		soup = self.getSoup(url)
		ulink = soup.find('a').get_text() #  scraping bitly url
		return requests.head(ulink, allow_redirects=True).url #  returns shared link of file in google drive

	#  Fetching id of gdrive link
	@timeme
	def fetch_id(self,url):
		return self.pattern.findall(self._unshorten(url))[0]

	#  Downloading content using id
	@timeme
	def download_content(self,subject,chapter,path,verbose=False):
		apath = os.path.join(path,chapter)
		if not os.path.isdir(apath):
			os.mkdir(apath)
		else:
			pass
			print('[!] Folder already exist')
			user = input('continue ? (y/n)..')
			if user == 'y':
				apath = os.path.join(path,input('enter new name for folder :'))
				os.mkdir(apath)
			else:
				exit(0)
		for index,links in enumerate(self.db[subject][chapter]):
			ids = self.fetch_id(links)
			f_path = os.path.join(apath,f'{chapter} L{index+1}.pdf')

			print('[.] Downloading Lecture-',index+1)
			gdownloader.downloadfile(ids,f_path)
		print('Downloaded {} Notes in {}!'.format(chapter,apath))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Unacdemy JEE Notes Downloader tool coded by Tr1ten',usage='python3 main.py -s SUBJECT -c "CHAPTER" "CHAPTER2"..',epilog='note : chapter name is case sensitive so spell it correctly (check db for correct chapter names) and it should be in qoutes.')
	group = parser.add_mutually_exclusive_group()
	parser.add_argument('-s','--subject',help='Subject of Notes (case sensitive) eg.maths',type=str,choices=['physics','chemistry','maths'])
	parser.add_argument('-c','--chapter',nargs='*',help='Chapter Name (case sensitive) eg.Application of derivative')
	parser.add_argument('-d','--dir',type=str,help='Specify directory to store notes',default=os.path.dirname(os.path.abspath(__file__)))
	group.add_argument('-v','--verbose',action="store_true",default=False,help='display details')
	group.add_argument('-p','--show',action="store_true",default=False,help='display available chapter')

	arguments = parser.parse_args()
	if not arguments.show and not (arguments.subject and  arguments.chapter):
		parser.print_help()
		exit(0)
	print('this may take some time....')
	obj = Unacdemy()
	obj.run()
	if arguments.show:
		print('Available Chapters notes to download -:')
		for subjects in obj.db.keys():
			print(f'{subjects} >>')
			for chapters in obj.db[subjects].keys():
				print(f'\t {chapters}')
		exit(0)

	if all(x in obj.db[arguments.subject].keys() for x in arguments.chapter):
		print('> Started Downloading Notes...')
		for chapters in arguments.chapter:
			print(f'>Downloading {chapters} Notes..')
			obj.download_content(arguments.subject,chapters,arguments.dir,arguments.verbose)
		else:
			print('Thanks for using this tool <3')
	else:
		print('~Chapter not found , maybe you mispelled or forget the qoutes')
		print('use "python main.py --show" to view available chapter names')
