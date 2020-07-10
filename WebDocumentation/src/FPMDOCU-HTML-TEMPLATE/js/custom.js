//check size of the window when the it loads for first time
/*
$(window).load(function() {
  var screenSize = $(window).width();
 if (screenSize > 900) {
    $('#main-menu-top').hide();
    $('#main-menu-bottom').show();
 }
 else {
    $('#main-menu-top').show();
    $('#main-menu-bottom').hide();
 }
});


//whenever change in window size check current size
$(window).resize(function(){
 var screenSize = $(window).width();
 if (screenSize > 900) {
    $('#main-menu-top').hide();
    $('#main-menu-bottom').show();
 }
 else {
    $('#main-menu-top').show();
    $('#main-menu-bottom').hide();
 }
}); 

*/


//------------------------- Search page
//whenever search icon is clicked, display search text box
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

//----------------------------- Index Page
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

//-------if search form is submitted in the index page redirect it to search page 
//------- search key word
$(document).ready(function() {
	$('#search-form-index-header').submit(function(event) {
	event.preventDefault();
	//redirect it to search-page.html with search_term
	window.location.href = "search-page.html?search_term="+$("#search-text-index-header").val();
	});
});

$(document).ready(function() {
	$('#search-form-index-top').submit(function(event) {
	event.preventDefault();
	//redirect it to search-page.html with search_term
	window.location.href = "search-page.html?search_term="+$("#search-text-index-top").val();
	});
});

//-------------------------------- Index Page ends


//-----------------function to display menu when the user clicks the expand button in small screen
$( function()
{
    $("#nav-top").click(function(){
	$(".navbar-toggle").click();
	        
    })
} );

//----------------- function to remove first blank line inside frame --------------------------
//----------------- css property 'white-space:pre-line;' creates a blank line for a first line
//----------------- to remove this we trim blank space
  $( document ).ready(function() {
    $(document.body).find(".note").each(function() {
      $(this).html($.trim($(this).html()));
    });
  });


