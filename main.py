import pdfkit as pdfkit
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
import codecs
import base64
import shutil
import warnings
from datetime import date

#path = "..../WebDocumentation"

path = os.getcwd()
pathRef = path +"/Reference/"


if not os.path.exists(pathRef):
    os.makedirs(pathRef)


print('Conversion started...')


# Start time
start = time.time()


if os.path.exists( pathRef + 'TEMP_MESHFREE.html'):
    os.remove(pathRef + 'TEMP_MESHFREE.html')

html_files_not_sorted = [f for f in os.listdir(path) if
              f.endswith('.html') and f != 'MESHFREE.html' and f.split(".")[0] != 'Index' and f != 'MESHFREEdocu_AllInOne.html' and (not ((f.startswith('MESHFREE.GettingStarted') and (('COMMON_VARIABLES' in f.split(".")[-2].upper()) or ('UCV_' in f.split(".")[-2].upper()) ) )))]

#for f in html_files_not_sorted:
#    if f.startswith('MESHFREE.GettingStarted') and ('COMMON_VARIABLES' in f.split(".")[-2].upper()): 
#        html_files_not_sorted.remove(f)
#for f in html_files_not_sorted:
#    if f.startswith('MESHFREE.GettingStarted') and f.split(".")[-2].upper().startswith('COMMON_VARIABLES'): 
#        html_files_not_sorted.remove(f)

def filterAndSortHTMLfiles(html_files):
    # Convert list of html files into DataFrame
    df = pd.DataFrame(html_files)
    # df.head(10)

    ordered_list_html_files = ['MESHFREE.html']
    order_by_list = ['InstallationGuide', 'GettingStarted', 'InputFiles', 'Indices', '__Constants__', 'RunTimeTools', 'Solvers', 'Download', 'PerformanceOptimization', 'Support', 'Releases']

    # new data frame with split value columns
    dftmp = df[0].str.split('html', expand=True)[0]
    df2 = dftmp.str.split(".", expand=True)

    for order in order_by_list:
        list2 = df2[df2[1] == order].sort_values(
            [df2.columns[2], df2.columns[3], df2.columns[4], df2.columns[5], df2.columns[6], df2.columns[7], df2.columns[8]], ascending=[True, True, True, True, True, True, True]).apply(
            lambda x: '.'.join(x.dropna().astype(str)) + 'html',
            axis=1
        )
        for name in list2.values:
            ordered_list_html_files.append(name)

    # Other files in the WebDocumentation, but not included to sort operation above
    # For ex.: MESHFREEdevelopment.html, MESHFREE.Interfaces.html, MESHFREE.MESHFREEdocu.html,
    # MESHFREE.Download.html, MESHFREE.Development.html and many others...
    df3 = df2[~df2[1].isin(order_by_list)]
    list3 = df3.sort_values(
        by=[df3.columns[0], df3.columns[1], df3.columns[2], df3.columns[3], df3.columns[4], df3.columns[5],
            df3.columns[6], df3.columns[7], df3.columns[8]],
        ascending=[False, True, True, True, True, True, True, True, True]).apply(
        lambda x: '.'.join(x.dropna().astype(str)) + 'html',
        axis=1
    )

    for name in list3.values:
        ordered_list_html_files.append(name)

    # len(ordered_list_html_files)

    return ordered_list_html_files



