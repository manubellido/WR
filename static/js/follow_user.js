/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
        document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
        var __noconflict = true;

}

$(function(){
    $("#follow-user").click(function(){
	var button = $(this).attr("disabled", "disabled");
	var follow_url = button.attr("data-follow-url"),
	unfollow_url = button.attr("data-unfollow-url"),
	isfollower_url = button.attr("data-isfollower-url");
	var isfollower = false;
	$.ajax({
	    async: false,
	    type: "GET",
	    url: isfollower_url,
            dataType: 'json',
            success: function(document){
		isfollower = (document.is_follower == true) ? true : false;
            },
            error: function(response){
		button.removeAttr("disabled");
            }
        });
	$.ajax({
	    type: "POST",
	    url: (isfollower) ? unfollow_url : follow_url,
            dataType: 'json',
            success: function(response){
		isfollower = !isfollower;
                button.removeAttr("disabled");
		button.text((isfollower) ? "Unfollow" : "Follow");
            },
            error: function(response){
                button.removeAttr("disabled");
            }
        });
    })
})
