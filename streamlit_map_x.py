import streamlit as st

st.write("깃허브 + 스트림릿_구현 되는 틀")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <title>되는지 안되는지 확인</title>
    
    <style>
     #map { width: 100%; height: 800px; }
     #placesList { list-style: none; padding: 0; }
     #placesList li { margin: 5px 0; }
    </style>
</head>
<body>

 <h1>카카오 지도와 장소 검색</h1>
    <input type="text" id="keyword" placeholder="검색할 장소 입력" />
    <button id="searchButton">장소 검색</button>
    <ul id="placesList"></ul>
    <div id="map"></div>


    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=393132b4dfde1b54fc18b3bacc06eb3f&libraries=services"></script>

    // 카카오 맵 API 로드 완료 후 초기화
    kakao.maps.load(function() {
        // 지도와 마커 관련 변수
        var map;
        var markers = [];

        // 카카오 지도 초기화
        function initMap() {
            var mapContainer = document.getElementById('map');
            var mapOption = {
                center: new kakao.maps.LatLng(37.5665, 126.978), // 서울 시청
                level: 3
            };

            map = new kakao.maps.Map(mapContainer, mapOption);
        }

        // 장소 검색 함수
        function searchPlaces(lat, lon, radius, categoryCode) {
            var apiKey = "6c1cbbc51f7ba2ed462ab5b62d3a3746";
            var url = "https://dapi.kakao.com/v2/local/search/category.json";

            $.ajax({
                method: "GET",
                url: url,
                data: {
                    category_group_code: categoryCode,
                    x: lon,
                    y: lat,
                    radius: radius
                },
                headers: { 
                    Authorization: "KakaoAK " + apiKey 
                }
            })
            .done(function (msg) {
                displayPlaces(msg.documents);
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.error("API 호출 실패: " + textStatus, errorThrown);
            });
        }

        // 장소를 지도에 마커로 표시하는 함수
        function displayPlaces(places) {
            removeMarkers();
            var placesList = $("#placesList");
            placesList.empty();

            places.forEach(function(place) {
                var position = new kakao.maps.LatLng(place.y, place.x);
                addMarker(position);
                placesList.append("<li>" + place.place_name + " - " + place.address_name + "</li>");
            });
        }

        // 마커를 지도에 추가하는 함수
        function addMarker(position) {
            var marker = new kakao.maps.Marker({
                position: position
            });
            marker.setMap(map);
            markers.push(marker);
        }

        // 이전 마커 제거
        function removeMarkers() {
            markers.forEach(function(marker) {
                marker.setMap(null);
            });
            markers = [];
        }

        // 버튼 클릭 시 장소 검색
        $("#searchButton").click(function() {
            var lat = 37.5665;
            var lon = 126.978;
            var radius = 1000;
            var categoryCode = "FD6";

            searchPlaces(lat, lon, radius, categoryCode);
        });

        // 페이지 로드 시 지도 초기화
        initMap();
    });
</script>
</body>
</html>
"""

# HTML 표시
st.components.v1.html(html_code, height=800)
