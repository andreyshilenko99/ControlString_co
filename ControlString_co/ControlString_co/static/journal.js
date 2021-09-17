var last_id = 0;

function refresh() {
    $.getJSON('/geo/journal_view/', function (data) {
        var current_id = data.features[0].properties.pk;
        console.log('data ', data)
        console.log('last_id ', last_id)
        console.log('current_id ', current_id)
        if (last_id === 0) {
            last_id = current_id;
        } else if (last_id !== current_id) {
            $.ajax({
                url: "journal",
                success: function (data) {
                    $("#detections").load("journal #detections");
                    // $('#detections').replaceWith($('#detections', data));
                    last_id = current_id;
                }
            });
        }
    })
}

var seconds_wait = 3; // seconds, edit here
setInterval(refresh, seconds_wait * 1000);

function map_init_basic(map, options) {
    function isEmpty(obj) {
        return Object.keys(obj).length === 0;
    }

    function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
    }

    function getRandomColor() {
        let letters = '0123456789ABCDEF';
        let color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    function random_rgba() {
        var o = Math.round, r = Math.random, s = 255;
        return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + '100' + ')';
    }

    function draw_tooltip(map, coords, icon_url, size, tooltip_text) {
        var tooltip_strizh = new L.Tooltip({
            direction: 'bottom',
            permanent: true,
            noWrap: true,
            opacity: 1
        });
        let logoMarkerStyleStrizh = L.Icon.extend({
            options: {
                iconSize: [size, size],
                iconAnchor: [size / 2, size / 2],
                popupAnchor: [0, size],
                // className: 'blinking'
            }
        });
        var logoMarkerStrizh = new logoMarkerStyleStrizh({
            iconUrl: icon_url
        });
        var mark = L.marker(coords,
            {icon: logoMarkerStrizh})
            .addTo(map)
        if (tooltip_text) {
            tooltip_strizh.setContent('PIZDA');
            mark.bindTooltip(tooltip_strizh).openTooltip()
        }
    }

    function place_text(map, coords, text) {
        var tooltip_ = new L.tooltip({
            direction: 'center',
            noWrap: true,
            permanent: true,
            opacity: 1,
            offset: L.point({x: -12, y: 24}),
            className: 'leaflet-tooltip-height'
        }).setContent(text.toString());

        L.marker(coords, {
            opacity: 0,
        })
            .addTo(map)
            .bindTooltip(tooltip_)
            .openTooltip();
    }


    map.setView([60.013674, 30.452474], 14);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; Strizh'
    }).addTo(map);

    var layerDrones = L.layerGroup().addTo(map);
    var layerStrizhes = L.layerGroup().addTo(map);
    var counter_periodic = -1;
    counter_periodic = counter_periodic + 1;

    $.getJSON('/geo/drone_journal/', function (data) {
        let arc1;
        let str1;
        let name1;
        let logoMarkerStyle = L.Icon.extend({
            options: {
                iconSize: [46, 46],
                iconAnchor: [23, 23],
                popupAnchor: [0, -46],
                // className: 'blinking'
            }
        });

        $.getJSON('/geo/strizh_view/', function (strizh_data) {
            let len_strizh_data = strizh_data.features.length;
            let strizh_map_name = {};

            // var logoMarkerStrizh = L.icon.pulse({iconSize:[20,20],color:'red', iconUrl: 'static/icons/g3.gif'});

            let logoMarkerStyleStrizh = L.Icon.extend({
                options: {
                    iconSize: [80, 80],
                    iconAnchor: [40, 75],
                    popupAnchor: [0, -80]
                }
            });
            var logoMarkerStrizh = new logoMarkerStyleStrizh({
                // iconUrl: 'static/icons/strizh_blue_pulse.gif'
                iconUrl: 'static/icons/strizh_markers/blue.png'
            });

            for (let j = 0; j < len_strizh_data; j++) {

                strizh_map_name[strizh_data.features[j].properties.name] = [strizh_data.features[j].properties.lat,
                    strizh_data.features[j].properties.lon, strizh_data.features[j].properties.name];

                console.log('strizh_data: ', strizh_data.features[j].properties)

                if (counter_periodic <= 10) {
                    if (counter_periodic === 10) {
                        counter_periodic = 0;
                        layerStrizhes.clearLayers();
                    }
                    if (counter_periodic === 0) {
                        var tooltip = L.tooltip({
                            direction: 'bottom',
                            noWrap: true,
                            permanent: true,
                            opacity: 0.85
                        })
                            .setContent(strizh_data.features[j].properties.name);

                        str1 = L.marker([strizh_data.features[j].properties.lat,
                            strizh_data.features[j].properties.lon], {icon: logoMarkerStrizh}).addTo(layerStrizhes)
                            .bindTooltip(tooltip).openTooltip();
                    }
                    map.addLayer(layerStrizhes)
                }
            }
            let logoMarker = new logoMarkerStyle({iconUrl: 'static/icons/drons/dron_top.png', color: '#ff0000'});
            console.log('data ', data)
            // статичная отрисовка радиуса вокруг стрижа, стрижа и его подписи
            if (data.features.length !== 0) {
                let radius = parseFloat(data.features[0].properties.area_radius_m);
                let area_sector_start_grad = parseFloat(data.features[0].properties.area_sector_start_grad);
                let area_sector_end_grad = parseFloat(data.features[0].properties.area_sector_end_grad);
                console.log('strizh_map_name', strizh_map_name)
                console.log('data.features[0].properties.strig_name', data.features[0].properties.strig_name)
                console.log('strizh_map_name[data.features[0].properties.strig_name]',
                    strizh_map_name[data.features[0].properties.strig_name])

                console.log('strizh_map_name[data.features[0].properties.strig_name]',
                    strizh_map_name[data.features[0].properties.strig_name])

                let strizh_center = [strizh_map_name[data.features[0].properties.strig_name][0], strizh_map_name[data.features[0].properties.strig_name][1]];

                // Отрисовка сектора с обновлением + layerDrones
                let r_y = 0.004499 * 4 / 5
                let r_x = 0.008892 * 4 / 5

                if (area_sector_start_grad === -1 && area_sector_end_grad === -1) {
                    let angle = (90 - (area_sector_start_grad)) / 180 * Math.PI;
                    var d_y = 0.004499 * Math.sin(angle);
                    var d_x = 0.008892 * Math.cos(angle);
                    arc1 = L.circle(strizh_center, {
                        color: '#0296f8',
                        // fillColor: "#f1b44e",
                        fillColor: "#3aacfd",
                        fillOpacity: 0.15,
                        radius: radius
                    }).addTo(layerDrones);

                } else {
                    let angle = (90 - (area_sector_start_grad + 30)) / 180 * Math.PI;
                    var d_y = r_y * Math.sin(angle);
                    var d_x = r_x * Math.cos(angle);
                    arc1 = L.circle(strizh_center, {
                        color: '#0296f8',
                        // fillColor: "#f1b44e",
                        fillColor: "#3aacfd",
                        fillOpacity: 0.02,
                        radius: radius
                    }).addTo(layerDrones);

                    L.circle(strizh_center, {
                        color: '#0296f8',
                        // fillColor: "#f1b44e",
                        fillColor: "#fddd3a",
                        radius: radius,
                        startAngle: area_sector_start_grad,
                        endAngle: area_sector_end_grad,

                    }).addTo(layerDrones);


                }

                // Отрисовка подписи к дрону в секторе + layerDrones
                //TODO current_time
                let podpis = data.features[0].properties.detection_time.substr(0, 19) + '.  ' +
                    data.features[0].properties.system_name + '.  ' + data.features[0].properties.comment_string

                console.log('podpis', podpis)

                var tooltip_drone = L.tooltip({
                    maxWidth: 2000,
                    direction: 'top',
                    offset: L.point({x: 0, y: -20}),
                    permanent: true,
                    opacity: 0.85,
                    className: 'leaflet-tooltip-own'
                })
                    .setContent(podpis);

                // Отрисовка дрона в секторе + layerDrones
                L.marker([strizh_center[0] + d_y,
                    strizh_center[1] + d_x], {icon: logoMarker}).addTo(layerDrones)
                    .bindTooltip(tooltip_drone).openTooltip();
            }
        });
    })


    $.getJSON('/geo/drone_journal_view_traj/', function (data) {
        console.log('data    drone_journal_view_traj', data)
        // var points_coords = {}
        var points_data = {}
        var n_elements = data.features.length;

        draw_tooltip(map,
            coords = [60.013674, 30.442474],
            icon_url = 'static/icons/controller/contr1_black.png', size = 50, tooltip_text = '')


        draw_tooltip(map,
            coords = [60.015, 30.55],
            icon_url = 'static/icons/home.png', size = 50, tooltip_text = '')

        for (let i = 0; i < n_elements; i++) {
            var aero_value = data.features[i].properties;
            var drone_id = aero_value.drone_id;
            var drone_lat = aero_value.drone_lat;
            var drone_lon = aero_value.drone_lon;
            var height = aero_value.height;
            if (!points_data[drone_id] || isEmpty(points_data[drone_id])) {
                points_data[drone_id] = {}
                points_data[drone_id].coords = [new L.LatLng(drone_lat, drone_lon)];
                points_data[drone_id].heights = [height];
            } else {
                points_data[drone_id].coords.push(new L.LatLng(drone_lat, drone_lon))
                points_data[drone_id].heights.push(height)
            }
        }
        console.log('points_data', points_data)
        for (const [keys, values_data] of Object.entries(points_data)) {
            var coords_arr = values_data.coords
            var heights_arr = values_data.heights

            var firstpolyline = new L.Polyline(coords_arr, {
                // color: getRandomColor(),
                // color: '#ff0000',
                color: random_rgba(),
                // color: 'rgb(255,242,0)',
                weight: 5,
                opacity: 0.9,
                smoothFactor: 0
            });
            firstpolyline.addTo(map);
            map.fitBounds(firstpolyline.getBounds());

            draw_tooltip(map,
                coords = coords_arr[0],
                icon_url = 'static/icons/route/start_circle.png', size = 60, tooltip_text = '')
            draw_tooltip(map,
                coords = coords_arr[coords_arr.length - 1],
                icon_url = 'static/icons/route/finish_circle.png', size = 60, tooltip_text = '')

            for (let j = 0; j < coords_arr.length; j++) {
                var height = heights_arr[j];
                var coords = coords_arr[j];
                if (j !== 0 && j !== coords_arr.length - 1) {
                    place_text(map, coords, height)
                }
                // map.addLayer(strizh_layers[strizh_name])
            }
        }

    });

    map.addLayer(layerDrones)
    // layerDrones.clearLayers();


}