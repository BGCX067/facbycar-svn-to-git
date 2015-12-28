$(document).ready(function() {

	$("#link_refine_search").click(function() 
	{
		$("#refine_search").slideToggle("slow");	
		
		if($(this).attr("state")=="off")
		{
			$(this).removeClass("link_refine_search_off");
			$(this).addClass("link_refine_search_on");
			$(this).attr("state", "on");
		}
		else if($(this).attr("state")=="on")
		{
			$(this).removeClass("link_refine_search_on");
			$(this).addClass("link_refine_search_off");
			$(this).attr("state", "off");
		}
		
	});
	
	$("#submit_comm_form").click(function() 
	{
		if($("#id_content").val()=='')
		{
			$("#field_content .error").html('Champ obligatoire');
			$("#field_content .error").css('display', 'block');
		}
		else
		{
			$.ajax({
				type: "POST",
				url: "/user_profile/",
				data: {
					"content":$("#id_content").val(), 
					"note":$("#id_note").val(),	 			
					"id_user":$("#id_user").val(),	 			
					"id_user_profil":$("#id_user_profil").val()},	 			
				dataType: "json",
				success: function(data){

					var div="<div class=\"block_comment\"><div class=\"block_comm\"><p class=\"block_comment_title\"><a title=\"Profil fac by car de "+data.username+"\" href=\"/user_profile/?u="+data.id_user+"\">"+data.username+"</a> a écrit le <span>"+data.date+"</span></p><p class=\"block_comment_note\"><img alt=\"Fac by car - Note de "+data.username+"\" src=\"/media/images/fac-by-car-etoile-"+data.note+".png\"/></p><p class=\"block_comment_content\">"+data.content+"</p></div></div>";
					var test2=document.getElementById("block_comments").lastChild;
					var block_comment = document.createElement('div');
					block_comment.innerHTML = div;
					
					document.getElementById('block_comments').insertBefore(block_comment, document.getElementById("premier").nextSibling);
					
					$("#nb_rating_profile").html(data.nb_rating);
					if(data.new_note == 0)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-0.png');
					if(data.new_note > 0 && data.new_note <= 0.5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-0-5.png');
					if(data.new_note > 0.5 && data.new_note <= 1)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-1.png');
					if(data.new_note > 1 && data.new_note <= 1.5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-1-5.png');
					if(data.new_note > 1.5 && data.new_note <= 2)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-2.png');
					if(data.new_note > 2 && data.new_note <= 2.5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-2-5.png');
					if(data.new_note > 2.5 && data.new_note <= 3)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-3.png');
					if(data.new_note > 3 && data.new_note <= 3.5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-3-5.png');
					if(data.new_note > 3.5 && data.new_note <= 4)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-4.png');
					if(data.new_note > 4 && data.new_note <= 4.5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-4-5.png');
					if(data.new_note > 4.5 && data.new_note <= 5)
						$("#image_note img").attr('src', '/media/images/fac-by-car-etoile-5.png');
						
				},
				error: function(){
					alert('error');
				}
			});
		}
		return false;
	});
	/*data: '{"A":5, "B":5}',*/
	
	/*$("#add").click(function(){
        $.post("/foo/", {},
            function(data) {
                alert(data);
            }, "json");
    });*/
	
});