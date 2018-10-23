var map;
var marker = [];
var infoWindow = [];
var markerData = [ // マーカーを立てる場所名・緯度・経度
  // {
  //   name: 'TAM 東京',
  //   lat: 35.6954806,
  //   lng: 139.76325010000005
  // }, {
  //   name: '小川町駅',
  //   lat: 35.6951212,
  //   lng: 139.76610649999998
  // }, {
  //   name: '淡路町駅',
  //   lat: 35.69496,
  //   lng: 139.76746000000003
  // }, {
  //   name: '御茶ノ水駅',
  //   lat: 35.6993529,
  //   lng: 139.76526949999993
  // }, {
  //   name: '神保町駅',
  //   lat: 35.695932,
  //   lng: 139.75762699999996
  // }, {
  //   name: '新御茶ノ水駅',
  //   lat: 35.696932,
  //   lng: 139.76543200000003
  // }
  {
    name: '新宿駅',
    lat: 35.689592,
    lng: 139.700413
  }, {
    name: '都庁',
    information : '長谷寺：眺め，市内を一望',
    lat: 35.689634,
    lng: 139.692101
  }, {
    name: '新宿御苑',
    information : '建長寺：日本庭園，落ち着く',
    lat: 35.685176,
    lng: 139.710052
  }, {
    name: '明治神宮',
    lat: 35.676398,
    lng: 139.699326
  }
];

// データを受け取る
function getdata(){
  var marker = document.getElementById('num').value;
  numx = parseInt(x);
  numx = numx + 1;
  document.getElementById('answer').innerHTML = numx;
}


function initMap() {
  // 地図の作成
  var mapLatLng = new google.maps.LatLng({
    lat: markerData[0]['lat'],
    lng: markerData[0]['lng']
  }); // 緯度経度のデータ作成
  map = new google.maps.Map(document.getElementById('map'), { // #mapに地図を埋め込む
    center: mapLatLng, // 地図の中心を指定
    zoom: 15 // 地図のズームを指定
  });

  // マーカー毎の処理
  for (var i = 0; i < markerData.length; i++) {
    markerLatLng = new google.maps.LatLng({
      lat: markerData[i]['lat'],
      lng: markerData[i]['lng']
    }); // 緯度経度のデータ作成
    marker[i] = new google.maps.Marker({ // マーカーの追加
      position: markerLatLng, // マーカーを立てる位置を指定
      map: map // マーカーを立てる地図を指定
    });

    infoWindow[i] = new google.maps.InfoWindow({ // 吹き出しの追加
      // 吹き出しに表示する内容
      content: '<div class="sample">' + markerData[i]['name'] + '<br>' + markerData[i]['information'] + '</div>'

    });

    markerEvent(i); // マーカーにクリックイベントを追加
  }

  marker[0].setOptions({ // TAM 東京のマーカーのオプション設定
    icon: {
      url: markerData[0]['icon'] // マーカーの画像を変更
    }
  });
}

// マーカーにクリックイベントを追加
function markerEvent(i) {
  marker[i].addListener('click', function() { // マーカーをクリックしたとき
    infoWindow[i].open(map, marker[i]); // 吹き出しの表示
  });
}
