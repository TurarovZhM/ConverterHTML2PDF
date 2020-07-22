#include "FPM_src/FPM_fortran/Modules/FPM_Types.f90"
#include "FPM_src/FPM_cpp/fortran_bridge/cpp_bridge.f90"
#include "FPM_src/FPM_fortran/PerformanceAndControl/FPM_RealNumber_Operations.f90"
#include "FPM_src/FPM_include/fpm_interfaces.f90"
!#if defined NO_CD
!#include "FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90.BeforeSwitchToITWMCorporateIdentity"
!#else
!#include "FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90"
!#endif
#include "FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU.f90"
!#include "FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMDOCU_BeforeSwitchToITWMCorporateIdentity.f90"
#include "FPM_src/FPM_fortran/PerformanceAndControl/string_operations.f90"
#include "FPM_src/FPM_fortran/Misc/FPM_exit.f90"
#include "FPM_src/FPM_fortran/Misc/find_free_unit.f90"
#include "FPM_src/FPM_fortran/Misc/ESI/release_ESI_license.f90"
#include "FPM_src/FPM_fortran/PerformanceAndControl/ChainOfStringOperations.f90"
#include "FPM_src/FPM_fortran/PreAndPostprocessing/FPMLOG/FPMLOG.f90"
#include "FPM_src/FPM_fortran/PreAndPostprocessing/Save/USER_save_data_CloseTimeStepFiles.f90"
#include "FPM_src/FPM_fortran/Misc/FILE_operations.f90"

program main_FPMDOCU
  use FPM_Types
#include "fpm_declarations.h"
implicit none
!#include "fpm_type_declarations.h"
  _integer4fpm_, parameter  :: NCurrentElement=100
  type(FPMDOCU_Container)   :: Root, RootIndex, SecondaryRoot, SecondaryRootIndex, CurrentElement(NCurrentElement), HelpElement, PreviousElement
  character*1024            :: Str, DStr, Orig, FileName, NameStr, CompleteName, FileStr, Argument, SourceFileName, IndexFileName
  character(:), allocatable :: full_command_line
  character*64              :: LstrOPEN(1000), LstrCLOSE(1000), strOPEN, strCLOSE

  character*8               :: Dashes
  _integer4fpm_             :: lenStr, lenDstr, ih_beg, ih_end, UN(1000), len_trimf77, iFPMDOCU, lenOrig, lenFileName, FileNameLineNumber, &
                               i, i2=2, i4=4, UNAIO, iFirst, len, iStat, UsersOnly, nbCurrentElement, lenDstrAll, lenNameStr, ih_DD, lenCompleteName, &
                               iFileHierarchy, lenFileStr, lenArgument, lenSourceFileName, lenIndexFileName, &
                               iOPEN_beg, iOPEN_end, iCLOSE_beg, iCLOSE_end, iStartFile, len_strOPEN, len_strCLOSE, Llen_strOPEN(1000), Llen_strCLOSE(1000)
  _logical4fpm_             :: isInsideBlock, isEndOfBlockWithValidLine, Lex, lExist, isSourceFileExist, isIndexFileExist, lOPEN(1000), Lvalid

  isInsideBlock = .false.
  isIndexFileExist = .false.
  isSourceFileExist = .false.

  Dashes = '"' // "'"

  SourceFileName = 'FPM_documentation'
  
  !check if source and index file are given in argument
  !If source file is not given, FPM_documentation file is used as source file 
  i = 0
  UsersOnly=0
  DO
    CALL get_command_argument(i, Argument)
    lenArgument = len_trimf77(Argument,1024)
    IF (lenArgument == 0) EXIT
    !check for source file name
    if ( index(Argument,'--SourceFileName=') .gt. 0 ) then
	   isSourceFileExist = .true.	
	   SourceFileName = Argument(18:lenArgument) 
    end if
    
    !check for index file name
    if ( index(Argument, '--IndexFileName=') .gt. 0 ) then
	   isIndexFileExist = .true.
	   IndexFileName = Argument(17:lenArgument) 
    end if   
    
    !already check if user docu here so that internal parts can be removed from .fpmdocu files
    if ( index(Argument, '--ForUsersOnly') .gt. 0 ) then
	   UsersOnly=1
    end if    

    i = i+1
  END DO
  
  lenSourceFileName = len_trimf77(SourceFileName, 1024)
  lenIndexFileName = len_trimf77(IndexFileName, 1024)
  
  
  Root%Pointer => NULL()
  RootIndex%Pointer => NULL()
  do i = 1,NCurrentElement
     CurrentElement(i)%Pointer => NULL()
  end do

  iFileHierarchy = 1
  UN(iFileHierarchy) = 21
  lOPEN(iFileHierarchy) = .true.
  open( unit=UN(iFileHierarchy), file=SourceFileName(1:lenSourceFileName), status='UNKNOWN' )
  Str = ' '

 
  
