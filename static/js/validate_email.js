/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
        document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
        var __noconflict = true;

}

(function ($){
        $(function(){
            validation_url="/is_email_valid/";
            invitation_url="/additional_invitations/"
            jQuery(".btn-primary").click(function(){
                var mails = new Array();
                submit_button = $(this);
                i = 0 ;
                jQuery("input.verify_email").each(function(){

                    if($(this).attr('data-valid')=="valid"){
                        mails[i] = $(this).val();
                        i++;
                    }
                });

                if (mails.length == 0){
                }else{
                    submit_button.attr("disabled","disabled");
                    jQuery.ajax({
                        type: 'POST',
                        url: invitation_url,
                        data:{
                            emails: mails.join(',')
                        },
                        dataType: 'json',
                        success: function(response){
                            /*console.log(response);*/
                            if(response.is_valid){
                                $("#form_messages").html(response.msg);
                                $("#form_messages").removeAttr("class");
                            }else{
                                $("#form_messages").html(response.error);
                                $("#form_messages").attr("class","errornote");
                            }
                            submit_button.removeAttr("disabled");
                        },
                        error: function(response){
                            submit_button.removeAttr("disabled");
                        }
                    });
                }

            });
            jQuery(".log-reg-form").submit(function(){
                return false;
            });
            jQuery(".verify_email").blur(function(){
                current = $(this).val();
                previous = $(this).attr('data-previous');
                id = $(this).attr('id').replace('validation_','');
                if( current != previous){
                    jQuery.ajax({
                        type: 'POST',
                        url: validation_url,
                        data:{
                            email: $(this).val()
                        },
                        dataType: "json",
                        success: function(response){

                            if(response.is_valid){
                              $("#message_"+id).html('');
                              $("#validation_"+id).attr("data-valid","valid");
                              $("#message_"+id).removeAttr("class");
                            }else{
                              $("#message_"+id).html(response.error);
                              $("#validation_"+id).attr("data-valid","invalid");
                              $("#message_"+id).attr("class","errornote");
                            }
                        }
                    });
                }
                $(this).attr('data-previous',current);

            });
        });
})(jQuery);
