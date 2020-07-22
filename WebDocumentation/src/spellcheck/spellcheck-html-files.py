import os
import sys
import argparse
import codecs
import json
path = os.getcwd()
path = os.getcwd()+'/src/search'
sys.path.insert(1, path)
from bs4 import BeautifulSoup


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
	
	i = 1
	data = []
	missingTitleTag = 0
	missingBodyTag = 0
	body=[]
	if not os.path.exists(output_directory_path):
		os.makedirs(output_directory_path)
	path1=os.path.join(output_directory_path,'temp1.txt') #this file temporarily stores the content of each html page.
	path2=os.path.join(output_directory_path,'output.txt') #Output file where all the spelling errors of html pages are listed.
	path3= os.path.join(output_directory_path,'temp2.txt') #this file temporarily stores the errors of each html page.
	file1 = open(path1,'w')
	file1.close()
	file2 = open(path2,'w')
	file2.close()
	file3 = open(path3,'w')
	file3.close()
	aspell_wordlist=['MESHFREEdocu','MESHFREE','BND','CTRL','FPMDOCu','Fraunhofer','ITWM','LaTeX','executables','fpmdocu','html','indices']
	for word in aspell_wordlist:
			if(word!='\n' and word!=""):
				os.system("echo '*{}\n#' | /p/tv/local/MESHFREEdocu_aspell-0.60.8/bin/aspell -a".format(word))
	
	for file in os.listdir(input_directory_path):
		if (file.endswith(".html") and file!="MESHFREEdocu_AllInOne.html"):
			f = open(input_directory_path+'/'+file, 'r')
			soup = BeautifulSoup(f, 'html.parser')
			item = {"id" : i}
			if soup.body is None:
				item["body"] = ''
			else:
				item["body"] = soup.body.get_text()
			item["url"] = '../'+ file
			#print("file",file)
			
			lines=[]
			lines.append(item["body"].encode('utf-8').strip())
			
			temp=item["url"] 
			
			with open(path1,"w") as file1:
				for item in lines:
					file1.write("%s\n" % item)
			linestemp=[]
			os.system(" /p/tv/local/MESHFREEdocu_aspell-0.60.8/bin/aspell list <$(pwd)/spellcheck/temp1.txt > $(pwd)/spellcheck/temp2.txt")
			file1.close()
			if(os.stat(path3).st_size != 0):
				with open(path3) as file3:
					linestemp = file3.readlines()
					with open(path2, "a") as file2:
						file2.write("\nSpelling Errors in %s are listed below ::- \n\n" % temp)
						file2.writelines(linestemp)
				file2.close()
				file3.close()
			f.closed
	        
		
	text="Completed spell checking for the html files!!!Check the spelling errors in "+output_directory_path+"/output.txt"
	cmd = "echo '{}' ...".format(text)
	os.system(cmd)
	
		
if __name__ == "__main__":
	main(sys.argv[1:])
	
