$(document).ready(function() {

	// home 
	
	$("form.new_user>input#nickname").click(function() {
		if($(this).val() == 'nickname') {
			$(this).val('');
		}
	});
	$("form.new_user>input#password").click(function() {
		if($(this).val() == 'pwd') {
			$(this).val('');
		}
	});
	$("form#gotoprofile>input#username").click(function() {
		if($(this).val() == 'nick') {
			$(this).val('');
		}
	});
	
	
});