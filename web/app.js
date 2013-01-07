var map;

function createIcon(pilot) {
    var hdg = Math.round(pilot.heading / 15) * 15;

    var html = "";
    if (pilot.speed > 50) {
        html = "<div class=\"plane-label\"><div class=\"plane-callsign\">" + pilot.callsign + "</div></div>";
    }

    var type = "";
    if (pilot.aircraft.search(/B77[0-9]/i) >= 0) {
        type = "b777-";
    }
    else if (pilot.aircraft.search(/B76[0-9]/i) >= 0) {
        type = "b767-";
    }
    else if (pilot.aircraft.search(/B75[0-9]/i) >= 0) {
        type = "b757-";
    }
    else if (pilot.aircraft.search(/B74[0-9]/i) >= 0) {
        type = "b747-";
    }
    else if (pilot.aircraft.search(/B73[0-9]/i) >= 0) {
        type = "b737-";
    }
    else if (pilot.aircraft.search(/A38[0-9]/i) >= 0) {
        type = "a380-";
    }
    else if (pilot.aircraft.search(/A343/i) >= 0) {
        type = "a343-";
    }
    else if (pilot.aircraft.search(/A346/i) >= 0) {
        type = "a346-";
    }
    else if (pilot.aircraft.search(/A33[0-9]/i) >= 0) {
        type = "a330-";
    }
    else if (pilot.aircraft.search(/A3[12][0-9]/i) >= 0) {
        type = "a320-";
    }
    else if (pilot.aircraft.search(/MD11/i) >= 0) {
        type = "md11-";
    }

    var icon = L.divIcon({
        className: "plane plane-" + type + hdg,
        iconSize: null,
        iconAnchor: null,
        html: html,
    });

    return icon;
}

function pilotInfo(event) {
    $.getJSON("/pilots/" + this.callsign,
        function (data) {
            $("#sidebar").html($("#info-template").render(data));
        }
    );
}

function update() {
    $.getJSON("/pilots/",
        function (data) {
            data.forEach(function(pilot) {
                var icon = createIcon(pilot);
                var marker = L.marker(pilot.position, {icon: icon});
                marker.addTo(map);
                marker.on("click", pilotInfo, pilot);
            });
        }
    );

    $.getJSON("/atc/",
        function (data) {
            data.forEach(function(atc) {
                switch (atc.type) {
                case 3:
                    L.circle(atc.position, 5000, {
                        color: 'yellow',
                        weight: 2,
                    }).addTo(map);
                case 4:
                    L.circle(atc.position, 20000, {
                        color: 'red',
                        weight: 2,
                    }).addTo(map);
                case 5:
                    L.circle(atc.position, 50000, {
                        color: 'blue',
                        weight: 2,
                    }).addTo(map);
                }
            });
        }
    );
}

$(document).ready(function() {
    map = L.map('map').setView([51.505, -0.09], 5);

    L.tileLayer("http://{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png", {
        attribution: "",
        maxZoom: 18,
        subdomains: ["otile1", "otile2", "otile3", "otile4"],
        zoomControl: true,
    }).addTo(map);

    map.addControl(new L.Control.Scale());

    update();
});