do
  read(UN(iFileHierarchy),'(a)',end=90) Str
  lenStr = len_trimf77(Str,1024)
  
  ! check if lines valid if open and closing clauses exist
  if ( Llen_strOPEN(iFileHierarchy) .gt. 0 ) then 
     if ( .not. lOPEN(iFileHierarchy) ) then
        i = index( Str(1:lenStr), LstrOPEN(iFileHierarchy)(1:Llen_strOPEN(iFileHierarchy)) )
        if ( i .gt. 0 ) then
           lOPEN(iFileHierarchy) = .true.
           cycle
        end if
     else
        i = index( Str(1:lenStr), LstrCLOSE(iFileHierarchy)(1:Llen_strCLOSE(iFileHierarchy)) )
        if ( i .gt. 0 ) then
           lOPEN(iFileHierarchy) = .false.
           cycle
        end if
     end if
  end if
  
  if ( .not. lOPEN(iFileHierarchy) ) cycle ! if line is not valid because it is not inbetween the opening and closing clauses
  
  Orig(1:lenStr) = Str(1:lenStr)
  lenOrig = lenStr
  
  !write(*,'(a)') 'read: Str = >>>' // Str(1:lenStr) // '<<<'

! first extract the name of the source file and the line number. The file name is always at the beginning of the line, followed by a ':', then the line number, followed by another ':'
! however, do this only on the lowest hierarchy level, as these lines stem from a grep and therefore contain file information.
  if ( iFileHierarchy .eq. 1 ) then  
     i = index( Str(1:lenStr),':' )
     FileName = Str(1:i-1)
     lenFileName = i-1
     Str(1:i) = ' '
     call RemoveLeadingSpaces(Str, lenStr)


     i = index( Str(1:lenStr),':' )
     read(Str(1:i-1),*) FileNameLineNumber
     Str(1:i) = ' '
     call RemoveLeadingSpaces(Str, lenStr)
  end if
  
  !call RemoveLeadingSpaces(Str, lenStr)   !  just to cleanup

! now serach for occurence of !$FPMDOCU
  iFPMDOCU = index( Str(1:lenStr),'!$FPMDOCU' )
  if ( iFPMDOCU .le. 0 ) then  ! if no !$FPMDOCU is in the line, we assume that the line stems from a .fpmdocu file where all !$FPMDOCU are dropped or we have !$FPMINTDOCU
     iFPMDOCU = index( Str(1:lenStr),'!$FPMINTDOCU' )
     if ( iFPMDOCU .le. 0 ) then
        Str = Str(1:lenStr)
        lenStr = len_trimf77(Str,1024)
     else
        if (UsersOnly .gt. 0) cycle !remove FPMINTDOCU lines from .fpmdocu files
        Str = Str(iFPMDOCU+12:lenStr)
        lenStr = len_trimf77(Str,1024)
     end if
  else
     Str = Str(iFPMDOCU+9:lenStr)
     lenStr = len_trimf77(Str,1024)
  end if
!  call RemoveLeadingSpaces(Str, lenStr)
  write(*,'(a)') 'read: Str = >>>' // Str(1:lenStr) // '<<<'

  
  
  
  Dstr = Str(1:lenStr)
  lenDstr = lenStr
  call RemoveLeadingSpaces(Dstr, lenDstr)
  