"""
This method changes links in given div tag
For example:
../DifferentialOperators/DOCUMATH_DifferentialOperators.pdf
Canges to: https://svn.itwm.fraunhofer.de/svn/MESHFREEdocu/DifferentialOperators/DOCUMATH_DifferentialOperators.pdf

Also adds # to links to navigate inside pdf file
"""
def changeLinksInDIV(div_text):
    for link in div_text.findAll('a'):
        # be careful not to change .pdf files links
        txtlink = str(link.get('href')).strip()
        
        """
        # Copy to Reference folder
        if txtlink.endswith('.pdf') and (not txtlink.startswith('www')) and (not txtlink.startswith('http')):
            print(txtlink)
            if os.path.isfile(txtlink):
                filename = txtlink.split("/")[-1]
                shutil.copy(txtlink, os.path.join(pathRef, filename))
        """
        if txtlink.startswith('../'):
        #if txtlink.endswith('.pdf') and txtlink.startswith('../'):
            #print('https://svn.itwm.fraunhofer.de/svn/MESHFREEdocu/' + txtlink[3:])
            link['href'] = link['href'].replace(link['href'], 'https://svn.itwm.fraunhofer.de/svn/MESHFREEdocu/' + txtlink[3:])
        
        
        if txtlink.endswith('.html') and (not txtlink.startswith('http')) and (not txtlink.startswith('www')) and (not txtlink.endswith('.pdf')) :
            link['href'] = link['href'].replace(link['href'], '#' + link['href'])
            if '25' in link['href']:
                link['href'] = link['href'].replace('25', '')
        
        if txtlink.startswith('http') or txtlink.startswith('www'):
            link['href'] = txtlink
            

def rename_h1_h2_h3_to_p(div_text, level = -1, ChapterNum = ""):
    
    if level == -1:
        for tags in div_text.findAll('h1'):
            tags.name = 'p' 
            tags.attrs['style'] = "font-size: 1.8em; font-weight: bolder; font-style: italic;"

        for tags in div_text.findAll('h2'):
            tags.name = 'p' 
            tags.attrs['style'] = "font-size: 1.5em; font-weight: bolder;"


        for tags in div_text.findAll('h3'):
            tags.name = 'p' 
            tags.attrs['style'] = "font-size: 1.17em; font-weight: bolder;"
    else:
        for tags in div_text.findAll('h1'):
            tags.string = ChapterNum + tags.get_text()
            tags.name = 'h' + str(level) 
            tags.attrs['style'] = "font-size: 1.8em !important; font-weight: bolder; color: rgb(85, 85, 85);"

    
       
"""
Converts image to base64 format
"""
def get_image_file_as_base64_data(div_text):
    for img in div_text.findAll('img'):
        txt_img = str(img.get('src')).strip()

        if not txt_img.startswith('..'):
            txt_img = path + '/' + txt_img

        if txt_img.endswith('.png'):
            with open(txt_img, 'rb') as image_file:
                b64_str = base64.b64encode(image_file.read()).decode()
                img['src'] = img['src'].replace(img['src'], 'data:image/png;base64,' + str(b64_str))
                if img["class"][0] != "img-responsive":
                    img.attrs['style'] = "max-width: 100%;"
                #else:
                #    img.attrs['style'] = "max-width: 60%;"

        if txt_img.endswith('.jpg') or txt_img.endswith('.jpeg'):
            with open(txt_img, 'rb') as image_file:
                b64_str = base64.b64encode(image_file.read()).decode()
                img['src'] = img['src'].replace(img['src'], 'data:image/jpeg;base64,' + str(b64_str))
                if img["class"][0] != "img-responsive":
                    img.attrs['style'] = "max-width: 100%;"
                #else:
                #    img.attrs['style'] = "max-width: 60%;"


