// GOOGLE MAP API AUTOCOMPLETE + DIRECTIONS ON THE MAP
// GOOGLE MAP API AUTOCOMPLETE + DIRECTIONS ON THE MAP
var geocoder;
var map;

var latlng;
var latlngArrivee;

var markerFac;

var rendererOptions = {
  draggable: true
};
var directionsService = new google.maps.DirectionsService();
var directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);



function initialize(){
	// Initialise the start and end of the direction
	
	$("#id_city_a").val("Champs-sur-Marne");
	$("#id_place_a").val('5 Boulevard Descartes');
	$("#id_city_d").val("Champs sur Marne");
	$("#id_place_d").val('Station RER');
	
	// MAP OPT
	var options = {
		zoom: 12,
		scaleControl: true,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map_canvas"), options);
        
	//GEOCODER
	geocoder = new google.maps.Geocoder();
	
	// MARKERS
	var imageFac ='http://etudiant.univ-mlv.fr/~fbrin/umlv.png';  
	var myLatlng = new google.maps.LatLng(48.83971,2.58884);
	markerFac = new google.maps.Marker({
		map: map,
		position: myLatlng,
		draggable: false,
		clickable: false,
		icon : imageFac,
		title:"Hello World!",
		zIndex: 0
	});
	
	directionsDisplay.setMap(map);
	calcRoute();
}
	
$(document).ready(function() { 
         
  initialize();  
  
  $(function() {
	  //AUTOCOMPLETE OF THE DEPARTURE FIELD
    $("#id_city_d").autocomplete({
      //This bit uses the geocoder to fetch id_place_d values
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
								latitude: item.geometry.location.lat(),
								longitude: item.geometry.location.lng()
							}
						}
					}
			}));
		})
      },
      //This bit is executed upon selection of an id_place_d
      select: function(event, ui) {
      
        var location = new google.maps.LatLng(ui.item.latitude, ui.item.longitude);
        //marker.setPosition(location);
        //map.setCenter(location);
		//calcRoute();
      }
    });
	
	//AUTOCOMPLETE OF THE ARRIVAL FIELD
	$("#id_city_a").autocomplete({
      //This bit uses the geocoder to fetch id_place_d values
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
								latitude: item.geometry.location.lat(),
								longitude: item.geometry.location.lng()
							}
						}
					}
			}));
		})
      },
      //This bit is executed upon selection of an id_place_d
      select: function(event, ui) {
		
		var location = new google.maps.LatLng(ui.item.latitude, ui.item.longitude);
		//markerArrivee.setPosition(location);
		//map.setCenter(location);
		//calcRoute();
		
      }
    });
  });
	

	// ADD an Event Listener on the directions so each we change it it call this fonction
	google.maps.event.addListener(directionsDisplay, 'directions_changed', function() {
		computeDistance(directionsDisplay.directions);
  	});

});

// Give the distance, the duration and the arrival and departure adress
function computeDistance(result) {
	var start2 =  result.routes[0].legs[0].start_location;
	var end2 =  result.routes[0].legs[0].end_location;
	
	
	//Convert the coordinate of a point in an postal adress
	geocoder.geocode({'latLng': start2}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        if (results[0]) {
			var i;
			var pointDepart='';
			var isInFrance=false;
			for (i=0 ; i<= results[0].address_components.length-1 ; i++)
            {
				if((results[0].address_components[i].types == 'country,political') && (results[0].address_components[i].long_name=='France'))
				{
					isInFrance=true;
				}
				if((results[0].address_components[i].types == 'locality,political') ||(results[0].address_components[i].types == 'sublocality,political') )
				{
					 $('#id_city_d').val(results[0].address_components[i].long_name); 
				} else if(results[0].address_components[i].types == 'street_number')
				{
					pointDepart = pointDepart+results[0].address_components[i].long_name+ ' ';
				} else if(results[0].address_components[i].types == 'route')
				{
					pointDepart = pointDepart+results[0].address_components[i].long_name;
				}
			}
			if(isInFrance)
			{
				$('#id_place_d').val(pointDepart); 
			} else 
			{
				$('#id_city_d').val("VA EN COURS");
				$('#id_place_d').val(" ");
			}
        }
      }
    });
	geocoder.geocode({'latLng': end2}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        if (results[0]) {
			var pointArrivee='';
			var i;
			var isInFrance=false;
			for (i=0 ; i<= results[0].address_components.length-1 ; i++)
            {
				if((results[0].address_components[i].types == 'country,political') && (results[0].address_components[i].long_name== 'France'))
				{
					isInFrance=true;
				}
				if((results[0].address_components[i].types == 'locality,political') ||(results[0].address_components[i].types == 'sublocality,political') )
				{
					 $('#id_city_a').val(results[0].address_components[i].long_name); 
				} else if(results[0].address_components[i].types == 'street_number')
				{
					pointArrivee = pointArrivee+results[0].address_components[i].long_name+ ' ';
				} else if(results[0].address_components[i].types == 'route')
				{
					pointArrivee = pointArrivee+results[0].address_components[i].long_name;
				}
			}
         	if(isInFrance)
			{
				$('#id_place_a').val(pointArrivee); 
			} else 
			{
				$('#id_city_a').val("VA EN COURS");
				$('#id_place_a').val(" "); 
			}
		}
      }
    });
}   


// Connect to the google server to take the data and being able to calculate the way
function calcRoute() {
  var start = document.getElementById("id_place_d").value +', '+ document.getElementById("id_city_d").value +',France ';
  var end = document.getElementById("id_place_a").value +', '+ document.getElementById("id_city_a").value+',France ';
  //alert(start+'    '+end);
  var request = {
    origin:start, 
    destination:end,
    travelMode: google.maps.DirectionsTravelMode.DRIVING
  };
  directionsService.route(request, function(response, status) {
    if (status == google.maps.DirectionsStatus.OK) {
	
		directionsDisplay.setDirections(response);
    }
  });
}

function initButtonResearch()
{	
   		calcRoute();	
}
