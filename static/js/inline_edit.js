
/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
	document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
	var __noconflict = true;
	var categories = "";
}
function fill_dropdown(dd){
	content = "";
	current= dd.attr('data-current');
	for(i=0;i<categories.length;i++){
		selected = '';
		if(categories[i].title == current){
			selected = 'selected="selected"';
		}
		content += '<option '+selected+' value="' + categories[i].id+ '">'+categories[i].title+"</option>\n";
	}
	dd.html(content);
}
(function ($){
	$(function(){
		jQuery(".btn-primary").ajaxComplete(function(){
				jQuery(".inline-category-edit").each(function(){
					fill_dropdown(jQuery(this));
				});
		});
		url = "/api/v1/circuits/categories";
		post_url = "/api/v1/circuits/{circuit-id}/patch";
		jQuery(".inline-category-edit").live('change',function(){
			cat_id = $(this).val();

			circuit_id = $(this).attr('data-id');
			update_url = post_url.replace("{circuit-id}",circuit_id);
			name = $(this).attr('data-name','');
			$(this).attr('data-current',$("option:selected", this).text());
			jQuery.ajax({
				type: 'POST',
				url : update_url,
				data: {category:cat_id,circuit_id:circuit_id},
				success: function(response){
					console.log(response);
					console.log(circuito_actualizado);
				}
			});
		});
		jQuery.ajax({
			url: url,
			dataType: "json",
			success: function(response){
				categories = response.categories;
				//Actualizamos todos los dropdown
				jQuery(".inline-category-edit").each(function(){
					fill_dropdown(jQuery(this));
				});
			}
		});
	});
	
})(jQuery);