"""
Method divides area for image to two parts.
In first part puts image
In second part writes description
"""
def resize_img_responsive(div):
    image_tags = div.findAll("img", {"class": "img-responsive"})
    childrens = div.findChildren()
    for i in range(1,len(childrens)):
        #print(image)
        if childrens[i-1] in image_tags:
            #print(childrens[i].name)
            #print(childrens[i+1].name)
            
            
            if childrens[i-1].name == 'img' and (childrens[i].name == 'em' or childrens[i].name == 'figcaption'):
                childrens[i-1].attrs['style'] = "width: 100%;height: auto; max-width: 100% !important;"
                childrens[i].attrs['style'] = "width: 100%; height: auto; max-width: 100% !important;"
                
                soup_str = """
                <div style="width:100%; display: -webkit-box; height: auto; margin:0; padding:0; overflow: hidden; page-break-inside:avoid; page-break-after:auto;">
                    <div style="width: 60%; height: auto; margin:0; padding:0;" >
                        {}
                    </div>
                    <div style="width: 40%; height: auto; padding-left:20px; padding-bottom: 0; margin:0; "> 
                        {}
                    </div>
                </div> 
                  """.format(str(childrens[i-1]), str(childrens[i]))
                
                childrens[i].decompose()
                
                soup = BeautifulSoup(soup_str, 'lxml')
                childrens[i-1].replace_with(soup)
            
            #if childrens[i-1].name == 'img'and childrens[i].name != 'em':
            #    childrens[i-1].attrs['style'] = "max-width: 60%;  height: auto;"
        
        


"""
Method drops tables that has header with text: This item is referenced in:
"""
def deleteThisItemReferencedIN(div):
    for link in div.findAll('th'):
        # be careful not to change .pdf files links
        txtlink = str(link.text).strip()
        #print(txtlink)
        if txtlink == 'This item is referenced in:':
            # print(txtlink)
            div.decompose()




"""
Method returns header of pdf File:
"""
def createHeader():
    

    def get_image_base64_data_str():
        image = path + '/search/image/MESHFREE_Logo.png' 

        with open(image, 'rb') as image_file:
            b64_str = base64.b64encode(image_file.read()).decode()
            return "data:image/png;base64,"+str(b64_str)


    divTxt = """
    <div style="margin-left: 3rem;"> 
        <div class="header">
            <div class="row header-row">
                <div class="col-sm-4">
                   <a class="a_link" href="https://www.meshfree.eu">
                      <img class="logo img-responsive1" style="max-width: 100% !important;" alt="" src="search/image/MESHFREE_Logo.png">
                   </a>
                </div>
            </div>
        </div>
    
        <div class="row company_name" style="margin-bottom: 1.5rem;">
            <a href="https://www.meshfree.eu">
            Simulate with complex geometries and complex physics
            </a>
        </div>
    </div>
    """
    
    divTxtSoup = BeautifulSoup(divTxt, 'lxml')

    get_image_file_as_base64_data(divTxtSoup)
    outputfile.write(str(divTxtSoup))
    
    today = date.today()
    # Textual month, day and year
    dateToday = today.strftime("%B %d, %Y")
    print("Today =", dateToday)
    
    outputfile.write("""</div>""")
    strng = """
    <div>
        <div class="row">
            <div style="margin-left: 3rem;">
            <div style="margin-bottom: 1.5rem;">
                <a href="http://www.itwm.fraunhofer.de"> &#169; 2020 Fraunhofer Institute for Industrial Mathematics ITWM</a>
            </div>
            <divstyle="margin-bottom: 1.5rem;">
                <p>Document created: """ + str(dateToday) + """</p>
            </div>
            </div>
        </div>
    </div>
    """
    outputfile.write(strng)

    # End Header
    # ----------------------------------------------------------



