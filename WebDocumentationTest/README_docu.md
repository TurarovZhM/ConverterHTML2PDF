# FPMDOCU
The FPMDOCU project aims to provide a smart functionality for creating web based documentation.
The developpers put comments into the FPM source code beginning with "!$FPMDOCU" or "!$FPMINTDOCU" and the FPMDOCU-maker parses these comments to html.

## Compilation of the FPMDOCU-maker
Navigate to the sources of the FPMDOCU and compile the FPMDOCU-maker. This step is necessary the first time and if there were changes in the FPMDOCU-maker, e.g. in the parsing.
```
$ cd FPMsoftwareF95/FPM_documentation/WebDocumentation/src/  
$ module add compiler/intel/ics_xe_2019.2.187 
$ ./compile_FPMDOCU
```
(If the module is no longer available, then a newer version should of course also work.)
## Parsing of the FPMDOCU
Navigate to the FPMDOCU folder and parse FPMDOCU: 
```
$ cd FPMsoftwareF95/FPM_documentation/WebDocumentation/  
$ ./makeFPMDOCU_AllInOne
```
This step will first remove the existing documentation, then parse the documentation and rebuild the search index.

## Opening the docu
The docu is then available by:
```
$ firefox MESHFREE.html  
```
There is also a file containing the complete docu:
```
$ firefox MESHFREEdocu_AllInOne.html  
```

## Issues

Issues we would like to work on in the future:
* Provide a table feature : https://rt.itwm.fhg.de/Ticket/Display.html?id=76589
* Hierarchy Menu on the left
* Apostroph 
* Print View, FPMDOCU -> PDF ( see https://rt.itwm.fhg.de/Ticket/Display.html?id=77062)
* Spell Check
* Optimize Build Velocity
* Optimize Search Function
* Environment for examples (to put them into a frame)
* b-blocks ignore everything that is after the opening #b. (see https://rt.itwm.fhg.de/Ticket/Display.html?id=77062)
* FPMDOCU -> PDF ( see https://rt.itwm.fhg.de/Ticket/Display.html?id=77062)
* Sort should ignore case (AbCd instead of ACbc)
* Explicit Sort order: https://rt.itwm.fhg.de/Ticket/Display.html?id=77261
* In the automated linking with #link also commented Ucv and cv parameters are linked, e.g. see COMP_FillEdges
* prevent self linkage of pages.
* Mark internal documentation https://rt.itwm.fhg.de/Ticket/Display.html?id=77628
* Add link to public MESHFREE site  https://rt.itwm.fhg.de/Ticket/Display.html?id=77629 
