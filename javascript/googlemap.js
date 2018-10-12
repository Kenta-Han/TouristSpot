function initMap() {
  var map = new google.maps.Map(document.getElementById("map"), {
    center: {lat: 35.68109, lng: 139.76393694444},
    zoom: 12
  });

  var marker = new google.maps.Marker({
    position: {lat: 35.68109, lng: 139.76393694444},
    map: map
  });

  var infoWindow = new google.maps.InfoWindow({
    content: '<div><h3 style="text-decoration:none;">3,280万円/㎡ 1.1億円/坪</h3> <span style="color:green;">千代田区丸の内2-4-1</span></div>'
  });

  marker.addListener('click', function() {
    infoWindow.open(map, marker);
  });
}