"""
This method creturns outline of PDF document
"""
def createOutline(html_files):
    list_for_outline = []
    # Get sorted list of html files from Web Documentation folder
    #ordered_html_files = filterAndSortHTMLfiles(html_files)
    ordered_html_files = html_files
    
    outline_text = """<div id="outline" style="margin: 1.5rem;">\n
    <h1 style="margin-bottom: 25px;">OUTLINE</h1>\n"""
    
    for file in ordered_html_files:
        if file.count('.') <= 3:
            list_for_outline.append(file)
    #return list_for_outline
     
    prev_splitted_file = list_for_outline[0].split(".")
    
    ChapterNum = ''
    ChapterNum1 = 1
    ChapterNum2 = 0
    ChapterNum3 = 0
    ChapterNum4 = 0
    
    for file in list_for_outline:
        level = 1
        splitted_file = file.split(".")
        #count = 0
        
        
        if file == 'MESHFREE.html':
            level = 1
        else:
            num_level = min(len(prev_splitted_file), len(splitted_file))-1

            for lev in range(num_level):
                if splitted_file[lev] != prev_splitted_file[lev]:
                    break
                else:
                    level=level+1
        """    
        if level == 1:
            ChapterNum1=ChapterNum1+1
            ChapterNum2=0
            ChapterNum3=0
            ChapterNum4=0
            ChapterNum = str(ChapterNum1) 
        """
        if level == 2:
            ChapterNum2=ChapterNum2+1
            ChapterNum3=0
            ChapterNum4=0
            ChapterNum = str(ChapterNum2) + '. '

        if level == 3:
            ChapterNum3=ChapterNum3+1
            ChapterNum4=0
            ChapterNum = str(ChapterNum2) + '.' + str(ChapterNum3) + '. '
        
        if level == 4:
            ChapterNum4=ChapterNum4+1
            ChapterNum = str(ChapterNum2) + '.' + str(ChapterNum3) + '.' + str(ChapterNum4) + '. '
                   
                    
        #if len(splitted_file) > len(prev_splitted_file):
        #    level=level+1
            
                
        prev_splitted_file = splitted_file
        
        if splitted_file[1] == '__Constants__' and splitted_file[2] != 'html':
            continue

        if splitted_file[0] != 'Index':
            if level <= 2:
                #outline_text = outline_text + """<div style="margin-top: 10px;"></div>\n"""
                outline_text = outline_text + """<div style="margin-left: """  + str((level - 1) * 30) + """px; margin-top: 10px; margin-bottom: 15px; font-size: 23px; /*font-weight: bold;*/"><a href ="#""" + file + """">"""  + ChapterNum + file.split(".")[-2] + "</a></div>\n"
            else:
                outline_text = outline_text + """<div style="margin-left: """  + str((level - 1) * 30) + """px; margin-top: 5px; margin-bottom: 5px; font-size: 17px;"><a href ="#""" + file + """">""" + ChapterNum + file.split(".")[-2] + "</a></div>\n"
        
        #else:
        #    if level == 0:
        #        outline_text = outline_text + """<div style="margin-left: """  + str((level - 1) * 30) + """px; margin-top: 10px; margin-bottom: 15px; font-size: 23px; /*font-weight: bold;*/"><a href ="#""" + file + """">""" + file.split(".")[-2] + "</a></div>\n"
        #    else:
        #        outline_text = outline_text + """<div style="margin-left: """  + str((level - 1) * 30) + """px; margin-top: 5px; margin-bottom: 5px; font-size: 17px;"><a href ="#""" + file + """">""" + file.split(".")[-2] + "</a></div>\n"
        
       
        
    outline_text = outline_text + "</div>\n"
    #print( outline_text)
    return outline_text


def strip_text(div, file):
    for text in div.find_all_next(text=True):
        #if isinstance(text, Comment):
            # We found a comment, ignore
        #    continue
        if not text.strip():
            # We found a blank text, ignore
            continue
        # Whatever is left must be good
        #print("+", text, "+")
        #text.lstrip()
        if text.split("\n")[0].strip() == "":
            txt = text.strip()
            text.replace_with("\n" + txt + " ")
        else:
            txt = text.strip()
            text.replace_with(" " + txt + " ")

        for word in text.split(" "):
            if len(word) >= 95:
                logfile.write( "WARNING: -- LONG WORD -- in file " + file + "\n")
                logfile.write(word + "\n\n")

##
#This method covers first two rows of #customTable with <tr> tag
#in order to in pdf, in page break, header and first row after header come together
##
def spanRowsofTable(div):

    count = 0
    row = "<tr>"
    
    for tr in div.findAll('tr')[:2]:
        
        count+=1
        if count <= 2:
            #new_tr.insert(count, tr_copy)
            row = row+ str(tr)
            tr.decompose()
           
    row = row+ "</tr>"
    div.insert(0, BeautifulSoup(row, 'html.parser'))
            
    


