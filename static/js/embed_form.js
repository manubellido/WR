$("#embed-button").click(function () {
    var div = $("#embed-div");
    var mq = window.matchMedia("(max-width: 767px)");
    var diff = mq.matches ? 260 : 130;;
    if(mq.matches)
	if(!$("#custom-group").hasClass("expanded"))
	    diff -= 80;

    if(div.hasClass('expanded')){
	div[0].style.display = "hidden";
	div.animate(
	    {'height': '-=' + diff},
	    500);
    }
    else{
	div[0].style.display = "block";
	div.animate(
	    {'height': '+=' + diff},
	    500);
    }
    $(this).toggleClass('active');
    div.toggleClass('expanded');
});

$("#embed-html").click(function () {
    $(this).select();
});

function set_embed_html(){
    var html_box = $("#embed-html");
    var size = $("#embed-size").find("option:selected").attr("value");

    if(size == "custom"){
	var height = $("#custom-height").attr("value");
	var width = $("#custom-width").attr("value");
	var size_parts = [width, height];
    }
    else
	var size_parts = size.split("x");

    var html = "<iframe width=\"" + size_parts[0] +
	"\" height=\"" + size_parts[1] +
	"\" src=\"" + site_prefix + circuit_url + "?embedded=true\"></iframe>";

    html_box.val(html);
};

$("#embed-size").change(function () {
    var size = $("#embed-size").find("option:selected").attr("value");
    var custom_group = $("#custom-group");
    var mq = window.matchMedia("(max-width: 767px)");

    if(size == "custom"){
	if(!custom_group.hasClass("expanded")){
	    custom_group[0].style.display = "block";
	    custom_group.animate(
		{'height': '+=' + 60},
		500);
	    if(mq.matches)
		$("#embed-div").animate(
		    {'height': '+=' + 60},
		    500);
	    else;
	    custom_group.toggleClass("expanded");
	    $("#custom-width").focus();
	}
	else;
    }
    else{
	custom_group[0].style.display = "hidden";
	custom_group.animate(
	    {'height': '-=' + 60},
	    500);
	    if(mq.matches)
		$("#embed-div").animate(
		    {'height': '-=' + 60},
		    500);
	    else;
	if(custom_group.hasClass("expanded"))
	    custom_group.toggleClass("expanded");
    }
    set_embed_html();
});

function isNumber(n) {
  return !isNaN(parseInt(n));
}
$("#custom-height").keyup(function () {
    var n = $(this).attr("value").charAt($(this).attr("value").length-1);
    if(isNumber(n))
	set_embed_html();
    else
	$(this).attr(
	    "value",
	    $(this).attr("value").substr(0, $(this).attr("value").length-1)
	);
});

$("#custom-width").keyup(function () {
    var n = $(this).attr("value").charAt($(this).attr("value").length-1);
    if(isNumber(n))
	set_embed_html();
    else
	$(this).attr(
	    "value",
	    $(this).attr("value").substr(0, $(this).attr("value").length-1)
	);
});


set_embed_html();
