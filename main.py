import requests 
from bs4 import BeautifulSoup
from pprint import pprint
from functools import reduce
import json
import re
import os
import time
import gdownloader
class Unacdemy(object):
	"""Simple Unacdemy Notes Downloading Utility"""

	def __init__(self):
		self.url = r'https://docs.google.com/spreadsheets/d/e/2PACX-1vQUwyeyCbReMBmABf-Q-XqG40oB5KrDQoUlLMpDZhBu18YasgWI72pAyH4beYolw95ylxQJdPqSWcig/pubhtml'
	
	def run(self):
		self.soup = self.getSoup(self.url)
		#  Checking for cache 
		if os.path.isfile('db.json'):
			with  open('db.json','r') as f:
				self.db = json.load(f)
		else:
			#  requesting and storing in json file
			self.fetch_links(self.url)
			self.tojson(self.db)

	
	#  Return Soup Object
	def getSoup(self,url):
		self.r = requests.get(url)
		return BeautifulSoup(self.r.content,'html.parser')
	
	#  Scraping links with Chapter names	
	def fetch_links(self,soup):
		''' Messy code / Worst way to do this'''
		#  physics , chemistry , maths , chapter names | class of tags for note links
		classes = [['s2','s21','s23','s30','s24 softmerge','s22 softmerge','s18','s19','s15','s19 softmerge','s10','s10 softmerge','s25'],['s7','s0','s17']]
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
		print([{(key,len(value.keys())):reduce(lambda acc,nk:acc+len(self.db[key][nk]),value.keys(),0)} for key,value in self.db.items()])

	#  Cacheing	
	def  tojson(self,db):
		with open('db.json','w') as f:
			json.dump(db,f,ensure_ascii=False,indent=4)

	#  to unshorten the url
	def _unshorten(self,url):
		soup = self.getSoup(url)
		ulink = soup.find('a').get_text()
		return requests.head(ulink, allow_redirects=True).url
	
	#  Fetching id of gdrive link
	def fetch_id(self,url):
		pattern = re.compile(r'd\/(.*?)\/view')
		return pattern.findall(self._unshorten(url))[0]

	#  Downloading content using id
	def download_content(self,subject,chapter,path=os.path.dirname(os.path.abspath(__file__))):
		apath = os.path.join(path,chapter)
		if not os.path.isdir(apath):
			os.mkdir(apath)
		for index,links in enumerate(self.db[subject][chapter]):
			ids = self.fetch_id(links)
			f_path = os.path.join(apath,f'{chapter} L{index+1}.pdf')
			print('Downloading Lecture-',index+1)
			gdownloader.downloadfile(ids,f_path)
			print('Notes Saved to ',f_path)
	def timeme(fn):
		def dfn(*args):
			start = time.time()
			r_value = fn(*args)
			print('Total time taken :',time.time()-start)
			return r_value
		return dfn


if __name__ == '__main__':
	obj = Unacdemy()
	obj.run()
	obj.download_content('maths',"Application of Derivatives")