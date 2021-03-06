import json
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

	#  Collecting data
	@timeme
	def __init__(self):
		#  Checking for cache
		if os.path.isfile('db.json'):
			with  open('db.json','r') as f:
				self.db = json.load(f)
		else:
			#  requesting and storing in json file
			raise OSError('db.json file not found ! ')

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
		for index,ids in enumerate(self.db[subject][chapter]):
			f_path = os.path.join(apath,f'{chapter} L{index+1}.pdf')
			if verbose:
				print('[.] Downloading Lecture {} in {}'.format(index+1,f_path))
			else:
				print('[.] Downloading Lecture-',index+1)
			gdownloader.downloadfile(ids,f_path)

		print('Downloaded {} Notes in {}!'.format(chapter,apath))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Unacdemy JEE Notes Downloader tool coded by Tr1ten',usage='python3 main.py -s SUBJECT -c "CHAPTER" "CHAPTER2"..',epilog='note : chapter name is case sensitive so spell it correctly and it should be in qoutes.')
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
	obj = Unacdemy()

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
			print(f'> Downloading {chapters} Notes..')
			obj.download_content(arguments.subject,chapters,arguments.dir,arguments.verbose)
		else:
			print('Thanks for using this tool <3')
	else:
		print('~Chapter not found , maybe you mispelled or forget the qoutes')
		print('use "python main.py --show" to view available chapter names')
