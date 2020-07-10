################################################################################
# Run
# > make full USERSONLY=ON ALLINONE=ON
# if you want to turn on all features and make the original FPMDOCU
#
# For a quick make runs
# > make single PARALLEL=-j8
# or just
# > make PARALLEL=-j8
#
# Interesting targets:
# * full:      run FPMDOCU executable only once to generate full docu
# * clean:     clean up HTML and PNGs
# * distclean: also clean up dependencies
# * depend: important for the following targets
#           excludes some files because they are not matched by the patterns yet
#           excludes FPMDOCU.F90 and equation_parser.f90 because they build every time
# * all (default): generates full docu by dependencies; should be faster than 'full'
#                  the index is most likely wrong if only few files were touched
# * single:        only generates docu for changed files; does not update the search index
# * searchindex:   update the search index (included by 'full' and 'all')
################################################################################

# set default options
USERSONLY=OFF
ALLINONE=OFF

# FPMDOCU executable
FPMDOCU=src/main_FPMDOCU.x


SRC_F90 = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.f90))
SRC_F = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.F))
SRC_CPP = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.cpp))
SRC_H = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.h))
SRC_DOCU = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.fpmdocu))
SRC_docu = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.FPMDOCU))


# set flags based on options
ifeq ($(USERSONLY),ON)
  USERSONLY_FLAG=--ForUsersOnly
  INTERNAL= 
  INTERNALHEADER= 
  SRC_intdocu=
  SRC_intdocu_fileextension=
  minusEfpmintdocu=
