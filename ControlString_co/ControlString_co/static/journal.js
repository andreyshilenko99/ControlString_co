var last_id = 0;
var last_id_sky = 0;

function refresh() {

    $.getJSON('/geo/journal_view/', function (data) {
        var current_id = data.features[0].properties.pk;
        if (last_id === 0) {
            last_id = current_id;
        } else if (last_id !== current_id && last_id !== 0) {
            last_id = current_id;
            $.ajax({
                url: "journal",
                success: function (data) {
                    $("#detections").load("journal #detections");
                    // $('#detections').replaceWith($('#detections', data));
                }
            });

        }

    })
}

function refresh_sky() {
    $.getJSON('/geo/journal_view_aero/', function (data) {
        var current_id = data.features[0].properties.pk;
        if (last_id_sky === 0) {
            last_id_sky = current_id;
        } else if (last_id_sky !== current_id && last_id_sky !== 0) {
            last_id_sky = current_id;
            $.ajax({
                url: "journal",
                success: function (data) {
                    $("#detections").load("journal #detections");
                    // $('#detections').replaceWith($('#detections', data));
                }
            });
        }
    })
}

var seconds_wait = 1; // seconds, edit here

// setInterval(refresh, seconds_wait * 1000);
// setInterval(refresh_sky, seconds_wait * 1000);


