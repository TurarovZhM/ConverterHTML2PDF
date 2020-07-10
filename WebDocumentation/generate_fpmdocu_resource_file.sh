#!/bin/bash

echo '<RCC>' > fpmdocu.qrc
echo '    <qresource prefix="/original/FPMDOCU/">' >> fpmdocu.qrc

echo "Adding images..."
for file in `ls *.png`; do
  echo "        <file>$file</file>" >> fpmdocu.qrc
done

echo "Adding HTML files..."
for file in `ls *.html | sed -e "s/\*/\&#42;/g"`; do
  echo "        <file>$file</file>" >> fpmdocu.qrc
done

echo "Adding additional files..."
echo '        <file>search/search.html</file>' >> fpmdocu.qrc
echo '        <file>search/web.json</file>' >> fpmdocu.qrc
echo '        <file>search/css/bootstrap.css</file>' >> fpmdocu.qrc
echo '        <file>search/css/fraunhofer.css</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/glyphicons-halflings-regular.ttf</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/icon-font-hinted.ttf</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/icon-font.eot</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/icon-font.svg</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/icon-font.ttf</file>' >> fpmdocu.qrc
echo '        <file>search/fonts/icon-font.woff</file>' >> fpmdocu.qrc
echo '        <file>search/image/1faaa131c4d376eb2d5aaa2e5c13ba2b.png</file>' >> fpmdocu.qrc
echo '        <file>search/image/73873e14214e5f4f586158269c290b68.png</file>' >> fpmdocu.qrc
echo '        <file>search/image/favicon.ico</file>' >> fpmdocu.qrc
echo '        <file>search/image/itwm_60mm_709x193_300dpi_rgb.png</file>' >> fpmdocu.qrc
echo '        <file>search/image/search-icon.png</file>' >> fpmdocu.qrc
echo '        <file>search/js/bootstrap.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/bootstrap.min.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/custom.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/jquery-1.12.0.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/jquery.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/jquery.mark.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/lunr.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/search-query.js</file>' >> fpmdocu.qrc
echo '        <file>search/js/w3data.js</file>' >> fpmdocu.qrc
echo '    </qresource>' >> fpmdocu.qrc
echo '</RCC>' >> fpmdocu.qrc
sed -e "s/_<_/_\&lt;_/" -i fpmdocu.qrc


echo "Generating built-in resources..."
rcc -name fpmdocu fpmdocu.qrc -o qrc_fpmdocu.cpp
echo "Generating external resource file..."
sed -e "s:<qresource prefix=\"/original/FPMDOCU/\">:<qresource prefix=\"/FPMDOCU/\">:" -i fpmdocu.qrc
rcc -binary -name fpmdocu fpmdocu.qrc -o fpmdocu.rcc

echo "Please copy qrc_fpmdocu.cpp and fpmdocu.rcc to the respective folders of STRING."