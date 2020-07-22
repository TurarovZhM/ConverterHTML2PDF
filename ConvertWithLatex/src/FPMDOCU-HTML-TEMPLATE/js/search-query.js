/* 
this file handles all the javascript part of the search
Whenever user presses search button this file does
following operations:

  1.	When searched for pharses
		1.1.	Search the whole text in generated index directly without using lunr
  2.	Else search for every possible combination of given input
		2.1. 	Lunr plugin loads index file(web.json file) which contains all the 
			contents  of html pages.
		2.2. 	Lunr uses title and body part present in the loaded json file to make  the index for the searching. 
		2.3.	Given searched term is divided into individual words and every possible combination is generated from
			these words. 
		2.4.	Individual combination is searched in generated index.
		2.5.	Search result from every combination of words is combined and duplicate resuls are removed
  3. 	Generated result is tailored to display only portions which contains searched terms.
  4. 	For highlighting the searched term we use jquery.mark.js file





*/ 
$(document).ready(function() {
	// this function is called whenever user presses submit button
	$('#search-form').submit(function(event) {
		event.preventDefault()
		$(".search-results").empty()

		var search_term = $('#search').val();
		var search_results = [];
		var phrase_search = false;
		var queryTokens = [];

		//if quote is present in given input(search_term)
		//	then don't split the search_term
		//else 
		//	split input string based on space and search with individual words
		//	combine search result from all the individual word into a single array of resul			
		if(search_term.indexOf('"')>=0 && search_term.indexOf('"')!=search_term.lastIndexOf('"')){
			search_term = search_term.trim().replace(/"/g,"");
			queryTokens.push(search_term)
			for(var i=0; i<data.length; i++) {
				var obj = data[i];
				if(obj.body.toLowerCase().indexOf(search_term.toLowerCase())>-1){
					search_results.push(obj);
				}
			}
			displaySearchResult(search_term,search_results,queryTokens)
		}
		else
		{

			//define the lunr index type
			var index = lunr(function () {
				this.field('title', {boost: 10})
				this.field('body')
				this.ref('id')
			});

			// create lunr index by loading contents of html files present
			// in json file as a 'data' variable
			$.each( data, function( i,item) {
				index.add(item);
			  });

			// split given input based on space
			var individual_search_terms = search_term.split(" ")

			
			// generate every possible combination from splited words
			var combination_of_terms = generate_combination_of_words(individual_search_terms)

			// for every combination of words, search it in lunr index
			for(var i=0; i<combination_of_terms.length; i++) {
				individual_term_search_results = index.search(combination_of_terms[i])
				//combining search result
				for(var j=0; j<individual_term_search_results.length; j++)
				{
					search_results.push(individual_term_search_results[j])
				}				
			}
			//filtering only unique documents
			search_results = arrayUnique(search_results)

			// add the title and body of each page into each result, too (this doesn't come with standard with lunr.js)
			// lunr will only return ref which is id of the document and searching score,
			// so to display title and content of the search result we need to extract it from 
			// json file explicitly by comparing id of the searched result with the id in the json file
			for(var result in search_results) {
				search_results[result].title = data.filter(function(post) {
					return post.id === search_results[result].ref;
				})[0].title;
				search_results[result].body = data.filter(function(post) {
					return post.id === search_results[result].ref;
				})[0].body;
				search_results[result].url = data.filter(function(post) {
					return post.id === search_results[result].ref;
				})[0].url;
			}
			
			//extract tokesns used by lunr for highlighting matched terms
			queryTokens = lunr.tokenizer(search_term)
			
			//display search result
			displaySearchResult(search_term, search_results, queryTokens)
		}
		//select the content and set focus on main text box
		$('#search').focus();
	});
});


/*
** method to display search result
**@search_term - search input given by the user
**@search_results - list of documents that are matched with the given search input
**@tokesn - terms that are used to find matched documents
*/
function displaySearchResult(search_term, search_results, tokens){
	$results = $('.search-results')
	// If there is no matching words in any documents then display search not match result
	if(search_results.length===0){
	   $results.append('<div class="blank-class-outer-bottom">'
				+'<div class="blank-class-inner">'
				    +'<div class="row">'
					    +'<div class="col-md-12">'
						  +'<h4>Your search "' + search_term + '" did not match any documents</h4>'
					    +'</div>'
				    +'</div>'
				+'</div>'							
			  +'</div>');
	}else{
		//display the title and contents of the searched result
		$.each(search_results, function(i,result) {
			var string_to_display = trimPageContent(tokens,result.body);
			    $results.append('<div class="blank-class-outer-bottom">' 
						+'<div class="blank-class-inner">'
						    +'<div class="row">'
							    +'<div class="col-md-12">'
									    +'<h4><a href="'+ result.url +'">'+result.title+'</a></h4><p>'+string_to_display+'</p>'
							    +'</div>'
						    +'</div>'
						+'</div>'							
					  +'</div>');
		});	
		
		// For highligthing the matched terms in the context
		$.each(tokens, function(index, token) {
			$(".search-results").mark(token,{"className":"lunr-match-highlight"});
		});

	}
}

/**
***trimPageContent- for displaying only parts that contain searched terms
**@tokens - terms that are used to find matched documents
**@pageBody - Full contents of html page
**/
function trimPageContent(tokens, pageBody){
	var page_body_lower_case = pageBody.toLowerCase();
	var indexList = [];
		
	for(i=0; i<tokens.length; i++){
		var index=0;
		var start_pos = 0;
		var token_lower_case = tokens[i].toLowerCase();
		var tokenLength = token_lower_case.length;
		var token_end_pos = 0;
		
		// extract position of all the occurance of searched terms and their length  
		index = page_body_lower_case.indexOf(token_lower_case,start_pos);
		while (index>-1){
			token_end_pos = index + tokenLength;
			indexList.push([index, token_end_pos]);
			start_pos = token_end_pos;		
			index = page_body_lower_case.indexOf(token_lower_case,start_pos);
		}
	}
	// sort them based on position
	indexList.sort(sortFunction);
	

	
	// display 80 characters before and after position of the matched terms
	// if next matched terms occurs within following 80 characters then, 
	//	display these two terms without dividing in between and entail 80 more charcters after second matched term
	var index = 0;
	var token_end_pos = 0;
	var text_display_list = []
	var length_of_page_body = pageBody.length;
	var display_start_pos = 0;
	var display_end_pos = 0;
	var text_display_list_length = 0;
	for(i=0; i<indexList.length; i++){
		index = indexList[i][0];
		token_end_pos = indexList[i][1]
		display_start_pos = index - 80;
		display_start_pos = display_start_pos<0?0:display_start_pos;
		display_end_pos = token_end_pos + 80;
		display_end_pos = display_end_pos>length_of_page_body?length_of_page_body:display_end_pos;
		
		text_display_list_length = text_display_list.length
		if(text_display_list_length==0)
			text_display_list.push([index,display_start_pos,display_end_pos])
		else if(text_display_list[text_display_list_length-1][2]>= display_start_pos)
			text_display_list[text_display_list_length-1][2] = display_end_pos;
		else
			text_display_list.push([index, display_start_pos, display_end_pos]);
	}
	
	var string_to_display = "";
	var individual_string = "";
	for (i=0; i<text_display_list.length; i++){
		individual_string = pageBody.substring(text_display_list[i][1], text_display_list[i][2])
		//If the searched word is at the beginning of the page, then only trip space at the end of substring
		//Else trim space at both sides of substring
		//re-trim if string is in middle of a word
		if(text_display_list[i][1]==0){
		  individual_string = individual_string.substring(0, individual_string.lastIndexOf(" "));
		  string_to_display = string_to_display + individual_string + "<b>. . .</b>  ";
		}else{
		  individual_string = individual_string.substring(individual_string.indexOf(" "), individual_string.lastIndexOf(" "));
		  string_to_display = "<b> ...</b>" + string_to_display + individual_string + "<b>. . .</b>  ";
		}
		
		
		
		
	}
	
	return string_to_display;
	
}

/**
** custom function to sorting two dimensional array
**/
function sortFunction(a, b) {
    if (a[0] === b[0]) {
        return 0;
    }
    else {
        return (a[0] < b[0]) ? -1 : 1;
    }
}


// filter array having unique ref id
function arrayUnique(combined_search_results) {

    for(var i=0; i<combined_search_results.length; i++) {
        for(var j=i+1; j<combined_search_results.length; j++) {
            if(combined_search_results[i]["ref"] === combined_search_results[j]["ref"]){
                combined_search_results.splice(j, 1);
		j--
	    }
        }
    }

    return combined_search_results;
}



// for generating combination of words
function generate_combination_of_words(individual_search_terms) {
  var number_of_words = individual_search_terms.length

  // total number of possible combination
  var total_possible_combination = number_of_possible_combination_calculation(number_of_words)
  var combination_of_words = []

  for(var i=0; i<total_possible_combination; i++)
  {
    var combined_word = ""
    //for each combination check if each bit is set
    for(var j =0; j<total_possible_combination; j++)
    {
      // if j is set in i
      if(Math.pow(2,j) & i)
		combined_word = combined_word.concat(individual_search_terms[j]," ")
    }
	  if(combined_word.length>0){
		combined_word = combined_word.replace(/\s+$/, '')
		combination_of_words.push(combined_word)
	  }
  }
	//sorting array of words based on their length
	for(var i =0; i<combination_of_words.length-1; i++){
		for(var j=i+1; j<combination_of_words.length; j++){
			if(combination_of_words[i].length<combination_of_words[j].length){
				var temp = combination_of_words[i]
				combination_of_words[i] = combination_of_words[j]
				combination_of_words[j] = temp
			}
		}
	}
	return combination_of_words  

}

//function to calculate totla number of different possible of word combination
function number_of_possible_combination_calculation(number_of_words){
	var number_of_possible_combination= 0;
	for(var i = number_of_words; i>=0; i--){
		//C(n,r) = n! / ( r! (n - r)! )
		var combination = factorial(number_of_words)/(factorial(i)*factorial(number_of_words-i))
		number_of_possible_combination = number_of_possible_combination + combination
	}
	return number_of_possible_combination
}

//function to calcualte factorial 
function factorial(n) {
  if (n === 0) {
    return 1;
  }

  // This is it! Recursion!!
  return n * factorial(n - 1);
}
	

//select text within textbox whenever main searhcbox is in focus

$(document).ready(function() {
	$('#search').focus(function() { $(this).select(); } );
});
	
	
	
	
//There are three search forms in the page
//First one is in the middle of the page which is the main search form,
//Second one is in the header of the page, which is only visible on large screen size
//Third one is also in the header of the page, which is only visible on small screen size
//Whenever the search form on the header is submitted, take the search input and 
//give it to the main search page
$(document).ready(function() {
	$('#search-form-header').submit(function(event) {
	event.preventDefault();
	$('#search').val($('#search-text-header').val());
	$('#search-form').submit();
	});
});

$(document).ready(function() {
	$('#search-form-top').submit(function(event) {
	event.preventDefault();
	$('#search').val($('#search-text-top').val());
	$('#search-form').submit();
	});
});


/*----------------Get Url Parameter ---------------------- 
 Function to get parameter value from URL
 */
function getParameterByName(name, url) {
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

/* Fuction to read url on page load */
$(document).ready(function() {
  var search_term = getParameterByName('search_term');
    if(!search_term){}
    else{
      $('#search').val(search_term);
      $('#search-form').submit();
    }
});


