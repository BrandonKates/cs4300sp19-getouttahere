


function showMap(home, pairs){

 var mymap = L.map('map').setView([0, 0], 1);
 L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mymap);

 if (home!=null && home.length == 2){
     add_home_marker(home[0],home[1],mymap);
     alert(home[1])
 }

 input_lat_lon_pairs(pairs,mymap);


}

function input_lat_lon_pairs(pairs,mymap) {
   for (var i = 0; i < pairs.length; i++) {
        add_marker(pairs[i][0],pairs[i][1],"<b>" + pairs[i][2] + "<b>",mymap)
      }
}

function add_home_marker(lon,lat,mymap) {
    
    var iconCircle = L.circleMarker([parseFloat(lat), parseFloat(lon)]).addTo(mymap);
}

function add_marker(lon,lat,place,mymap) {

  var canoeIcon = L.icon({
    iconUrl: '/static/images/canoe_transparent.png',
    iconSize:     [40, 60], // size of the icon
    shadowSize:   [50, 64] // size of the shadow
});

  var jsonMarkerOptions = {
    radius: 8,
    draggable: true,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

var jsonTextOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};
    var marker = L.marker([lon, lat], {icon: canoeIcon}).addTo(mymap);

    marker.bindPopup(place,{autoPan:false});

    marker.on('mouseover', function (e) {
            this.openPopup();
        });

     marker.on('mouseout', function (e) {
            this.closePopup();
        });
}

//Credits: https://www.movable-type.co.uk/scripts/latlong.html
  function distance(lat1,lon1,lat2,lon2) {
  var R = 3958.8; // Radius of the earth in miles
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in miles
  return d.toFixed(2);
}

function deg2rad(deg) {
  return deg * (Math.PI/180)
}