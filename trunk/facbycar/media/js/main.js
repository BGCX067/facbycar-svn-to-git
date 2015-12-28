// GOOGLE MAP API AUTOCOMPLETE + DIRECTIONS ON THE MAP
var geocoder;
var map;

var latlng;
var latlngArrivee;

var markerFac;

var rendererOptions = {
  draggable: false
};
var directionsService = new google.maps.DirectionsService();
var directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);


function initialize(){
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

});


// Connect to the google server to take the data and being able to calculate the way
function calcRoute() {
  var start = document.getElementById("address").innerHTML +', '+ document.getElementById("cityd").innerHTML +',France ';
  var end = document.getElementById("address2").innerHTML +', '+ document.getElementById("citya").innerHTML+',France ';
  //var start ="paris, France";
  //var end = "Champs sur marne, france";
  var request = {
    origin:start, 
    destination:end,
    travelMode: google.maps.DirectionsTravelMode.DRIVING
  };
  directionsService.route(request, function(response, status) {
	 
    if (status == google.maps.DirectionsStatus.OK) {
		var distanceKm = response.routes[0].legs[0].distance.value/1000;
		var dureeMin = Math.round(response.routes[0].legs[0].duration.value/60);
		var heure=0;
		while(dureeMin>60){
			heure +=1;
			dureeMin -=60;
		}
		if(heure>0)
		{
			$('#duree').innerHTML(heure+' h '+dureeMin + ' min');
		} else 	$('#duree').html(dureeMin + ' min');
		$('#distance').html(distanceKm+' KM');
		directionsDisplay.setDirections(response);
    }
  });
  
}