outputfile = open(pathRef + "/TEMP_MESHFREE.html", "w+")
logfile = open(pathRef + "/LOG_FILE.txt", "w+")
outputfile.write("""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="">
<meta name="author" content="">
<link rel="icon" href="search/image/favicon.ico">
<title>MESHFREEdocu</title>

<!--
<link href="search/css/bootstrap.css" rel="stylesheet">
<link href="search/css/fraunhofer.css" rel="stylesheet">
<script type="text/javascript" src="search/js/jquery-1.12.0.js"></script>
<script src="search/js/bootstrap.min.js"></script>
<script src="search/js/custom.js"></script>
-->
<link type='text/css' href="search/css/bootstrap.css" >
<link type='text/css' href="search/css/fraunhofer.css">
<script type='text/javascript' href="search/js/jquery-1.12.0.js"></script>
<script href="search/js/bootstrap.min.js"></script>
<script href="search/js/custom.js"></script>

<style>
*{
    border-left:#fff !important;
    border-right:#fff !important;
}

.description p {
  max-width: none !important;
}

.breadcrumbs {
  border-bottom: none !important;
  padding-top: 10px !important;
}

.blank-class-outer-top {
  border-top: none !important;
}

.row reference{
    padding-top: 0 !important;
    margin-top: 0 !important;
}
.reference {
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}
.jumbotron{
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}
.content {
    padding-bottom: 0 !important;
}

.customh2 {
    margin-top:0 !important;
    margin-bottom:0 !important;
}

h2.customh2 {
    margin-top:0 !important;
    margin-bottom:0 !important;
}


.code {
    white-space: pre-line !important;
    overflow-y: hidden !important;
    overflow-x: hidden !important;
    
    padding:0.5em ! important;
    margin:0 !important;
}      
.my-code {
    white-space: pre-line;
    page-break-after: auto;
    display:block;
    font-family: monospace;
    
    margin-top:0rem;
    margin-bottom: 0rem;
    margin-left: -0.8em;
    margin-right: -0.8em;
    font-size: 1.4rem;
    text-align:left;
    text-overflow: ellipsis ellipsis;
    overflow: hidden !important;
}

.my-note{
    /*margin-top:1rem;*/
    /*margin-bottom: 1rem;*/
    /*padding:1rem;*/
    background-color: #F5F5F5;
    border: 1px solid #c7cacc;
    white-space:pre-line;
    /*white-space: break-spaces;*/
    font-family: monospace;
    font-size: 1.4rem;
    text-align:left;

    display: block;
    overflow: hidden;
    page-break-inside:avoid; 
    page-break-after:auto;
} 

.comprehensive-example {
    /* text-align: right; */
    margin-left: 10px;
}

@media print {
  h2, h3, p , .code {page-break-inside: avoid;}
  h1, h2, h3, h4 {margin-top:5px !important;}
  h1 {margin-bottom:5px !important;}
  span { page-break-inside: avoid !important; }
  
}

p, .p {
    /*margin-top: 0 !important;
    margin-bottom: 1px !important;
    */
}

.table-responsive {
  overflow-x: hidden !important;
  white-space: pre-line !important;
}

.table-responsive table tr {
    /*background-color: #f7f7f7; */
    background-color: #fff !important;
}

#customTable , .table{
    
    /*overflow: hidden;
    display: block;*/
    /*overflow: hidden;

    page-break-inside:avoid; */
    
}


.table{
    page-break-inside:avoid; 
}


tr{
    
    page-break-inside:avoid; 
}


td, .table-responsive > .table > tfoot > tr > td {
    white-space: pre-line !important;
}

@media print
{
  table { page-break-after:auto ;
      overflow-x: hidden;
      /*display:block;*/
  }
  
  tr    { page-break-inside:avoid; page-break-after:auto }
  td    { page-break-inside:avoid; page-break-after:auto }
  thead { display:table-header-group }
  tfoot { display:table-footer-group }
  

  
  
}

.a_link {
    display: inline-block;
}


.img-responsive{
    max-width: 60% !important;
}

img.latex{
    /*transform: scale(0.6);*/
    transform-origin:  bottom left;
    height: auto;
    width: auto;
    zoom:0.8;
}

</style>


</head>
<body>

""")



