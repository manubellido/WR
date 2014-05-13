django.jQuery(document).ready(function() {
    
	post_url = "/api/v1/circuits/{circuit-id}/patch";
		django.jQuery(".inline-admin-category-edit").change(function(){
			circuit_id = $(this).attr('data-id');
			cat_id = $(this).val();
			update_url = post_url.replace("{circuit-id}",circuit_id);
			django.jQuery.ajax({                                                       
				type: 'POST',                                                   
				url : update_url,                                               
				data: {category:cat_id,circuit_id:circuit_id},                  
				success: function(response){                                    
					console.log("Circuito actualizado");                                      					
				}
			});
		});
});


