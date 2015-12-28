// GOOGLE MAP API AUTOCOMPLETE + DIRECTIONS ON THE MAP
var geocoder;
var map;

function initialize(){
	// Initialise the start and end of the direction
	//MAP
	
	// MAP OPT
	var options = {
		zoom: 12,
		scaleControl: true,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map_canvas"), options);
        
	//GEOCODER
	geocoder = new google.maps.Geocoder();
	
	$("#city_a").val("Champs-sur-Marne");
	$("#city_d").val("...");
	
}
	
$(document).ready(function() {   
  initialize();  

  
  $(function() {
	  //AUTOCOMPLETE OF THE DEPARTURE FIELD
    $("#city_d").autocomplete({
		
      //This bit uses the geocoder to fetch address values
       source: function(request, response) {
		var _address = request.term +', France,'+ ' Europe';
			geocoder.geocode( {'address':  _address}, function(results, status) {
				response($.map(results, function(item) {
					var i;
					for (i=0 ; i<= item.address_components.length-1 ; i++)
            		{
						if((item.address_components[i].types == 'locality,political') ||(item.address_components[i].types == 'sublocality,political') )
						{
							return {
								label: item.address_components[i].long_name,
								value: item.address_components[i].long_name,
							}
						}
					}
			}));
		})
      },
      //This bit is executed upon selection of an address
      select: function(event, ui) {
     	
      }
    })
	
	//AUTOCOMPLETE OF THE ARRIVAL FIELD
	$("#city_a").autocomplete({
      //This bit uses the geocoder to fetch address values
      source: function(request, response) {
		var _address = request.term +' France'+ ' Europe';
			geocoder.geocode( {'address':  _address}, function(results, status) {
				response($.map(results, function(item) {
					var i;
					for (i=0 ; i<= item.address_components.length-1 ; i++)
            		{
						if((item.address_components[i].types == 'locality,political') ||(item.address_components[i].types == 'sublocality,political') )
						{
							return {
								label: item.address_components[i].long_name,
								value: item.address_components[i].long_name,
							}
						}
					}
			}));
		})
      },
      //This bit is executed upon selection of an address
      select: function(event, ui) {
		//alert('toto');
		
      }
    });
  });
	


});




