/*
  This should work on any label that needs to be made clickable.
  The label should have the following html attributes:
  - 'for=name' where name is the 'name' attr of the checkbox.
  - 'clickable', so jquery can find it correctly
*/
$("label[clickable]").click(function () {
    var label_for = $(this).attr("for");
    var checkbox = $("input[name='" + label_for + "']")
    checkbox.attr("checked", !checkbox.attr("checked"));
});
