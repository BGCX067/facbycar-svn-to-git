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
	
	// Commentaires
	$("#submit_comm_form").click(function() 
	{
		if($("#id_content").val()=='')
		{
			$("#field_content .error").html('Champ obligatoire');
			$("#field_content .error").show();
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
	
	// Particpation au trajet
	$("#participate").click(function() 
	{
		$.ajax({
			type: "POST",
			url: "/route/",
			data: {			
				"id_user":$("#id_user").val(),	 						 			
				"id_route":$("#id_route").val()},	 			
			dataType: "json",
			success: function(data){
				$(".overlay").show();
				$("#rep").show();
				$("#participate").hide();
			},
			error: function(){
				alert('error');
			}
		});	
		return false;
	});
	
	
	/* Close pop-in */ 
	$(".popin .close").click(function(){
		$("#rep").hide();
		$(".overlay").hide();	
	});
	$(".overlay").click(function(e){
		// Close the overlay and poping only on direct hit
		if (e.target === $(".overlay")[0]) {
			$("#rep").hide();
			$(".overlay").hide();		
		}
	});
	
	
	
	
});

function validateFormAddRoute2() {
	var form=document.forms["form_route2"];
	
	Today = new Date;
	JourToday = Today.getDate();
	MoisToday = (Today.getMonth())+1;
	AnneeToday = Today.getFullYear();
	
	/*Daily*/
	var mo=form["hour_mo"].value;
	var tu=form["hour_tu"].value;
	var we=form["hour_we"].value;
	var th=form["hour_th"].value;
	var fr=form["hour_fr"].value;
	var sa=form["hour_sa"].value;
	var su=form["hour_su"].value;
	
	var start=form["start_time"].value;
	var end=form["end_time"].value;
	
	var annee_start = start.substr(0, 4);
	var mois_start = start.substr(5, 2);
	var jour_start = start.substr(8, 2);
	
	var annee_end = end.substr(0, 4);
	var mois_end = end.substr(5, 2);
	var jour_end = end.substr(8, 2);
	
	if (mo=="00" && tu=="00" && we=="00" && th=="00" && fr=="00" && sa=="00" && su=="00" ) {
		$("#form_route_time_daily .error").css('display', 'block');
		return false;
	}
	if(start=="" || start=="aaaa-mm-jj" || end=="" || end=="aaaa-mm-jj") {
		$("#form_route_time_validity .error").css('display', 'block');
		return false;
	}
	else if(annee_start < AnneeToday || mois_start < MoisToday || jour_start < JourToday || annee_end < AnneeToday || mois_end < MoisToday || jour_end < JourToday) {
		$("#form_route_not_daily .error2").css('display', 'block');
		return false;
	}
	
}

function validateFormAddRoute2_2() {
	var form=document.forms["form_route2"];
	
	Today = new Date;
	JourToday = Today.getDate();
	MoisToday = (Today.getMonth())+1;
	AnneeToday = Today.getFullYear();
	
	/*Not Daily*/
	var hour=form["hour"].value;
	var date=form["date"].value;
	
	var annee = date.substr(0, 4);
	var mois = date.substr(5, 2);
	var jour = date.substr(8, 2);
	

	if (date=="aaaa-mm-jj" || date=="" ) {
		$("#form_route_not_daily .error").css('display', 'block');
		return false;
	}
	else if(annee < AnneeToday || mois < MoisToday || jour < JourToday) {
		$("#form_route_not_daily .error2").css('display', 'block');
		return false;
	}
	if (hour=="00") {
		$(".fieldWrapper .error").css('display', 'block');
		return false;
	}
}


/*CSRF*/
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
