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
	def _unshorten(self,url):
		soup = self.getSoup(url)
		ulink = soup.find('a').get_text() #  scraping bitly url
		return requests.head(ulink, allow_redirects=True).url #  returns shared link of file in google drive 
	
	#  Fetching id of gdrive link
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
			if verbose:
				print('[.] Downloading Lecture-',index+1)
			gdownloader.downloadfile(ids,f_path)
			if verbose:
				print('[+]Notes Saved to ',f_path)
		print('Downloaded {} Notes in {}!'.format(chapter,apath))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Unacdemy JEE Notes Downloader Utility coded by Tri10',usage='python3 main.py -s SUBJECT -c "CHAPTER"')
	group = parser.add_mutually_exclusive_group()
	parser.add_argument('-s','--subject',required=True,help='Subject of Notes (case sensitive) eg.maths',type=str,choices=['physics','chemistry','maths'])
	parser.add_argument('-c','--chapter',type=str,required=True,help='Chapter Name (case sensitive) eg.Application of derivative')
	parser.add_argument('-d','--dir',type=str,help='Specify directory to store notes',default=os.path.dirname(os.path.abspath(__file__)))
	group.add_argument('-v','--verbose',action="store_true",default=False)
	args = parser.parse_args()
	obj = Unacdemy()
	obj.run()
	if args.chapter in obj.db[args.subject].keys():
		print('> Started Downloading Notes...')
		obj.download_content(args.subject,args.chapter,args.dir,args.verbose)
	else:
		print('~Chapter not found , maybe you mispelled ')
		for chapters in obj.db[args.subject].keys():
			if chapters.lower().count(args.chapter):
				print('[?] Do yo mean "{}" '.format(chapters))
				break
		else:
			print('[*] try finding chapter name in db.json file')


	
	