"""
This method prepares one large html file for convertion.
Inside this method, other methods calls.
"""
def convertHTML2PDF(html_files):

    # Get sorted list of html files from Web Documentation folder
    #ordered_html_files = filterAndSortHTMLfiles(html_files)
    ordered_html_files = html_files

    # Add Header
    createHeader()
    #header_text = createHeader()
    #outputfile.write(header_text)
    
    # Add Table of Contents
    outline_text = createOutline(html_files)
    outputfile.write(outline_text)


    outputfile.write("""<div class="my-fh-wrapper"> """)
    
    
    ChapterNum = ''
    ChapterNum1 = 1
    ChapterNum2 = 0
    ChapterNum3 = 0
    ChapterNum4 = 0
    
    # After header add following texts of files to prepared large html file
    for file in ordered_html_files:

        print(file)
        
        ####
        level = 1
        
        
        if file == 'MESHFREE.html':
            level=1
            prev_splitted_file = file.split(".")
        else:  
            #print(prev_splitted_file)
            
            splitted_file = file.split(".")
            #print(splitted_file)
        
            num_level = min(len(prev_splitted_file), len(splitted_file)) 

            for lev in range(num_level):
                if splitted_file[lev] != prev_splitted_file[lev]:
                    break
                else:
                    level=level+1
            """
            if level == 1:
                ChapterNum1=ChapterNum1+1
                ChapterNum2=0
                ChapterNum3=0
                ChapterNum4=0
                ChapterNum = str(ChapterNum1) 
            """

            if level == 2:
                ChapterNum2=ChapterNum2+1
                ChapterNum3=0
                ChapterNum4=0
                ChapterNum = str(ChapterNum2) + '. '
            if level == 3:
                ChapterNum3=ChapterNum3+1
                ChapterNum4=0
                ChapterNum = str(ChapterNum2) + '.' + str(ChapterNum3) + '. '
            if level == 4:
                ChapterNum4=ChapterNum4+1
                ChapterNum = str(ChapterNum2) + '.' + str(ChapterNum3) + '.' + str(ChapterNum4) + '. '
            
            prev_splitted_file = splitted_file
                
        if level > 4:
            level = -1
        
        #if file.split(".")[0] == 'Index':
        #    level=-1
        
        
        ####
        
        file_text = codecs.open(path + '/' + file, 'r')
        html_text = file_text.read()

        soup = BeautifulSoup(html_text, 'lxml')
        div_fhwrapper = soup.find("div", {"class": "fh-wrapper"})  # "header", "class": "border-vertical"})

        div_fhwrapper.find('div', {"class": "header"}).decompose()

        # Delete footer
        #if div_fhwrapper.find('div', {"class": "blank-class-outer-top footer"}):
        #    div_fhwrapper.find('div', {"class": "blank-class-outer-top footer"}).decompose()

        # Change Link in DOWNLOAD COMPREHENSIVE EXAMPLE to downlad files in svn
        if div_fhwrapper.find('div', {"class": "blank-class-outer-top footer"}):
            div_footer_download = div_fhwrapper.find('div', {"class": "blank-class-outer-top footer"})
            changeLinksInDIV(div_footer_download)

        if div_fhwrapper.find('div', {"class": "blank-class-outer footer visible-md visible-lg"}):
            div_fhwrapper.find('div', {"class": "blank-class-outer footer visible-md visible-lg"}).decompose()
        if div_fhwrapper.find('div', {"class": "footer-small visible-xs visible-sm"}):
            div_fhwrapper.find('div', {"class": "footer-small visible-xs visible-sm"}).decompose()

        # Change style of div "fh-wrapper"
        div_fhwrapper.attrs['style'] = "margin-left: 2.5rem; margin-right: 2.5rem; display: block;"

        # adds # before link, to navigate inside pdf
        changeLinksInDIV(div_fhwrapper)

        #rename_h1_h2_h3_to_p(div_fhwrapper)
        
        
        # Delete tables with header text : 'This item referenced in:'
        if div_fhwrapper.find('div', {"class": "blank-class-outer-top"}):
            #div_blank_class_outer_top = div_fhwrapper.find('div', {"class": "blank-class-outer-top"})
            #deleteThisItemReferencedIN(div_blank_class_outer_top)
            for div_blank_class_outer_top in div_fhwrapper.findAll('div', {"class": "blank-class-outer-top"}):
                # be careful not to change .pdf files links
                deleteThisItemReferencedIN(div_blank_class_outer_top)

        if not div_fhwrapper.find('div', {"class": "blank-class-outer-top"}):
            div_description = soup.find("div", {"class": "description"})
            if str(div_description.text).strip() == "":
                continue




        # Deletes empty <li> tag in this file
        for x in div_fhwrapper.findAll('li'):
            #print(str(x.get_text(strip=True)))
            if len(x.get_text(strip=True)) == 0:
                x.extract()
            for p in x.findAll('p'):
                p.replaceWithChildren()

        # Find div breadcrumbs
        div_breadcrumbs = soup.find("div", {"class": "breadcrumbs"})

        # sets id name to div 
        # it is necessary for anchor links
        div_breadcrumbs.attrs['id'] = str(file)

        # Change styles
        div_bordervertical = div_fhwrapper.find("div", {"class": "border-vertical"})
        if div_bordervertical:
            div_bordervertical.attrs['style'] = 'padding-left: 10px; padding-right: 10px;'

        div_jumbotron = soup.find("div", {"class": "jumbotron"})
        div_jumbotron.attrs[
            'style'] = "padding-top: 5px !important; padding-bottom: 10px !important; margin-bottom: 0px !important;"

        rename_h1_h2_h3_to_p(div_jumbotron, level, ChapterNum)
        
        # Renames div 'jumbotron' to 'my-jumbotron'
        # That is needed not to inherit many default styles
        for div in soup.find_all('div', class_='jumbotron'):
            pos = div.attrs['class'].index('jumbotron')
            div.attrs['class'][pos] = 'my-jumbotron'
            
        div_description = soup.find("div", {"class": "description"})
        rename_h1_h2_h3_to_p(div_description)



        for div in div_description.find_all('table', {"id": "customTable"}):            
            spanRowsofTable(div)



        """
        Deletes many break lines fefore text
        """
        strip_text(div_description, file)

        resize_img_responsive(div_description)

        # Replaces image to base64 format
        get_image_file_as_base64_data(div_fhwrapper)

        # Renames div 'fh-wrapper' to 'my-fh-wrapper'
        # That is needed not to inherit many default styles
        for div in soup.find_all('div', class_='fh-wrapper'):
            pos = div.attrs['class'].index('fh-wrapper')
            div.attrs['class'][pos] = 'my-fh-wrapper'

        #for div in soup.find_all('div', class_='code'):
        #    pos = div.attrs['class'].index('code')
        #    div.attrs['class'][pos] = 'my-code'
        
        
        # Trims break lines and spaces of code at the start and end
        for div in soup.findAll("div", {"class": "note"}):
            divcode =  div.find("div", {"class": "code"})
            if divcode:
                divcode.string = divcode.get_text().strip()
        
                
        for div in soup.find_all('div', class_='note'):
            pos = div.attrs['class'].index('note')
            div.attrs['class'][pos] = 'my-note'
        
        if file == 'MESHFREE.InstallationGuide.Execute.CommandLine.html':
            for div in soup.find_all("div", {"class": "my-note"}):
                div.attrs['style'] = 'white-space: pre-wrap;'

        # Write to prepared html file content of div 'my-fh-wrapper'
        div_myfhwrapper = soup.find("div", {"class": "my-fh-wrapper"})
        #content = str(div_myfhwrapper)
        
        for text in div_myfhwrapper.find_all(recursive=False):
            #print(j)
            #find_all(recursive=False)
            outputfile.write(str(text))
        
        #outputfile.write(content)

        soup.clear()
        # print(content)

        # Close read file in this iteration
        file_text.close()


    outputfile.write("""</div>""")
    
    """
    # Add footer to file
    meshfree_file = codecs.open(path + '/MESHFREE.html', 'r')
    meshfree_text = meshfree_file.read()

    meshfree_soup = BeautifulSoup(meshfree_text, 'lxml')
    # Find footer
    div_footer = meshfree_soup.find("div", {"class": "footer-small visible-xs visible-sm"})
    # Change links if necessary
    changeLinksInDIV(div_footer)
    content_footer = str(div_footer)
    meshfree_file.close()
    # write to file
    outputfile.write(content_footer)
    """

    content_footer = """
    <div class="footer-small visible-xs visible-sm">
        <div class="blank-class-outer-bottom">
            <div class="blank-class-inner">
                <div class="row ">
                    <div class="col-md-12">
                        <a href="#MESHFREE.Releases.html" target="_blank">Releases</a>
                    </div>
                </div>
            </div>
        </div>
        <div class="blank-class-outer-bottom">
            <div class="blank-class-inner">
                <div class="row ">
                    <div class="col-md-12">
                        <a href="https://svn.itwm.fraunhofer.de/svn/MESHFREEdocu/Executables/" target="_blank">Executables</a>
                    </div>
                </div>
            </div>
        </div>
        <div class="blank-class-outer-left-right">
            <div class="blank-class-inner">
                <div class="row ">
                    <div class="col-md-12">
                        <a href="http://itwm.fraunhofer.de" target="_blank"> &#169; 2020 Fraunhofer Institute for Industrial Mathematics ITWM</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    """
    outputfile.write(content_footer)


