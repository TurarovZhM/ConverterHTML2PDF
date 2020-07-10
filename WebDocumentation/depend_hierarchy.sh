#!/bin/bash 
################################################################################
# Script for fixing entries in FPMDOCUdepfile which use shortcuts for
# the hierarchy description.
# - lines starting with '..' are children of the previous hierarchy
# - lines starting with '.' are on the same hierarchy level as the previous item
################################################################################

# FPMDOCUdepfile.new will be used as intermediate file and thus needs to be empty
rm -f FPMDOCUdepfile.new

# variables to store the current hierarchy
PARENT=""
CHILD=""

# read FPMDOCUdepfile line by line
while read -r line
do
  # clear output...
  printf '%s\r' "                                                                                "
  # ...and print current status (i.e. which line we are currently processing)
  printf '%s\r' "${line:0:75}[...]"   # progress
  
  if [ ${line:0:2} = ".." ]   # FPMDOCU adding a child to current hierarchy
  then      
    PARENT=$(echo "$PARENT.$CHILD")
    CHILD=$(echo "$line" | sed -e 's@^\.\.\(.*\).html.*@\1@' | sed -e 's@\*@\\\*@')
    NEW_LINE=$(echo "$line" | sed -e "s/..$CHILD/$PARENT.$CHILD/")
  elif [ ${line:0:1} = "." ]  # FPMDOCU adding child on same hierarchy level
  then
    CHILD=$(echo "$line" | sed -e 's@^\.\(.*\).html.*@\1@' | sed -e 's@\*@\\\*@')
    NEW_LINE=$(echo "$line" | sed -e "s/.$CHILD/$PARENT.$CHILD/")
  else                        # FPMDOCU just update PARENT and CHILD
    PARENT=$(echo "$line" | sed -e 's@\(.*\)\.\([^\.]*\)\.html.*@\1@')
    CHILD=$(echo "$line" | sed -e 's@\(.*\)\.\([^\.]*\)\.html.*@\2@' | sed -e 's@\*@\\\*@')
    NEW_LINE=$line
  fi
  
  # store result in intermediate FPMDOCUdepfile
  echo $NEW_LINE >> FPMDOCUdepfile.new
done < FPMDOCUdepfile
echo "" #add newline after progress

# copy result back to the actual dependency file
cp -f FPMDOCUdepfile.new FPMDOCUdepfile
rm -f FPMDOCUdepfile.new