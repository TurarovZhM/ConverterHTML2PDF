import pdfkit as pdfkit
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
import codecs
import base64

path = "/Users/zhomart/Documents/Fraunhofer/HTMLtoPDF/ConverterHTML2PDF/WebDocumentation"
# pathOut = "/Users/zhomart/Documents/Fraunhofer/HTMLtoPDF/ConverterHTML2PDF/WebDocumentation/output"


# if not os.path.exists(pathO):
#    os.makedirs(pathOut)


print('Conversion started...')

# Start time
start = time.time()

if os.path.exists(path + '/TEMP_MESHFREE.html'):
    os.remove(path + '/TEMP_MESHFREE.html')

html_files = [f for f in os.listdir(path) if
              f.endswith('.html') and f != 'MESHFREE.html' and f != 'MESHFREEdocu_AllInOne.html']


# print(len(html_files))


# for f in html_files[:10]:
#    print(f)


def filterAndSortHTMLfiles(html_files):
    # Convert list of html files into DataFrame
    df = pd.DataFrame(html_files)
    # df.head(10)

    ordered_list_html_files = ['MESHFREE.html']
    order_by_list = ['InstallationGuide', 'GettingStarted', 'InputFiles', '__Constants__', 'RunTimeTools', 'Solvers',
                     'PerformanceOptimization', 'Windows', 'Support', 'Releases', 'Indices']

    # new data frame with split value columns
    dftmp = df[0].str.split('html', expand=True)[0]
    df2 = dftmp.str.split(".", expand=True)

    for order in order_by_list:
        list2 = df2[df2[1] == order].sort_values(
            [df2.columns[2], df2.columns[3], df2.columns[4], df2.columns[5], df2.columns[6], df2.columns[7],
             df2.columns[8]], ascending=[True, True, True, True, True, True, True]).apply(
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


outputfile = open(path + "/TEMP_MESHFREE.html", "w+")

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
<link href="search/css/bootstrap.css" rel="stylesheet">
<link href="search/css/fraunhofer.css" rel="stylesheet">
<script type="text/javascript" src="search/js/jquery-1.12.0.js"></script>
<script src="search/js/bootstrap.min.js"></script>
<script src="search/js/custom.js"></script>
<style>
@media screen {
    p, h1, h2, h3 {
        display: block;
        page-break-inside: avoid !important;
    } 
}
</style>
</head>
<body>""")


def changeLinksInDIV(div_text):
    for link in div_text.findAll('a'):
        # be careful not to change .pdf files links
        txtlink = str(link.get('href')).strip()
        if txtlink.endswith('.html') and (not txtlink.startswith('http')) and (not txtlink.startswith('www')):
            # print(txtlink)
            link['href'] = link['href'].replace(link['href'], '#' + link['href'])


def get_image_file_as_base64_data(div_text):
    for img in div_text.findAll('img'):
        txt_img = str(img.get('src')).strip()
        # print(txt_img)

        if not txt_img.startswith('..'):
            txt_img = path + '/' + txt_img

        if txt_img.endswith('.png'):
            with open(txt_img, 'rb') as image_file:
                b64_str = base64.b64encode(image_file.read()).decode()
                img['src'] = img['src'].replace(img['src'], 'data:image/png;base64,' + str(b64_str))
                # encoded = base64.b64encode(b64_str)
        if txt_img.endswith('.jpg') or txt_img.endswith('.jpeg'):
            with open(txt_img, 'rb') as image_file:
                b64_str = base64.b64encode(image_file.read()).decode()
                img['src'] = img['src'].replace(img['src'], 'data:image/jpeg;base64,' + str(b64_str))
                # encoded = base64.b64encode(b64_str)
    # print(str(b64_str))


def convertHTML2PDF(html_files):
    # Call sorting function
    ordered_html_files = filterAndSortHTMLfiles(html_files)

    for file in ordered_html_files:

        print(file)

        file_text = codecs.open(path + '/' + file, 'r')
        html_text = file_text.read()

        soup = BeautifulSoup(html_text, 'lxml')
        div_fhwrapper = soup.find("div", {"class": "fh-wrapper"})  # "header", "class": "border-vertical"})

        div_fhwrapper.find('div', {"class": "header"}).decompose()
        div_fhwrapper.find('div', {"class": "blank-class-outer footer visible-md visible-lg"}).decompose()
        div_fhwrapper.find('div', {"class": "footer-small visible-xs visible-sm"}).decompose()

        # adds # before link
        changeLinksInDIV(div_fhwrapper)

        div_breadcrumbs = soup.find("div", {"class": "breadcrumbs"})

        # sets id name to div
        # it is necessary for anchor links
        div_breadcrumbs.attrs['id'] = str(file)

        # decreases padding
        div_jumbotron = soup.find("div", {"class": "jumbotron"})
        div_jumbotron.attrs[
            'style'] = "padding-top: 5px !important; padding-bottom: 10px !important; margin-bottom: 0px !important;"

        # deletes empty bullets in list
        for x in div_fhwrapper.findAll('li'):
            # print(x)
            if len(x.get_text(strip=True)) == 0:
                x.extract()

        get_image_file_as_base64_data(div_fhwrapper)

        content = str(div_fhwrapper)
        outputfile.write(content)

        soup.clear()
        # print(content)

        # Close read file in this iteration
        file_text.close()

    meshfree_file = codecs.open(path + '/MESHFREE.html', 'r')
    meshfree_text = meshfree_file.read()

    meshfree_soup = BeautifulSoup(meshfree_text, 'lxml')
    div_footer = meshfree_soup.find("div", {"class": "footer-small visible-xs visible-sm"})
    changeLinksInDIV(div_footer)
    content_footer = str(div_footer)
    meshfree_file.close()
    outputfile.write(content_footer)


# Convert WEbDocumentation to PDF
convertHTML2PDF(html_files)

outputfile.write("</body>")
outputfile.write("</html>")
outputfile.close()

print('TEMP_MESHFREE.html file was created')
print('Now converting file to PDF, please wait')
print("...")

# config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")
css = [path + '/search/css/bootstrap.css', path + '/search/css/fraunhofer.css']
options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
}
pdfkit.from_file(path + '/TEMP_MESHFREE.html', path + '/MESHFREE.pdf', options=options, css=css)

# After PDF created, html file is not necessary
# if os.path.exists(path + '/TEMP_MESHFREE.html'):
#    os.remove(path + '/TEMP_MESHFREE.html')

# End time
end = time.time()

print("Convertion time is = ", str((end - start) / 60) + ' min')
print('PDF is Ready!')