html_files_sorted = filterAndSortHTMLfiles(html_files_not_sorted)


#for htm in html_files_sorted[:150]:
#    print(htm)

# Call Method that prepares large one html file
convertHTML2PDF(html_files_sorted)

outputfile.write("</body>")
outputfile.write("</html>")
outputfile.close()
logfile.close()


print('TEMP_MESHFREE.html file was created')
print('Now converting file to PDF, please wait')
print("...")



# To convert html to pdf using wkhtmltopdf tool
config = pdfkit.configuration(wkhtmltopdf="/p/tv/local/python3.8.3/bin/wkhtmltopdf")
css = [path + '/search/css/bootstrap.css', path + '/search/css/fraunhofer.css']
options = {
    'page-size': 'A4',
    'margin-top': '0.5in',
    'margin-right': '0.5in',
    'margin-bottom': '0.5in',
    'margin-left': '0.5in',
    'footer-right': '[page]',
    #'dpi':96,
    'zoom': 1.8,
}

# Now start convertion
pdfkit.from_file(pathRef + 'TEMP_MESHFREE.html', pathRef + 'MESHFREE.pdf', options=options, css=css, configuration=config)

# Wait 2 second and delete temp file
time.sleep(2)

# After PDF created, html file is not necessary
if os.path.exists(pathRef + 'TEMP_MESHFREE.html'):
    os.remove(pathRef + 'TEMP_MESHFREE.html')

# End time
end = time.time()

print("Convertion time is = ", str((end - start) / 60) + ' min')
print('PDF is Ready!')