! check include file definitions
  if ( Dstr(1:15) .eq. '#FPMDOCUINCLUDE' ) then
     Str = Dstr(1:lenDstr)
     lenStr = lenDstr
     
     write(*,'(a)') 'StrContainingFPMDOCUINCLUDE = >>>' // Str(1:lenStr) // '<<<' 
     if ( Str(16:16) .eq. '{' ) then
        iOPEN_beg = 17
        iOPEN_end = index(Str(17:lenStr),'}')-1+17-1
        if ( iOPEN_end .lt. iOPEN_beg ) then
           write(*,*) 'ERROR 1 in #FPMDOCUINCLUDE{OPENclause}{CLOSEclause}'
           stop
        end if
        strOPEN = Str(iOPEN_beg:iOPEN_end)
        len_strOPEN = iOPEN_end-iOPEN_beg + 1
        
        if ( Str(iOPEN_end+2:iOPEN_end+2) .ne. '{' ) then
           write(*,*) 'ERROR 2 in #FPMDOCUINCLUDE{OPENclause}{CLOSEclause}'
           stop
        end if
        iCLOSE_beg = iOPEN_end+3
        iCLOSE_end = index(Str(iCLOSE_beg:lenStr),'}')-1 + iCLOSE_beg - 1
        if ( iCLOSE_end .lt. iCLOSE_beg ) then
           write(*,*) 'ERROR 3 in #FPMDOCUINCLUDE{OPENclause}{CLOSEclause}'
           stop
        end if
        strCLOSE = Str(iCLOSE_beg:iCLOSE_end)
        len_strCLOSE = iCLOSE_end-iCLOSE_beg + 1
        
        iStartFile = iCLOSE_end + 2
     else
        len_strOPEN = 0
        len_strCLOSE = 0
        iStartFile = 16
     end if

     FileStr = Str(iStartFile:lenStr)
     lenFileStr = lenStr-iStartFile + 1
     call RemoveLeadingSpaces(FileStr, lenFileStr)
     if ( (FileStr(1:1) .eq. '"') .or. (FileStr(1:1) .eq. "'") ) then  ! remove leading and tailing quotas
        FileStr = FileStr(2:lenFileStr-1)
        lenFileStr = lenFileStr - 1
     end if
     inquire( file=FileStr(1:lenFileStr), exist=lExist )
     if ( lExist ) then  ! if the file exists, open in special unit and go on reading the new file
        iFileHierarchy = iFileHierarchy + 1
        UN(iFileHierarchy) = UN(iFileHierarchy-1) + 1
        open( unit=UN(iFileHierarchy), file=FileStr(1:lenFileStr), status='UNKNOWN' )

        if ( len_strOPEN .gt. 0 ) then
           lOPEN(iFileHierarchy) = .false.  ! valid lines only if strOPEN is found in file
           Llen_strOPEN(iFileHierarchy) = len_strOPEN
           Llen_strCLOSE(iFileHierarchy) = len_strCLOSE
           LstrOPEN(iFileHierarchy) = strOPEN
           LstrCLOSE(iFileHierarchy) = strCLOSE
        else
           lOPEN(iFileHierarchy) = .true. ! read the next line in the file
           Llen_strOPEN(iFileHierarchy) = 0
           Llen_strCLOSE(iFileHierarchy) = 0
        end if
        
        cycle  ! go on reading the include file
     else ! include file does not exist -> expell warning in the html text
        Str = Str(1:lenStr) // ' ------------> WARNING: this include file did not exist at the time the present FPMDOCU was compiled'
        lenStr = len_trimf77(Str,1024)
     end if
  end if
  

  
  
  
  
  
  
  
  if ( lenStr .le. 0 ) then  ! be able to also print empty lines in case we are in a block
     Str = ' '
     lenStr = 1
  end if


  ! check for hierarchy defintions
  do
     !ih_beg = index( Str(1:lenStr), '#h' )
     call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#h', i2, ih_beg )
     if ( ih_beg .gt. 0 ) then
        !ih_end = index( Str(ih_beg:lenStr), 'h#' )
        call IndexInActivePartOfString( Str(ih_beg:lenStr), lenStr-ih_beg+1, Dashes, i2, 'h#', i2, ih_end )
        if ( ih_end .gt. 0 ) then
           isInsideBlock = .false. ! defintion of a #h...h#-environment neutralizes a previous block command (#b)

           PreviousElement%Pointer => CurrentElement(1)%Pointer

           Dstr = Str(ih_beg+2:ih_beg+ih_end-1)
           lenDstr = ih_end-1-2
           call RemoveLeadingSpaces(DStr, lenDStr)

           lenDstrAll = lenDstr
           nbCurrentElement = 0
           ! now check, if two or more hierarchy items are named
           do
              nbCurrentElement = nbCurrentElement + 1
              if ( nbCurrentElement .gt. NCurrentElement ) then
                 write(*,*) 
                 write(*,*) 'ERROR in main_FPMDOCU.f90!!!!!!!!!!!!!!!'
                 write(*,*) 'number of allowed hierarchy names for one block exceeded'
                 write(*,*) 'nbCurrentElement, NCurrentElement = ', nbCurrentElement, NCurrentElement
                 stop
              end if
              call IndexInActivePartOfString( DStr, lenDStrAll, Dashes, i2, '||', i2, ih_DD )
              if ( ih_DD .gt. 0 ) then
                 lenDstr = ih_DD-1
              else
                 lenDstr = lenDstrAll
              end if

              if ( Dstr(1:2) .eq. '..' ) then ! given a relative hierarchy as attachment on the current tree leaf
                 NameStr = PreviousElement%Pointer%Name(1:PreviousElement%Pointer%lenName) // Dstr(2:lenDstr)
                 lenNameStr = PreviousElement%Pointer%lenName + lenDstr-1
                 call FPMDOCU_CollectHierarchyElement( PreviousElement, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
              elseif ( Dstr(1:1) .eq. '.' ) then ! given a relative hierarchy as a new child in the same hierarchy level
                 NameStr = Dstr(2:lenDstr)
                 lenNameStr = lenDstr-1
                 call FPMDOCU_CollectHierarchyElement( PreviousElement, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
              else
                 NameStr = Dstr(1:lenDstr)
                 lenNameStr = lenDstr
                 call FPMDOCU_CollectHierarchyElement( Root, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
              end if

              ! check if there is a directory with examples for this item
              lenCompleteName = 1024
              call FPMDOCU_ReconstructCompleteName( CurrentElement(nbCurrentElement), CompleteName, lenCompleteName )
              inquire( directory='../OnlineExamples/'//CompleteName(1:lenCompleteName), exist=Lex )
              if ( Lex ) then
                 CurrentElement(nbCurrentElement)%Pointer%SimpleSimulationExampleGiven = .true.
              end if

              if ( ih_DD .le. 0 ) then ! there was no additional hierarchy name
                 exit
              else ! if additional hierarchy name
                 Dstr(1:ih_DD+1) = ' '
                 call RemoveLeadingSpaces(DStr, lenDStrAll)
              end if
           end do

           Str(ih_beg:ih_beg+ih_end+1) = ' '   ! clean the #h ... h# part in the string
        else
           write(*,*)
           write(*,*)
           write(*,'(a)') 'missing h# in line: >>>' // Orig(1:lenOrig) // '<<<'
           write(*,*) 'FPMDOCU FAILED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
           stop
        end if
     else
        exit
     end if
  end do

  ! check for alias definitions
  do
     !ih_beg = index( Str(1:lenStr), '#a' )
     call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#a', i2, ih_beg )
     if ( ih_beg .gt. 0 ) then
        !ih_end = index( Str(ih_beg:lenStr), 'a#' )
        call IndexInActivePartOfString( Str(ih_beg:lenStr), lenStr-ih_beg+1, Dashes, i2, 'a#', i2, ih_end )
        if ( ih_end .gt. 0 ) then
           isInsideBlock = .false. ! defintion of a #a...a#-environment neutralizes a previous block command (#b)
           Dstr = Str(ih_beg+2:ih_beg+ih_end-1)
           lenDstr = ih_end-1-2
           do i = 1,nbCurrentElement
              call FPMDOCU_SetAlias( CurrentElement(i), DStr, lenDStr )
           end do
           Str(ih_beg:ih_beg+ih_end+1) = ' '
        else
           write(*,*)
           write(*,*)
           write(*,'(a)') 'missing a# in line: >>>' // Orig(1:lenOrig) // '<<<'
           write(*,*) 'FPMDOCU FAILED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
           stop
        end if
     else
        exit
     end if
  end do

  ! check for text
  do
     !ih_beg = index( Str(1:lenStr), '#t' )
     call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#t', i2, ih_beg )
     if ( ih_beg .gt. 0 ) then
        !ih_end = index( Str(ih_beg:lenStr), 't#' )
        call IndexInActivePartOfString( Str(ih_beg:lenStr), lenStr-ih_beg+1, Dashes, i2, 't#', i2, ih_end )
        if ( ih_end .gt. 0 ) then
           Dstr = Str(ih_beg+2:ih_beg+ih_end-1)
           lenDstr = ih_end-1-2
           do i = 1,nbCurrentElement
              call FPMDOCU_AddText( CurrentElement(i), DStr, lenDStr )
           end do
           Str(ih_beg:ih_beg+ih_end+1) = ' '
        else
           write(*,*)
           write(*,*)
           write(*,'(a)') 'missing t# in line: >>>' // Orig(1:lenOrig) // '<<<'
           write(*,*) 'FPMDOCU FAILED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
           stop
        end if
     else
        exit
     end if
  end do

  ! check if links have to be computed for this item
  call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#link', i2, ih_beg )
  if ( ih_beg .gt. 0 ) then
     Str(ih_beg:ih_beg+4) = ' '
     do i = 1,nbCurrentElement
        CurrentElement(i)%Pointer%SearchForLinksInOtherPages = .true.
     end do
  end if
  
  ! check if links have to be computed for this item
  call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#sort', i2, ih_beg )
  if ( ih_beg .gt. 0 ) then
     Str(ih_beg:ih_beg+4) = ' '
     do i = 1,nbCurrentElement
        CurrentElement(i)%Pointer%SortChildrenLexicographically = .true.
     end do
  end if
  

  

  call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#b', 2, ih_beg )
  if ( ih_beg .gt. 0 ) then
    !check for valid #b tag
    !for valid #b tag it should followed by 
    !empty string or new line character or space character
    if ( (Str(ih_beg+2:ih_beg+2) .eq. '') .or. &
	  (Str(ih_beg+2:ih_beg+2) .eq. achar(10)) .or. &
	  (Str(ih_beg+2:ih_beg+2) .eq. achar(13)) .or. &
	  (Str(ih_beg+2:ih_beg+2) .eq. achar(32)) ) then
         Dstr = Str(ih_beg+2:lenStr)
         ! if b# is present in the same line
         if(index(Dstr, 'b#') .ge. 1) then
            Dstr=Dstr(1:index(Dstr, 'b#')-1)
            lenDstr = lenStr-5
         else 
            lenDstr = lenStr-3
         end if
         do i = 1,nbCurrentElement
            call FPMDOCU_AddText( CurrentElement(i), DStr, lenDStr )
         end do
         Str(1:ih_beg+1) = ' '
	      isInsideBlock = .true.
	      cycle
    end if
  end if

  isEndOfBlockWithValidLine = .false.
  call IndexInActivePartOfString( Str, lenStr, Dashes, i2, 'b#', i2, ih_end )
  if ( ih_end .gt. 0 ) then
     Lvalid = (ih_end .eq. 1)
     if (ih_end .gt. 1) then
        Lvalid = Lvalid .or. (Str(ih_end-1:ih_end-1) .eq. '')
        Lvalid = Lvalid .or. (Str(ih_end-1:ih_end-1) .eq. achar(32))
    end if
    !check for valid b# tag
    !for valid b# tag, it should come after 
    !empty string or space or it should be the first character of the line
    if ( Lvalid ) then
	  Str(ih_end:lenStr) = ' '
	  isInsideBlock = .false.
	  lenStr = len_trimf77( Str, lenStr )
	  if ( lenStr .gt. 0 ) then
	      isEndOfBlockWithValidLine = .true.    ! line of the form ...!$FPMDOCU plaplub b#
	  else
	      cycle                                ! line of the form ...!$FPMDOCU b#
	  end if
    end if
  end if

  ! check if line begins and ends with " or ', if so, delete leading spaces and " or '
  if ( isInsideBlock .or. isEndOfBlockWithValidLine ) then
     DStr = Str(1:lenStr)
     lenDStr = lenStr
     call RemoveLeadingSpaces( DStr, lenDStr )
     lenDStr = len_trimf77(DStr, lenDStr) ! remove spaces at the end
     if ( lenDStr .gt. 0 ) then  ! check if the string is enclosed by dashes
        if ( ( (DStr(1:1) .eq. '"') .and. (DStr(lenDStr:lenDStr) .eq. '"') ) ) then
           DStr = DStr(2:lenDStr-1)
           lenDStr = lenDStr - 2
           if ( index(DStr(1:lenDStr), '"') .le. 0 ) then ! if in the reduced string still appear ' or ", then do not reduce the line
                                                          ! especiall try to avoid the situation "alias" = "plaplapla " -> alias" = "plaplapla
              Str = DStr(1:lenDStr)
              lenStr = lenDStr 
           end if
        elseif ( ( (DStr(1:1) .eq. "'") .and. (DStr(lenDStr:lenDStr) .eq. "'") ) ) then
           DStr = DStr(2:lenDStr-1)
           lenDStr = lenDStr - 2
           if ( index(DStr(1:lenDStr), "'") .le. 0 ) then ! if in the reduced string still appear ' or ", then do not reduce the line
                                                          ! especiall try to avoid the situation "alias" = "plaplapla " -> alias" = "plaplapla
              Str = DStr(1:lenDStr)
              lenStr = lenDStr 
           end if
        elseif ( ( (DStr(1:1) .eq. "@") .and. (DStr(lenDStr:lenDStr) .eq. "@") ) ) then
           DStr = DStr(2:lenDStr-1)
           lenDStr = lenDStr - 2
           Str = DStr(1:lenDStr)
           lenStr = lenDStr 
        end if

     end if
     do i = 1,nbCurrentElement
        call FPMDOCU_AddText( CurrentElement(i), Str, lenStr )
     end do
  end if


  do i = 1,nbCurrentElement
     if ( associated(CurrentElement(i)%Pointer) ) then
        call FPMDOCU_SetSourceFile( CurrentElement(i), FileName, lenFileName, FileNameLineNumber )
     end if
  end do
  
  cycle
  
90 continue
  close(unit=UN(iFileHierarchy))
  iFileHierarchy = iFileHierarchy - 1
  if ( iFileHierarchy .lt. 1 ) then
     exit   ! if end-of-file at the lowest hierarchy level, the whole reading is done
  else
     cycle ! go on reading file on the lower hierarchy level
  end if
  
end do



!-------------------------------------------- If Separate Index file is given then create secondary root--------------------------------------
if(isIndexFileExist) then
    SecondaryRoot%Pointer => NULL()
    SecondaryRootIndex%Pointer => NULL()
    do i = 1,NCurrentElement
      CurrentElement(i)%Pointer => NULL()
    end do

    iFileHierarchy = 1
    UN(iFileHierarchy) = 21
    open( unit=UN(iFileHierarchy), file=IndexFileName(1:lenIndexFileName), status='UNKNOWN' )
    Str = ' '


  do
    read(UN(iFileHierarchy),'(a)',end=91) Str
    lenStr = len_trimf77(Str,1024)

    Orig(1:lenStr) = Str(1:lenStr)
    lenOrig = lenStr
    

  ! first extract the name of the source file and the line number. The file name is always at the beginning of the line, followed by a ':', then the line number, followed by another ':'
  ! however, do this only on the lowest hierarchy level, as these lines stem from a grep and therefore contain file information.
    if ( iFileHierarchy .eq. 1 ) then  
      i = index( Str(1:lenStr),':' )
      FileName = Str(1:i-1)
      lenFileName = i-1
      Str(1:i) = ' '
      call RemoveLeadingSpaces(Str, lenStr)


      i = index( Str(1:lenStr),':' )
      read(Str(1:i-1),*) FileNameLineNumber
      Str(1:i) = ' '
      call RemoveLeadingSpaces(Str, lenStr)
    end if
    
    !call RemoveLeadingSpaces(Str, lenStr)   !  just to cleanup
    
  ! check include file definitions
    if ( Str(1:15) .eq. '#FPMDOCUINCLUDE' ) then
      FileStr = Str(16:lenStr)
      lenFileStr = lenStr-15
      call RemoveLeadingSpaces(FileStr, lenFileStr)
      if ( (FileStr(1:1) .eq. '"') .or. (FileStr(1:1) .eq. "'") ) then  ! remove leading and tailing quotas
	      FileStr = FileStr(2:lenFileStr-1)
	      lenFileStr = lenFileStr - 1
      end if
      inquire( file=FileStr(1:lenFileStr), exist=lExist )
      if ( lExist ) then  ! if the file exists, open in special unit and go on reading the new file
	      iFileHierarchy = iFileHierarchy + 1
	      UN(iFileHierarchy) = UN(iFileHierarchy-1) + 1
	      open( unit=UN(iFileHierarchy), file=FileStr(1:lenFileStr), status='UNKNOWN' )
	      cycle  ! go on reading the include file
      else ! include file does not exist -> expell warning in the html text
	      Str = Str(1:lenStr) // ' ------------> WARNING: this include file did not exist at the time the present FPMDOCU was compiled'
	      lenStr = len_trimf77(Str,1024)
      end if
    end if
    


  ! now serach for occurence of !$FPMDOCU
    iFPMDOCU = index( Str(1:lenStr),'!$FPMDOCU' )
    if ( iFPMDOCU .le. 0 ) then  ! if no !$FPMDOCU is in the line, we assume that the line stems from a .fpmdocu file where all !$FPMDOCU are dropped or we have !$FPMINTDOCU
      iFPMDOCU = index( Str(1:lenStr),'!$FPMINTDOCU' )
      if ( iFPMDOCU .le. 0 ) then
	    Str = Str(1:lenStr)
	    lenStr = len_trimf77(Str,1024)
      else
       if (UsersOnly .gt. 0) cycle !remove FPMINTDOCU lines from .fpmdocu files
	    Str = Str(iFPMDOCU+12:lenStr)
	    lenStr = len_trimf77(Str,1024)
      end if
    else
      Str = Str(iFPMDOCU+9:lenStr)
      lenStr = len_trimf77(Str,1024)
    end if
  !  call RemoveLeadingSpaces(Str, lenStr)
    write(*,'(a)') 'read: Str = >>>' // Str(1:lenStr) // '<<<'

    if ( lenStr .le. 0 ) then  ! be able to also print empty lines in case we are in a block
      Str = ' '
      lenStr = 1
    end if


    ! check for hierarchy defintions
    do
      !ih_beg = index( Str(1:lenStr), '#h' )
      call IndexInActivePartOfString( Str, lenStr, Dashes, i2, '#h', i2, ih_beg )
      if ( ih_beg .gt. 0 ) then
	  call IndexInActivePartOfString( Str(ih_beg:lenStr), lenStr-ih_beg+1, Dashes, i2, 'h#', i2, ih_end )
	  if ( ih_end .gt. 0 ) then
	    isInsideBlock = .false. ! defintion of a #h...h#-environment neutralizes a previous block command (#b)

	    PreviousElement%Pointer => CurrentElement(1)%Pointer

	    Dstr = Str(ih_beg+2:ih_beg+ih_end-1)
	    lenDstr = ih_end-1-2
	    call RemoveLeadingSpaces(DStr, lenDStr)

	    lenDstrAll = lenDstr
	    nbCurrentElement = 0
	    ! now check, if two or more hierarchy items are named
	    do
		nbCurrentElement = nbCurrentElement + 1
		if ( nbCurrentElement .gt. NCurrentElement ) then
		  write(*,*) 
		  write(*,*) 'ERROR in main_FPMDOCU.f90!!!!!!!!!!!!!!!'
		  write(*,*) 'number of allowed hierarchy names for one block exceeded'
		  write(*,*) 'nbCurrentElement, NCurrentElement = ', nbCurrentElement, NCurrentElement
		  stop
		end if
		call IndexInActivePartOfString( DStr, lenDStrAll, Dashes, i2, '||', i2, ih_DD )
		if ( ih_DD .gt. 0 ) then
		  lenDstr = ih_DD-1
		else
		  lenDstr = lenDstrAll
		end if

		if ( Dstr(1:2) .eq. '..' ) then ! given a relative hierarchy as attachment on the current tree leaf
		  NameStr = PreviousElement%Pointer%Name(1:PreviousElement%Pointer%lenName) // Dstr(2:lenDstr)
		  lenNameStr = PreviousElement%Pointer%lenName + lenDstr-1
		  call FPMDOCU_CollectHierarchyElement( PreviousElement, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
		elseif ( Dstr(1:1) .eq. '.' ) then ! given a relative hierarchy as a new child in the same hierarchy level
		  NameStr = Dstr(2:lenDstr)
		  lenNameStr = lenDstr-1
		  call FPMDOCU_CollectHierarchyElement( PreviousElement, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
		else
		  NameStr = Dstr(1:lenDstr)
		  lenNameStr = lenDstr
		  call FPMDOCU_CollectHierarchyElement( SecondaryRoot, NameStr, lenNameStr, CurrentElement(nbCurrentElement) )
		end if

		! check if there is a directory with examples for this item
		lenCompleteName = 1024
		call FPMDOCU_ReconstructCompleteName( CurrentElement(nbCurrentElement), CompleteName, lenCompleteName )
		inquire( directory='./OnlineExamples/'//CompleteName(1:lenCompleteName), exist=Lex )
		if ( Lex ) then
		  CurrentElement(nbCurrentElement)%Pointer%SimpleSimulationExampleGiven = .true.
		end if

		if ( ih_DD .le. 0 ) then ! there was no additional hierarchy name
		  exit
		else ! if additional hierarchy name
		  Dstr(1:ih_DD+1) = ' '
		  call RemoveLeadingSpaces(DStr, lenDStrAll)
		end if
	    end do

	    Str(ih_beg:ih_beg+ih_end+1) = ' '   ! clean the #h ... h# part in the string
	  else
	    write(*,*)
	    write(*,*)
	    write(*,'(a)') 'missing h# in line: >>>' // Orig(1:lenOrig) // '<<<'
	    write(*,*) 'FPMDOCU FAILED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	    stop
	  end if
      else
	  exit
      end if
    end do



    do i = 1,nbCurrentElement
      if ( associated(CurrentElement(i)%Pointer) ) then
	  call FPMDOCU_SetSourceFile( CurrentElement(i), FileName, lenFileName, FileNameLineNumber )
      end if
    end do
    
    cycle
    
  91 continue
    close(unit=UN(iFileHierarchy))
    iFileHierarchy = iFileHierarchy - 1
    if ( iFileHierarchy .lt. 1 ) then
      exit   ! if end-of-file at the lowest hierarchy level, the whole reading is done
    else
      cycle ! go on reading file on the lower hierarchy level
    end if
    
  end do
  ! if separate index file is present generate RootIndex out of SecondaryRoot generated from given index file
  call FPMDOCU_EstablishIndexTable( SecondaryRoot, RootIndex, 0 )
else
!-------------------------------------------- separate index generation ends---------------------------------------------

  ! if separate index file is not present generate RootIndex out of main Root generated from source file
  call FPMDOCU_EstablishIndexTable( Root, RootIndex, 0 )
  !call FPMDOCU_MakeUpIndexTable( RootIndex, 0 )
end if

UNAIO=0
iFirst=0
UsersOnly=0

call GET_COMMAND(LENGTH = len, STATUS = iStat)
if ( (iStat .le. 0) .and. (len .gt. 0) ) then

   ! and check if we can actually read them
   allocate(character(len) :: full_command_line)
   call GET_COMMAND(COMMAND=full_command_line, STATUS=iStat)
   if ( iStat .eq. 0 ) then
      if ( index(full_command_line,'--ProduceAllInOneFile') .gt. 0 ) then
         UNAIO = 20
         iFirst = 1
      end if
      if ( index(full_command_line,'--ForUsersOnly') .gt. 0 ) then
         UsersOnly = 1
      end if
   end if
   deallocate(full_command_line)
end if

if ( UNAIO .gt. 0 ) then
   open( unit=UNAIO, file='MESHFREEdocu_AllInOne.html', status='UNKNOWN', buffered='YES', buffercount=1, blocksize=1048576 )
   write(UNAIO,'(a)') '<!doctype html>'
   write(UNAIO,'(a)') '<html>'
end if




#if defined NO_CD
call FPMDOCU_ExportHTML_NoCD( Root, 1, UNAIO, iFirst, UsersOnly, SourceFileName, lenSourceFileName )
call FPMDOCU_ExportHTML_NoCD( RootIndex, 1, UNAIO, iFirst, UsersOnly, SourceFileName, lenSourceFileName )
#else
call FPMDOCU_ExportHTML( Root, 1, UNAIO, iFirst, UsersOnly, SourceFileName, lenSourceFileName )
call FPMDOCU_ExportHTML( RootIndex, 1, UNAIO, iFirst, UsersOnly, SourceFileName, lenSourceFileName )
#endif

if ( UNAIO .gt. 0 ) then
   write(UNAIO,'(a)') '</div>';                                           
   write(UNAIO,'(a)') '</body>';                                             
   write(UNAIO,'(a)') '</html>'
   close(unit=UNAIO)
end if
!  call FPMDOCU_CollectHierarchyElement( Str, lenStr )

end




subroutine amfpmj_finalize() ! dummy function as not needed but linked in by FPM_exit()
write(*,*) 'amfpmj_finalize'
end
