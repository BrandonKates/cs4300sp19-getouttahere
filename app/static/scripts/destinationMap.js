


function showMap(pairs){

 var mymap = L.map('map').setView([0, 0], 1);
 L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mymap);

 input_lat_lon_pairs(pairs,mymap)

}

function input_lat_lon_pairs(pairs,mymap) {
   for (var i = 0; i < pairs.length; i++) {
        add_marker(pairs[i][0],pairs[i][1],"<b>" + pairs[i][2] + "<b>",mymap)
      }
}


function add_marker(lon,lat,place,mymap) {

  var canoeIcon = L.icon({
    iconUrl: '/static/images/canoe_transparent.png',
    iconSize:     [40, 60], // size of the icon
    shadowSize:   [50, 64] // size of the shadow
});

  var jsonMarkerOptions = {
    radius: 8,
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
    var marker = L.marker([lon, lat],  {icon: canoeIcon}).addTo(mymap);

    marker.bindPopup(place);

    marker.on('mouseover', function (e) {
            this.openPopup();
        });

     marker.on('mouseout', function (e) {
            this.closePopup();
        });

  
}

 