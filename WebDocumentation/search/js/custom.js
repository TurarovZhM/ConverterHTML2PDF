//------------------------- Search page-----------------------------------
//whenever search icon is clicked, display search text box
//There are two search icons, 
//one for small screen which is #search-btn-top-icon
//one for large screen which is #search-btn-header

//search button click function for large screen
$( function()
{
    $("#search-btn-header").click(function(){
	if($("#search-text-header").val()===""){
	    $("#search-text-header").slideToggle();
	    $("#search-text-header").focus();
	    return false;
	}
        
    })
} );


//search button click function for small screen
$( function()
{
    $("#search-btn-top-icon").click(function(){
	if($("#search-text-top").val()===""){
	    $("#search-text-top").slideToggle();
	    $("#search-text-top").focus();
	    return false;
	}
	else{
	    $("#search-form-top").submit();
	}
        
    })
} );


//-------------------------Search Page ends

//----------------------------- Index Page--------------------------------------
//whenever search icon is clicked, display search text box
//As in search page, there are also two search icons in index page, 
//one for small screen which is #search-btn-top-icon
//one for large screen which is #search-btn-header

//search button click function for large screen
$( function()
{
    $("#search-btn-index-header").click(function(){
	if($("#search-text-index-header").val()===""){
	    $("#search-text-index-header").slideToggle();
	    $("#search-text-index-header").focus();
	    return false;
	}
        
    })
} );


//search button click function for small screen
$( function()
{
    $("#search-btn-index-top-icon").click(function(){
	if($("#search-text-index-top").val()===""){
	    $("#search-text-index-top").slideToggle();
	    $("#search-text-index-top").focus();
	    return false;
	}
	else{
	    //redirect it to search-page.html with search_term
	    window.location.href = "search-page.html?search_term="+$("#search-text-index-top").val();
	}
        
    })
} );


//function to redirect search request from index page to search page

//search request in large screen
$(document).ready(function() {
	$('#search-form-index-header').submit(function(event) {
	event.preventDefault();
	//redirect it to search-page.html with search_term
	window.location.href = "search/search.html?search_term="+$("#search-text-index-header").val();
	});
});

//search request in small screen
$(document).ready(function() {
	$('#search-form-index-top').submit(function(event) {
	event.preventDefault();
	//redirect it to search-page.html with search_term
	window.location.href = "search/search.html?search_term="+$("#search-text-index-top").val();
	});
});

//-------------------------------- Index Page ends-------------------------------------------------------------

//-----------------function to display menu when the user clicks the expand button in small screen
$( function()
{
    $("#nav-top").click(function(){
	$(".navbar-toggle").click();
	        
    })
} );


/**
**	 function to remove first blank line inside frame and UCVCODE block
** css property 'white-space:pre-line;' creates a blank line for a first line
** to remove this we trim blank space
** trim will also remove initial space used for indentatation
** to balance this, first we find out number of white spaces used for indentation 
** both in frame block and UCVCODE block and add this spaces at the beginning of the text
** There might be cases where UCVCODE block appears immediatly after frame block,
** in this case we don't need to add any spaces at the beginning of the frame block, 
** we only need to add at the beginning of the UCVCODE block
**/

$( document ).ready(function() {
    $(document.body).find(".code").each(function() {
      var str_original = $(this).html();
      var indent_white_space = get_white_space_for_indentation(str_original);
      var str_trim = $.trim($(this).html());
      $(this).html(indent_white_space + str_trim);
    });
  });
  


  $( document ).ready(function() {
    $(document.body).find(".note").each(function() {
      var str_trim = $.trim($(this).html());
      if(str_trim.substr(0,18)=='<div class="code">'){
	$(this).html(str_trim);
      }
      else{
	var str_original = $(this).html();
	var indent_white_space = get_white_space_for_indentation(str_original);
	$(this).html(indent_white_space+str_trim);
      }
     });
  });

//   $( document ).ready(function() {
//     $(document.body).find(".note").each(function() {
//       var str_trim = $.trim($(this).html());
//       if(str.substr(0,18)=='<div class="code">')
// 	$(this).html(str_trim);
//       else if(str.substr(0,9)=='!$FPMDOCU')
// 	$(this).html(" "+str_trim);
//       else
// 	$(this).html("  "+str_trim);
//      });
//   });
  
    $( document ).ready(function() {
    $(document.body).find(".description").each(function() {
      $(this).html($.trim($(this).html()));
    });
  });
  

/*----------------get suitable number of white space for indentation  ---------------------- 
 */
function get_white_space_for_indentation(str_original) {
    var str_left_trim = str_original.replace(/^\s+/,"");
    var pos_first_non_white_space = str_original.length -str_left_trim.length;
    var indent_white_space =  "";

    if(pos_first_non_white_space!=0){
      var str_white_space = str_original.substr(0,pos_first_non_white_space);
      var pos_of_last_new_line = str_white_space.lastIndexOf("\n");
      if(pos_of_last_new_line!=-1){  //if new line exists
	//To create desired number of white space
	//We have to add 1 to the desired length because the separator string goes between the array elements.
	indent_white_space = new Array(pos_first_non_white_space - (pos_of_last_new_line+1) +1).join( " " );
      }
      else
	indent_white_space = new Array(pos_first_non_white_space +1).join( " " );
    }

    return indent_white_space;
}
  
/* Function to remove empty list(<li></li>)
 * For lists(#numberedlist, #bulletlist) fortran code
 * generates first list as empty, this function remove
 * that empty list  
 */  
$( document ).ready(function() {
  $('li').each(
         function(){
             if($(this).html().trim()==''){
	       $(this).remove();	       
	    }
         }
  );
});



/*
 * Function to define max height of the UCVCODE block
 * when windows load for the first time and during 
 * resize 
 */
$(window).on("load resize", function () {
    $('.code').css('max-height', window.innerHeight * .6);
});
