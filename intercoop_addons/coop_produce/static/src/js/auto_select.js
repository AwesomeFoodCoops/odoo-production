$(document).ready(function(){
	$(document).on('focus', '.auto_select input', function(e){
		$(this).select();
	})
});
