/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
        document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
        var __noconflict = true;

}

$(function(){
    $("#post-comment").click(function(){
	var button = $(this).attr("disabled", "disabled");
	var comment = $("#comment-area").val();

	var url = button.attr("data-target-href"),
	comment_user = button.attr("data-comment-user");
	$.ajax({
	    type: "POST",
	    url: url,
	    data: {
		comment_user: comment_user,
		comment: comment
	    },
            success: function(document){
		var raw_html = document.raw_html;
		var comment_section = $("#comment-section");
		raw_html = raw_html.replace(/\n+/gi,"").replace(/\s+/gi," ");
		comment_section.append(raw_html);
		$("#comment-area").val("");
                button.removeAttr("disabled");
            },
            error: function(response){
		button.removeAttr("disabled");
            }
        });
    })
})
