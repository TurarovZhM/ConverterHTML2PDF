#!/bin/csh -f
unalias cp
unset -f cp
echo 
echo "-------------> remove files from FPMDOCU"
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/*.html
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/*.png
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/search/*.*
# try to remove all files except for everything that is contained in the .svn-folders (otherwise, svn is confused)
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/OnlineExamples/*
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/OnlineExamples/*/*
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/OnlineExamples/*/*/*
rm --force /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/OnlineExamples/*/*/*/*


echo "-------------> copy new files to FPMDOCU" 
cp -u --force *.html /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation
cp -u --force *.png /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation
cp -u --force search/* /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/search
cp -u --force -L -r OnlineExamples/* /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/WebDocumentation/OnlineExamples/.

echo "-------------> svn status check" 
cd /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/
# remove all unnecessary files from the svn 
svn st | grep ! | cut -d! -f2| sed 's/^ *//' | sed 's/^/"/g' | sed 's/$/"/g' | xargs svn rm
#svn commit --message "new version on FPMDOCU"
cd -
cd ..
echo "-------------> copy PDF and PNG" 
cp --parents --force -u */*.pdf /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/
cp --parents --force -u */*.png /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/
cd -
# add all new files to svn
cd /p/tv/FPM_presentations/FPMDOCU/FPMDOCU/
#svn add *
#svn add */*
#svn add */*/*
#svn add OnlineExamples/*
#svn add OnlineExamples/*/*
echo "-------------> svn add" 
svn add --force *
#
# now even create a tar file of all the data
#
echo "-------------> svn add FPMDOCU.tar.gz" 
rm --force FPMDOCU.tar.gz
tar -c -z --exclude-vcs --exclude "Executables" -f FPMDOCU.tar.gz *
svn add FPMDOCU.tar.gz
cd -