else
  USERSONLY_FLAG=
  INTERNAL=-e '!\$$FPMINTDOCU'
  INTERNALHEADER=-e '!\$$FPMINTDOCU\s*\#h.*h\#'
  SRC_intdocu = $(foreach sdir,../../FPM_src,$(wildcard $(sdir)/*.fpmintdocu))
  SRC_intdocu_fileextension=,fpmintdocu
  minusEfpmintdocu=-e ':.*\.fpmintdocu'
endif
ifeq ($(ALLINONE),ON)
  ALLINONE_FLAG=--ProduceAllInOneFile
else
  ALLINONE_FLAG= 
endif

  SRC = $(SRC_F90) $(SRC_F) $(SRC_CPP) $(SRC_H) $(SRC_DOCU) $(SRC_docu) $(SRC_intdocu)


.PHONY: all single full html searchindex clean distclean depend
# default target: generate all through dependencies (i.e. only things that have changed + those which have been exempted from the dependencies)
all:
	make single PARALLEL=$(PARALLEL)
	make fpmdocuF90 
	make equationparserF90 
	make searchindex

-include FPMDOCUdepfile

# only generate the HTMLs where the source has been changed -> faster if there are only few changes; needs 'make depend'
single:
	make FPM_documentation 
	make $(PARALLEL) deferred_single

deferred_single: $(OBJECTS)

# generate the full FPMDOCU in a single run (as before); cleans before it runs
full: html searchindex

# extra target for 'all' because FPMDOCU.F90 is touched every time
fpmdocuF90:
	@echo "Processing ../../FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90"
	-echo "" | grep ../../FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90 -e '!\$$FPMDOCU' $(INTERNAL) > fpmdocuF90.tmpdocu
	sed -i -e 's@^@$<:1:@' fpmdocuF90.tmpdocu
	$(FPMDOCU) --SourceFileName=fpmdocuF90.tmpdocu --IndexFileName=FPM_documentation $(ALLINONE_FLAG) $(USERSONLY_FLAG) >> /dev/zero
	rm fpmdocuF90.tmpdocu

# extra target for 'all' because equation_parser.F90 is touched every time
equationparserF90:
	@echo "Processing ../../FPM_src/FPM_fortran/Misc/equation_parser.f90"
	-echo "" | grep ../../FPM_src/FPM_fortran/Misc/equation_parser.f90 -e '!\$$FPMDOCU' $(INTERNAL) > equationparserF90.tmpdocu
	sed -i -e 's@^@$<:1:@' equationparserF90.tmpdocu
	$(FPMDOCU) --SourceFileName=equationparserF90.tmpdocu --IndexFileName=FPM_documentation $(ALLINONE_FLAG) $(USERSONLY_FLAG) >> /dev/zero
	rm equationparserF90.tmpdocu

# generate full file for indexing (used by %.html)
FPM_documentation: $(SRC)
	grep --include=\*.{f90,cpp,h,fpmdocu$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e '!\$$FPMDOCU' $(INTERNAL) > FPM_documentation
	grep --include=\*.{fpmdocu,FPMDOCU$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e 'xxxxxxxxxxxxxxxxx' --invert-match >> FPM_documentation

# generate the full FPMDOCU HTML files; sub-target to full
html: clean
	grep --include=\*.{f90,cpp,h,fpmdocu$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e '!\$$FPMDOCU' $(INTERNAL) > FPM_documentation
	grep --include=\*.{fpmdocu,FPMDOCU$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e 'xxxxxxxxxxxxxxxxx' --invert-match >> FPM_documentation
	$(FPMDOCU) $(ALLINONE_FLAG) $(USERSONLY_FLAG)
	rm FPM_documentation

# needs to be used in combination with dependencies included from FPMDOCUdepfile; generates docu for a specific HTML file
%.html:
	@echo "Processing $@ from ---$<---=================================================================="
	#@echo "Processing $@ from $<" >> log.txt
	-echo "" | grep $< -e '!\$$FPMDOCU' $(INTERNAL) > "$@.tmpdocu"
	sed -i -e 's@^@$<:1:@' "$@.tmpdocu"
	$(FPMDOCU) --SourceFileName="$@.tmpdocu" --IndexFileName=FPM_documentation $(ALLINONE_FLAG) $(USERSONLY_FLAG) >> /dev/zero
	rm "$@.tmpdocu"

# generate the search index
searchindex:
	./makeSearchIndex.sh

# clean generated output
clean:
	rm -f *.html
	rm -f *.png
	rm -f *-md5.txt
	rm -f *.dvi
	rm -f *.ps
	rm -f *.tmpdocu
	rm -f FPM_documentation

# clean everything, including the dependency file
distclean: clean
	rm FPMDOCUdepfile

# generate the dependencies for HTML to their corresponding .F90 files; does *not* generate dependencies for *all* hierarchy items and not for true .FPMDOCU files (the latter would be quite easy to change)
depend:
	# find all the hierarchy #h...h# items to derive the names of the HTML files and store them as dependencies for the 'single' target
	grep --include=\*.{f90,cpp,h,fpmdocu$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e '!\$$FPMDOCU' $(INTERNAL) | grep -e '!\$$FPMDOCU\s*#h.*h#' $(INTERNALHEADER) | grep -v -e '\.\./\.\./FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90' | grep -v -e '\.\./\.\./FPM_src/FPM_fortran/Misc/equation_parser.f90' | sed -e 's/.*#h\s*\([^ ]*\)\s*h#.*/\1.html\ \\/' | grep -v -e ':' > FPMDOCUdepfile
	sed -i -e '1 s/^/OBJECTS = /' FPMDOCUdepfile
	echo "" >> FPMDOCUdepfile
	# find all the hierarchy #h...h# items (again) and create the real dependencies between the HTML and the F90 files
	grep --include=\*.{f90,cpp,h,fpmdocu$(SRC_intdocu_fileextension)} -rnw '../../FPM_src' -e '!\$$FPMDOCU' $(INTERNAL) | grep -e '!\$$FPMDOCU\s*#h.*h#' $(INTERNALHEADER) | sed 's@\(.*\.[^:]*\):.*#h\s*\([^ ]*\)\s*h#.*@\2.html: \1@' | grep -e ':.*\.f90$$' -e ':.*\.F' -e ':.*\.cpp' -e ':.*\.h' -e ':.*\.fpmdocu' $(minusEfpmintdocu) -e ':.*\.FPMDOCU' >> FPMDOCUdepfile
	./depend_hierarchy.sh         # script to fix shortcuts in the hierarchy definition, i.e. lines that start with '.' or '..'
	# add some more dependencies which seem not to be autogenerated
	echo "FPM.InputFiles.USER_common_variables.MOVE.%MOVE_ProjectionOfMovementOfAnotherPart%.html: ../../FPM_src/FPM_liquid/USER_update_boundary_particles_V2.f90" >> FPMDOCUdepfile
	echo "FPM.InputFiles.USER_common_variables.MOVE.%MOVE_concat%.html: ../../FPM_src/FPM_liquid/USER_update_boundary_particles_V2.f90" >> FPMDOCUdepfile
	echo "FPM.InputFiles.USER_common_variables.MOVE.%MOVE_vertuschka%.html: ../../FPM_src/FPM_liquid/USER_update_boundary_particles_V2.f90" >> FPMDOCUdepfile
	echo "FPM.InputFiles.USER_common_variables.MOVE.%MOVE_ElasticBeam%.html: ../../FPM_src/FPM_liquid/USER_update_boundary_particles_V2.f90" >> FPMDOCUdepfile
	echo "FPM.InputFiles.USER_common_variables.MOVE.%MOVE_ReducedModel%.html: ../../FPM_src/FPM_liquid/USER_update_boundary_particles_V2.f90" >> FPMDOCUdepfile













