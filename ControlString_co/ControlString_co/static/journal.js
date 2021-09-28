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


function refresh_map(map) {
    var map1 = L.tileLayer('http://localhost:8000/static/q_tiles/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">566</a>'
    });
    var map2 = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    });

    map = L.map('map', {
        layers: [map1] // only add one!
    }).setView([60.013674, 30.452474], 15);

    var baseLayers = {
        "OSM Mapnik": map1,
        "Landscape": map2
    };
    var xx = L.control.layers(baseLayers).addTo(map);
    console.log('control', xx)
    return map
}


var seconds_wait = 3; // seconds, edit here
setInterval(refresh, seconds_wait * 1000);

// setInterval(refresh_map, seconds_wait * 1000);


function map_init_basic(map, options) {
    map = refresh_map(map)
    console.log('map', map)
    L.ClickableTooltip = L.Tooltip.extend({
        onAdd: function (map) {
            L.Tooltip.prototype.onAdd.call(this, map);
            var el = this.getElement(),
                self = this;
            el.addEventListener('click', function () {
                self.fire("click");
            });
            el.style.pointerEvents = 'auto';
        }
    });

    function clickZoom(e) {
        map.setView(e.target.getLatLng(), 15);
    }

    function track_map_bounds(map, coords_arr) {
        let coords_lat = [];
        let coords_lon = [];
        console.log('coords_arr:', coords_arr);
        for (let n = 0; n < coords_arr.length; n++) {
            coords_lat.push(coords_arr[n].lat)
            coords_lon.push(coords_arr[n].lng)
        }
        const sum_lat = coords_lat.reduce((a, b) => a + b, 0);
        const sum_lon = coords_lon.reduce((a, b) => a + b, 0);
        const avg_lat = (sum_lat / coords_lat.length) || 0;
        const avg_lon = (sum_lon / coords_lon.length) || 0;
        let mean_coords = new L.LatLng(avg_lat, avg_lon);
        let min_lat = Math.min.apply(Math, coords_lat)
        let min_lon = Math.min.apply(Math, coords_lon)
        let max_lat = Math.max.apply(Math, coords_lat)
        let max_lon = Math.max.apply(Math, coords_lon)
        let c1 = L.latLng(min_lat, min_lon);
        let c2 = L.latLng(max_lat, max_lon);
        map.fitBounds(L.latLngBounds(c2, c1));
        console.log('map.getZoom()', map.getZoom())
        console.log('mean_coords:', mean_coords);
        map.setZoom(map.getZoom() - 1);
        map.setView(mean_coords, map.getZoom() - 1);
        return map
    }

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
        var tooltip_strizh = new L.ClickableTooltip({
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
            tooltip_strizh.setContent(tooltip_text);
            mark.bindTooltip(tooltip_strizh).openTooltip().on('click', clickZoom);
        }
    }

    function place_text(map, coords, text) {
        var tooltip_ = new L.Tooltip({
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
            .openTooltip().on('click', clickZoom);
    }

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
                    strizh_data.features[j].properties.lon, strizh_data.features[j].properties.radius];

                console.log('strizh_data: ', strizh_data.features[j].properties)

                if (counter_periodic <= 10) {
                    if (counter_periodic === 10) {
                        counter_periodic = 0;
                        layerStrizhes.clearLayers();
                    }
                    if (counter_periodic === 0) {
                        var tooltip = new L.ClickableTooltip({
                            direction: 'bottom',
                            noWrap: true,
                            permanent: true,
                            opacity: 0.85
                        })
                            .setContent(strizh_data.features[j].properties.name);

                        str1 = L.marker([strizh_data.features[j].properties.lat,
                            strizh_data.features[j].properties.lon], {icon: logoMarkerStrizh}).addTo(layerStrizhes)
                            .bindTooltip(tooltip).openTooltip().on('click', clickZoom);
                    }
                    map.addLayer(layerStrizhes)
                }
            }
            let logoMarker = new logoMarkerStyle({iconUrl: 'static/icons/drons/znak_dron.png', color: '#ff0000'});
            console.log('data ', data)
            // статичная отрисовка радиуса вокруг стрижа, стрижа и его подписи
            if (data.features.length !== 0) {
                // let radius = parseFloat(data.features[0].properties.area_radius_m);
                let area_sector_start_grad = parseFloat(data.features[0].properties.area_sector_start_grad);
                let area_sector_end_grad = parseFloat(data.features[0].properties.area_sector_end_grad);
                console.log('strizh_map_name', strizh_map_name)
                console.log('data.features[0].properties.strig_name', data.features[0].properties.strig_name)
                console.log('strizh_map_name[data.features[0].properties.strig_name]',
                    strizh_map_name[data.features[0].properties.strig_name])

                console.log('strizh_map_name[data.features[0].properties.strig_name]',
                    strizh_map_name[data.features[0].properties.strig_name])

                let strizh_center = [strizh_map_name[data.features[0].properties.strig_name][0], strizh_map_name[data.features[0].properties.strig_name][1]];
                var radius = parseFloat(strizh_map_name[data.features[0].properties.strig_name][2])

                // Отрисовка сектора с обновлением + layerDrones
                let r_y = radius * 0.000008998
                let r_x = radius * 0.000017784

                if (area_sector_start_grad === -1 && area_sector_end_grad === -1) {
                    let angle = (90 - (area_sector_start_grad)) / 180 * Math.PI;
                    var d_y = r_y * Math.sin(angle);
                    var d_x = r_x * Math.cos(angle);
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

                if (chosen_complex_to_show !== '') {
                    // initial_draw_strizh = 1;

                    // // let r_y = Math.abs((radius - 400)) * 0.000008998
                    let r_y = radius * 0.000008998
                    // // let r_x = Math.abs((radius - 400)) * 0.000017784
                    let r_x = radius * 0.000017784


                    let max_lat = strizh_center[0] + r_x
                    let max_lon = strizh_center[1] + r_y
                    let min_lat = strizh_center[0] - r_x
                    let min_lon = strizh_center[1] - r_y

                    let c1 = L.latLng(min_lat, min_lon);
                    let c2 = L.latLng(max_lat, max_lon);

                    console.log('map.getZoom()', map.getZoom())
                    map.fitBounds(L.latLngBounds(c2, c1), {padding: [10, 10]});
                    // map.setZoom(map.getZoom() );
                    map.setView(strizh_center, map.getZoom() - 2);
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
                    .bindTooltip(tooltip_drone).openTooltip().on('click', clickZoom);
            }
        });


        console.log('chosen_complex_to_show', chosen_complex_to_show)
    })


    $.getJSON('/geo/drone_journal_view_traj/', function (data) {
        console.log('data    drone_journal_view_traj', data)
        // var points_coords = {}
        var points_data = {}
        var n_elements = data.features.length;

        draw_tooltip(map,
            coords = [60.013674, 30.442474],
            icon_url = 'static/icons/controller/pad.svg', size = 50, tooltip_text = '')


        draw_tooltip(map,
            coords = [60.015, 30.47],
            icon_url = 'static/icons/home/home2.png', size = 50, tooltip_text = '')

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

            var polyline = new L.Polyline(coords_arr, {
                // color: getRandomColor(),
                color: '#ff775c',
                // color: random_rgba(),
                // color: 'rgb(255,242,0)',
                weight: 5,
                opacity: 0.9,
                smoothFactor: 0
            });
            polyline.addTo(map);
            // map.fitBounds(polyline.getBounds());

            draw_tooltip(map,
                coords = coords_arr[coords_arr.length - 1],
                icon_url = 'static/icons/route/start.svg', size = 60, tooltip_text = '')
            draw_tooltip(map,
                coords = coords_arr[0],
                icon_url = 'static/icons/route/stop.svg', size = 60, tooltip_text = '')

            if (chosen_complex_to_show !== '') {
                // initial_draw_strizh = 1;
                // let avg = average(coords_arr)
                map = track_map_bounds(map, coords_arr)

            }

            for (let j = 0; j < coords_arr.length; j++) {
                let height = heights_arr[j];
                let coords = coords_arr[j];
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