function map_init_basic() {
    var map = get_map_init(chosen_map_link, chosen_complex_to_show);

    var layerDrones = L.layerGroup().addTo(map);
    var layerStrizhes = L.layerGroup().addTo(map);

    var counter_periodic = -1;
    counter_periodic = counter_periodic + 1;

    // Отрисовка иконки skypoint
    $.getJSON('/geo/skypoint_view/', function (skypoint_data) {
        console.log('skypoint_data', skypoint_data)
        for (let n = 0; n < skypoint_data.features.length; n++) {
            let sky_name = skypoint_data.features[n].properties.name;
            let lat = skypoint_data.features[n].properties.lat;
            let lon = skypoint_data.features[n].properties.lon;
            let sky_coords = new L.LatLng(lat, lon)
            draw_tooltip_journal(layerStrizhes, coords = sky_coords,
                icon_url = 'static/icons/skypoint_markers/green.png', size = 60,
                tooltip_text = sky_name, is_strizh = true)
        }
    });

    // отрисовка радиуса вокруг стрижа
    $.getJSON('/geo/drone_journal/', function (data) {
            let arc1;
            let str1;
            let logoMarkerStyle = L.Icon.extend({
                options: {
                    iconSize: [46, 46],
                    iconAnchor: [23, 23],
                    popupAnchor: [0, -46],
                }
            });

            $.getJSON('/geo/strizh_view/', function (strizh_data) {
                let len_strizh_data = strizh_data.features.length;
                let strizh_map_name = {};
                let logoMarkerStyleStrizh = L.Icon.extend({
                    options: {
                        iconSize: [80, 80],
                        iconAnchor: [40, 75],
                        popupAnchor: [0, -80]
                    }
                });
                var logoMarkerStrizh = new logoMarkerStyleStrizh({
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
                            }).setContent(strizh_data.features[j].properties.name);

                            str1 = L.marker([strizh_data.features[j].properties.lat,
                                strizh_data.features[j].properties.lon], {icon: logoMarkerStrizh}).addTo(layerStrizhes)
                                .bindTooltip(tooltip).openTooltip().on('click', clickZoom);
                        }
                        map.addLayer(layerStrizhes)
                    }
                }
                let logoMarker = new logoMarkerStyle({iconUrl: 'static/icons/drons/znak_dron.png', color: '#ff0000'});
                console.log('data ', data)
                // отрисовка радиуса вокруг стрижа, стрижа и его подписи
                if (data.features.length !== 0) {
                    let area_sector_start_grad = parseFloat(data.features[0].properties.area_sector_start_grad);
                    let area_sector_end_grad = parseFloat(data.features[0].properties.area_sector_end_grad);

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
                        d_y = r_y * Math.sin(angle);
                        d_x = r_x * Math.cos(angle);
                        arc1 = L.circle(strizh_center, {
                            color: '#0296f8',
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
                        console.log('strizh_map_name[chosen_complex_to_show]', strizh_map_name[chosen_complex_to_show]);
                        console.log('radius', radius);
                        // initial_draw_strizh = 1;
                        var radius_border = get_radius_borders(strizh_map_name[chosen_complex_to_show][2],
                            [strizh_map_name[chosen_complex_to_show][0],
                                strizh_map_name[chosen_complex_to_show][1]])

                        if (radius >= 700 && radius <= 1800) {
                            console.log('13');
                            var zoom_level = 13;
                        } else if (radius < 400) {
                            console.log('15');
                            zoom_level = 15;
                        } else if (radius >= 400 && radius < 700) {
                            console.log('14');
                            zoom_level = 14;
                        } else {
                            console.log('14444');
                            zoom_level = 14
                        }
                        map.fitBounds(L.latLngBounds(radius_border[0], radius_border[1]));

                        map.setView([strizh_map_name[chosen_complex_to_show][0],
                            strizh_map_name[chosen_complex_to_show][1]], zoom_level);


                        // map.setZoom(map.getZoom() );
                        // map.flyTo(strizh_center, map.getZoom() - 1);
                    }

                    // Отрисовка подписи к дрону в секторе + layerDrones
                    let podpis = "<dl style='overflow-wrap: break-word;" +
                        "word-wrap: break-word; white-space: nowrap;'> " +
                        "<dt> Время </dt> "
                        + "<dd>" + data.features[0].properties.current_time.substr(0, 19) + "</dd>"
                        + "<dt>Имя Дрона </dt>"
                        + "<dd>" + data.features[0].properties.system_name + "</dd>"
                        + "<dt>Комментарий </dt>";
                    if (data.features[0].properties.comment_string.length >= 70) {
                        podpis += "<dd>" + data.features[0].properties.comment_string.slice(0, 70) + "</dd>"
                            + "<dd>" + data.features[0].properties.comment_string.slice(70, data.features[0].properties.comment_string.length) + "</dd>" + "<br>"
                            + "</dl>"
                    } else {
                        podpis += "<dd>" + data.features[0].properties.comment_string + "</dd>"
                            + "</dl>"
                    }
                    var tooltip_drone = L.tooltip({
                        maxWidth: 400,
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
        }
    )

// отрисовка траектории - skypoint
    $.getJSON('/geo/drone_journal_view_traj/', function (data) {
        var points_data = {}
        var n_elements = data.features.length;

        // отрисовка координат дома (пока не доступно их получение)
        // draw_tooltip_journal(map,
        //     coords = [lat, long],
        //     icon_url = 'static/icons/home/home2.png', size = 50, tooltip_text = '')

        for (let i = 0; i < n_elements; i++) {
            var aero_value = data.features[i].properties;
            var drone_id = aero_value.drone_id;
            var drone_lat = aero_value.drone_lat;
            var drone_lon = aero_value.drone_lon;
            var remote_lat = aero_value.remote_lat;
            var remote_lon = aero_value.remote_lon;
            var height = aero_value.height;
            if (!points_data[drone_id] || isEmpty(points_data[drone_id])) {
                points_data[drone_id] = {}
                points_data[drone_id].coords = [new L.LatLng(drone_lat, drone_lon)];
                points_data[drone_id].remote_coords = [new L.LatLng(remote_lat, remote_lon)];
                points_data[drone_id].heights = [height];
            } else {
                points_data[drone_id].coords.push(new L.LatLng(drone_lat, drone_lon))
                points_data[drone_id].remote_coords.push(new L.LatLng(remote_lat, remote_lon))
                points_data[drone_id].heights.push(height)
            }
        }
        for (const [keys, values_data] of Object.entries(points_data)) {
            var coords_arr = values_data.coords
            var coords_remote_arr = values_data.remote_coords
            var heights_arr = values_data.heights

            var polyline = new L.Polyline(coords_arr, {
                color: '#ff775c',
                weight: 5,
                opacity: 0.9,
                smoothFactor: 0
            });
            polyline.addTo(map);
            // map.fitBounds(polyline.getBounds());

            draw_tooltip_journal(map,
                coords = coords_arr[coords_arr.length - 1],
                icon_url = 'static/icons/route/start.svg', size = 60, tooltip_text = '')
            draw_tooltip_journal(map,
                coords = coords_arr[0],
                icon_url = 'static/icons/route/stop.svg', size = 60, tooltip_text = '')
            draw_tooltip_journal(map,
                coords = coords_remote_arr[coords_remote_arr.length - 1],
                icon_url = 'static/icons/controller/pad.svg', size = 50,
                tooltip_text = '')
            if (chosen_complex_to_show !== '') {
                map = track_map_bounds(map, coords_arr)
            }
            for (let j = 0; j < coords_arr.length; j++) {
                let height = heights_arr[j];
                let coords = coords_arr[j];
                let last_idx = coords_arr.length - 1
                if (j !== 0 && j !== last_idx) {
                    // place_text(map, coords, height + ' м.')
                    place_text(map, coords, height)
                    map = place_number_detection(map, coords, (last_idx - j).toString(), height)
                }
            }
        }
    });

    map.addLayer(layerDrones)

}