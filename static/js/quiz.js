<!-- Ваш код JavaScript -->
<script>
    var map = L.map('map').setView([51.505, -0.09], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1
    }).addTo(map);

    var marker;
    var markerPosition;

    // Обработка события клика на карте
    map.on('click', function(e) {
      // получение координат клика
      var lat = e.latlng.lat;
      var lon = e.latlng.lng;

      // добавление маркера на карту
      if (marker) {
        marker.setLatLng([lat, lon]);
      } else {
        marker = L.marker([lat, lon]).addTo(map);
      }
      // сохранение позиции маркера
      markerPosition = { lat: lat, lon: lon };
    });
</script>