# -*- coding: utf-8 -*-
import os
import sys
import argparse
import json
from bs4 import BeautifulSoup

""" this file reads html files from given input directory path,
	extracts required information from the files and
	saves json variable file 'web.json' in output directory path
	
	if anything goes wrong while reading files, it writes into 
	read-html-files-log.txt file in the output directory path
	
	//
	BeautifulSoup is a python package which is used to extract
	text content from the html file
	//
	Json is a pyton package which is used to read and write data in json format
	//
	Here we are storing id, title and body as json data
	id = a unique identifier to the document, which is used to distinguish between multiple documents
	title = title of the document
	url = url of the html file which will be used to link html file in search result
	body = content of the html file in plane text format
	body and title both are used to indexing purpose
	//
	
	
"""

def main(argv):
	#reading command line argument
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--inputdirectory',
						help = 'Input Directory Path',
						required = 'True')
	parser.add_argument('-o', '--outputdirectory',
						help = 'Output Directory Path',
						required = 'True')
	args = parser.parse_args(argv)
	
	input_directory_path = args.inputdirectory
	output_directory_path = args.outputdirectory
	"""
		if there is missing title tag or body tag in html file, 
		log that information in read-html-files-log.txt in the output directory	 
	"""

	i = 1
	data = []
	missingTitleTag = 0
	missingBodyTag = 0
	logFile =  open(output_directory_path+'/read-html-files-log.txt',"w")
	for file in os.listdir(input_directory_path):
		if file.endswith(".html"):
			f = open(input_directory_path+'/'+file, 'r')
			soup = BeautifulSoup(f, 'html.parser')
			
			item = {"id" : i}
			if soup.title is None:
				item["title"] = ''
				logFile.write(file +'.............. Missing Title Tag\n')
				missingTitleTag +=1
			else:
				item["title"] = soup.title.get_text()
			if soup.body is None:
				item["body"] = ''
				logFile.write(file +'.............. Missing Body Tag\n')
				missingBodyTag +=1
			else:
				item["body"] = soup.body.get_text()
			item["url"] = '../'+ file
			data.append(item)
			i +=1
			f.closed
	logFile.closed

	if i>1:
		with open(output_directory_path+'/web.json',"w") as json_file:
			"""
			dumping the data in json file
			@data = array data which is in json format
			@json_file = name of the file in which data will be dump
			@indent= 4 - for dumping the json data in user readable format
			"""
			json_file.write('var data = ')
			json.dump(data, json_file,indent=4)
		json_file.closed

		print str(i-1) +' file(s) read successfully'
		if missingTitleTag>0:
			print str(missingTitleTag) + ' html file(s) without Title tag'
		if missingBodyTag>0:
			print str(missingBodyTag) + ' html file(s) without Body tag'
		if missingTitleTag>0 or missingBodyTag>0:
			print 'Please check read-html-files-log.txt file for detailed log'
			

	else:
		print 'No suitable files found'
		
if __name__ == "__main__":
	main(sys.argv[1:])
