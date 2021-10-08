var last_id = 0;


function refresh() {
    $.getJSON('/geo/data/', function (data) {
        var current_id = data.features[0].properties.pk;
        if (last_id === 0) {
            last_id = current_id;
        } else if (last_id !== current_id && last_id !== 0) {
            last_id = current_id;
            $.ajax({
                url: "main",
                success: function (data) {
                    $("#detections").load("main #detections");
                }
            });
        }
    })
    $.getJSON('/geo/journal_view_aero/', function (data) {
        var current_id = data.features[0].properties.pk;
        if (last_id === 0) {
            last_id = current_id;
        } else if (last_id !== current_id && last_id !== 0) {
            last_id = current_id;
            $.ajax({
                url: "main",
                success: function (data) {
                    $("#detections").load("main #detections");
                }
            });
        }
    })


}

function get_conditions_ajax() {

    return $.ajax({
        url: '/geo/conditions_view/',
        async: false,
    }).responseText;

}

function get_conditions() {
    var conditions_ajax = JSON.parse(get_conditions_ajax())
    console.log('________________________')
    console.log('conditions_ajax', conditions_ajax)
    console.log('________________________')
    for (let i = 0; i < conditions_ajax.features.length; i++) {
        var uniping_cond = conditions_ajax.features[i].properties.seconds_drone_show;
        var parentID = document.getElementById('information-right')
        console.log('parentID', parentID)
        parentID.getElementsByClassName("temperature_val")[0].innerHTML = 'Температура: ' + uniping_cond;
        parentID.getElementsByClassName("humidity_val")[0].innerHTML = 'Влажность: ' + uniping_cond;
        parentID.getElementsByClassName("cooler")[0].innerHTML = 'Вентилятор: ' + uniping_cond;
        // document.getElementsByClassName("cooler").innerHTML = 'Вентилятор: ' + uniping_cond;
    }

    // return conditions_ajax
}


var SECONDS_WAIT = 2; // seconds, edit here
var DRONE_COUNTER = 4 // number of iterations to clear drone

// number of drones in a trajectory for showing on a map
const MAXDRONES = 50;

setInterval(get_conditions, 10 * 1000);
setInterval(refresh, SECONDS_WAIT * 1000);


function map_init_basic() {
    // drone display time before clearing = SECONDS_WAIT*DRONE_COUNTER
    var map = get_map_init();

    function clickZoom(e) {
        map.setView(e.target.getLatLng(), 15);
    }

// set view to chosen strizh

    var sound = new Howl({
        src: ['static/sound2_3sec.mp3'],
        volume: 0.1,
        onend: function () {
            console.log('_______')
            console.log('PLAYED sound')
            console.log('_______')
        }
    });

    var data_drawn = new Set();
    var ids_drawn = new Set();

    var initial_draw = 0;
    var initial_draw_track = 0;
    var init_tracks_number = 0;
    var initial_draw_strizh = 0;

    var dron_colors = {};
    var flag_state = {};
    var drone_counter = {};
    var drone_layers = {};
    var strizh_layers = {};
    var layers_track = {};
    var DronesTraj = {};
    var pks_tracked = {};

    var col = '#2f80ed';
    var icon_url = 'static/icons/strizh_markers/blue.png';
    var logoMarkerStyle = L.Icon.extend({
        options: {
            iconSize: [46, 46],
            iconAnchor: [23, 23],
            popupAnchor: [0, -46],
            className: 'blinking'
        }
    });
    var tooltip_radius = new L.tooltip();

    function refreshMarkers() {
        $.getJSON('/geo/skypoint_view/', function (skypoint_data) {
            console.log('skypoint_data', skypoint_data)
            for (let n = 0; n < skypoint_data.features.length; n++) {
                let sky_name = skypoint_data.features[n].properties.name;
                let lat = skypoint_data.features[n].properties.lat;
                let lon = skypoint_data.features[n].properties.lon;
                let sky_coords = new L.LatLng(lat, lon)
                draw_tooltip_main(map, coords = sky_coords,
                    icon_url = 'static/icons/skypoint_markers/green.png', size = 60,
                    tooltip_text = sky_name, is_strizh = true)
            }
        });

        var drone_counter_dict = get_counter_dict()
        console.log('drone_counter_dict', drone_counter_dict)
        console.log('drone_counter', drone_counter)
        $.getJSON('/geo/data/', function (data) {
                let arc1;
                let sector1;
                let str1;
                let str_radius;
                $.getJSON('/geo/strizh_view/', function (strizh_data) {
                        let len_strizh_data = strizh_data.features.length;
                        let strizh_map_name = {};
                        let logoMarkerStyleStrizh = L.Icon.extend({
                            options: {
                                iconSize: [80, 80],
                                iconAnchor: [40, 75],
                                popupAnchor: [0, -80],
                                // className: 'blinking'
                            }
                        });
                        // каждые 10 итераций отрисовка стрижа и подписи к нему
                        var strizh_markers = {};
                        for (let j = 0; j < len_strizh_data; j++) {
                            let strizh_name = strizh_data.features[j].properties.name;
                            let strizh_coords = [strizh_data.features[j].properties.lat, strizh_data.features[j].properties.lon];
                            let radius = strizh_data.features[j].properties.radius;
                            strizh_map_name[strizh_data.features[j].properties.name] = [strizh_data.features[j].properties.lat,
                                strizh_data.features[j].properties.lon, radius];
                            let dx_radius = radius * 0.000008998;
                            let radius_x = strizh_map_name[strizh_data.features[j].properties.name][0] - dx_radius;
                            let DRONE_COUNTER = Math.floor(strizh_data.features[j].properties.seconds_drone_show / SECONDS_WAIT)
                            let strizh_radius_coords = [radius_x, strizh_map_name[strizh_data.features[j].properties.name][1]];

                            if (!flag_state[strizh_name] || isEmpty(flag_state[strizh_name])) {
                                for (let i = 0; i < len_strizh_data; i++) {
                                    flag_state[strizh_name] = {};
                                    if (strizh_layers[strizh_name]) {
                                        strizh_layers[strizh_name].clearLayers();
                                    }
                                }
                            }
                            var tooltip_strizh = new L.ClickableTooltip({
                                direction: 'bottom',
                                permanent: true,
                                noWrap: true,
                                opacity: 1
                            });
                            if (isEmpty(flag_state[strizh_name])) {
                                tooltip_strizh.setContent(strizh_name);

                                tooltip_radius = L.tooltip({
                                    color: 'transparent',
                                    direction: 'center',
                                    noWrap: true,
                                    permanent: true,
                                    opacity: 1,
                                    offset: L.point({x: -12, y: -18}),
                                    className: 'leaflet-tooltip-radius'
                                }).setContent(radius.toString() + ' м.');

                                if (!strizh_layers[strizh_name]) {
                                    strizh_layers[strizh_name] = L.layerGroup().addTo(map);
                                }
                                if (complex_state[strizh_name] === 'включен' ||
                                    complex_state[strizh_name] === 'выключен вентилятор') {
                                    if (complex_mode[strizh_name] === 'scan_on') {
                                        // on and scan on, jammer off (3)
                                        col = '#17bd04'
                                        icon_url = 'static/icons/strizh_markers/green_pulse.gif'
                                    } else if (complex_mode[strizh_name] === 'jammer_on') {
                                        // scan off and jammer on (5)
                                        col = '#ff1414'
                                        icon_url = 'static/icons/strizh_markers/red_pulse.gif'
                                    } else {
                                        // on but not active (2)
                                        col = '#2f80ed'
                                        icon_url = 'static/icons/strizh_markers/blue.png'
                                    }
                                } else {
                                    // all off or not working (1)
                                    col = '#4f4f4f'
                                    icon_url = 'static/icons/strizh_markers/gray.png'
                                }

                                arc1 = L.circle(strizh_coords, {
                                    color: col,
                                    fillColor: col,
                                    fillOpacity: 0.01,
                                    radius: radius
                                }).addTo(strizh_layers[strizh_name]);

                                var logoMarkerStrizh = new logoMarkerStyleStrizh({
                                    iconUrl: icon_url
                                });
                                str1 = L.marker([strizh_data.features[j].properties.lat, strizh_data.features[j].properties.lon],
                                    {icon: logoMarkerStrizh})
                                    .addTo(strizh_layers[strizh_name])
                                    .bindTooltip(tooltip_strizh)
                                    .openTooltip()
                                    .on('click', clickZoom);
                                strizh_markers[strizh_name] = str1;

                                str_radius = L.marker(strizh_radius_coords, {
                                    opacity: 0,
                                })
                                    .addTo(strizh_layers[strizh_name])
                                    .bindTooltip(tooltip_radius)
                                // .openTooltip();
                                map.addLayer(strizh_layers[strizh_name])
                            }

                        }
                        if (chosen_strizh !== '' && initial_draw_strizh === 0) {
                            initial_draw_strizh = 1;
                            markerFunction(chosen_strizh, strizh_markers);
                        }

                        let logoMarkerDroneSymb = new logoMarkerStyle({iconUrl: 'static/icons/drons/znak_dron.png'});
                        var len_arr = 20;
                        if (data.features.length < 20) {
                            len_arr = data.features.length;
                        }
                        let arr_drones = [];

                        for (let step = 0; step < len_arr; step++) {
                            arr_drones.push(data.features[step].properties.system_name)
                        }

                        for (let i = 0; i < len_arr; i++) {
                            var d_id = data.features[i].properties.pk;
                            // let radius = parseFloat(data.features[i].properties.area_radius_m);
                            let area_sector_start_grad = parseFloat(data.features[i].properties.area_sector_start_grad);
                            let area_sector_end_grad = parseFloat(data.features[i].properties.area_sector_end_grad);
                            console.log('strizh_map_name', strizh_map_name)
                            console.log('data.features[i].properties.strig_nam', data.features[i].properties.strig_name)

                            let strizh_center = [strizh_map_name[data.features[i].properties.strig_name][0], strizh_map_name[data.features[i].properties.strig_name][1]];
                            let strizh_name = data.features[i].properties.strig_name;
                            let radius = strizh_map_name[data.features[i].properties.strig_name][2];

                            // дрон нарисован
                            if (ids_drawn.has(data.features[i].properties.pk)) {
                                return
                            }
                            // не нарисован
                            else {
                                // задан цвет
                                if (Object.keys(dron_colors).includes(data.features[i].properties.system_name)) {
                                    if (data_drawn.has(data.features[i].properties.system_name)) {
                                        drone_counter[d_id] = [drone_counter_dict[strizh_name], strizh_name];
                                    }
                                }
                                // не задан цвет
                                else if (!Object.keys(dron_colors).includes(data.features[i].properties.system_name)) {
                                    dron_colors[data.features[i].properties.system_name] = getRandomColor();
                                }
                                drone_counter[d_id] = [0, strizh_name];
                            }
                            data_drawn.add(data.features[i].properties.system_name);
                            ids_drawn.add(data.features[i].properties.pk);

                            if (initial_draw === 0) {
                                initial_draw = 1
                                return
                            }
                            // Отрисовка сектора с обновлением + layer Drones
                            // let r_y = 0.004499 //* 4 / 5
                            let r_y = radius * 0.000008998
                            // let r_x = 0.008892 //* 4 / 5
                            let r_x = radius * 0.000017784 //* 4 / 5
                            // scan on, glushenie off  (4)
                            if (complex_mode[strizh_name] === 'scan_on') {
                                tooltip_strizh.setContent(strizh_name);

                                flag_state[strizh_name][d_id] = 1;

                                // flag_state[strizh_name] = 4;
                                strizh_layers[strizh_name].clearLayers()
                                if (!drone_layers[d_id]) {
                                    drone_layers[d_id] = L.layerGroup().addTo(map);
                                }

                                sound.play();
                                col = '#ffc900';
                                icon_url = 'static/icons/strizh_markers/yellow_pulse.gif';
                                logoMarkerStrizh = new logoMarkerStyleStrizh({
                                    iconUrl: icon_url
                                });

                                str1 = L.marker(strizh_center, {icon: logoMarkerStrizh})
                                    .addTo(drone_layers[d_id])
                                    .bindTooltip(tooltip_strizh).openTooltip().on('click', clickZoom);

                                arc1 = L.circle(strizh_center, {
                                    color: '#ffc900',
                                    fillColor: "#ffc900",
                                    fillOpacity: 0.01,
                                    radius: radius
                                });
                                // arc1.addTo(layerDrones);

                                arc1.addTo(drone_layers[d_id]);

                                if (area_sector_start_grad === -1 && area_sector_end_grad === -1) {
                                    let angle = Math.PI / 2;
                                    var d_y = r_y * Math.sin(angle);
                                    var d_x = r_x * Math.cos(angle);

                                } else {
                                    let angle = (90 - (area_sector_start_grad + 30)) / 180 * Math.PI;
                                    d_y = r_y * Math.sin(angle);
                                    d_x = r_x * Math.cos(angle);
                                    sector1 = L.circle(strizh_center, {
                                        color: '#ffc900',
                                        radius: radius,
                                        startAngle: area_sector_start_grad,
                                        endAngle: area_sector_end_grad,
                                        fillOpacity: 0.1
                                    });
                                    if (!drone_layers[d_id]) {
                                        drone_layers[d_id] = L.layerGroup().addTo(map);
                                    }
                                    sector1.addTo(drone_layers[d_id]);
                                }
                            }

                            // Отрисовка подписи к дрону в секторе + layer Drones
                            //TODO current_time
                            let podpis = "<dl style='max-width:400px;word-wrap: break-word;'> " +
                                "<dt> Время </dt> "
                                + "<dd>" + data.features[0].properties.current_time.substr(0, 19) + "</dd>"
                                + "<dt>Имя Дрона </dt>"
                                + "<dd>" + data.features[0].properties.system_name + "</dd>"
                                + "<dt>Комментарий </dt>"
                                + "<dd style=' white-space: pre-wrap;'>" + data.features[0].properties.comment_string + "</dd>"
                                + "</dl>"

                            var tooltip_drone = L.tooltip({
                                maxWidth: 2000,
                                direction: 'top',
                                // noWrap: true,
                                offset: L.point({x: 0, y: -20}),
                                permanent: true,
                                opacity: 0.85,
                                className: 'leaflet-tooltip-own'
                            }).setContent(podpis);

                            // Отрисовка дрона в секторе + layer Drones
                            var drone1 = L.marker([strizh_center[0] + d_y,
                                strizh_center[1] + d_x], {icon: logoMarkerDroneSymb, opacity: 0.6});
                            // drone1.addTo(layerDrones).bindTooltip(tooltip_drone).openTooltip();
                            if (!drone_layers[d_id]) {
                                drone_layers[d_id] = L.layerGroup().addTo(map);
                            }
                            drone1.addTo(drone_layers[d_id]).bindTooltip(tooltip_drone).openTooltip();
                        }
                    }
                );
            }
        )
        console.log('complex_mode', complex_mode)

        // cycle to iterate through layers
        for (const [key, value] of Object.entries(drone_counter)) {
            let name = value[1];
            let dron_id = parseInt(key);
            if (value[0] === drone_counter_dict[name]) {
                delete flag_state[name][dron_id];
                delete drone_counter[key];
                if (drone_layers[key]) {
                    drone_layers[key].clearLayers();
                }
                delete drone_layers[key];
            } else {
                if (drone_layers[key]) {
                    map.addLayer(drone_layers[key]);
                }
                drone_counter[key][0] += 1;
            }
        }

        $.getJSON('/geo/journal_view_aero/', function (data) {
            var tracks_number = 0;
            let data_len = data.features.length;
            if (data_len > MAXDRONES) {
                data_len = 15;
            }
            var ids_tracked = []

            for (let k = data_len - 1; k >= 0; k--) {
                let aero_value = data.features[k].properties
                let height = aero_value.height;
                let pk = aero_value.pk;
                let coords_drone = new L.LatLng(aero_value.drone_lat, aero_value.drone_lon);
                let drone_id = aero_value.drone_id;
                if (!(ids_tracked.includes(drone_id.toString()))) {
                    ids_tracked.push(drone_id.toString())
                }
                if (!(pk in pks_tracked)) {
                    if (!pks_tracked[pk] || isEmpty(pks_tracked[pks_tracked])) {
                        pks_tracked[pk] = 0;
                        if (initial_draw_track !== 0) {
                            sound.play()
                        }
                    }
                } else if (pks_tracked[pk] === DRONE_COUNTER) {
                    continue
                } else {
                    pks_tracked[pk] += 1;
                }
                if (!(drone_id in DronesTraj)) {
                    if (!DronesTraj[drone_id] || isEmpty(DronesTraj[drone_id])) {
                        DronesTraj[drone_id] = {};
                        DronesTraj[drone_id].coords_drone = []
                        DronesTraj[drone_id].counter = 0
                        DronesTraj[drone_id].pks = []
                        DronesTraj[drone_id].heights = [];
                        DronesTraj[drone_id].color = random_rgba();
                    }
                }
                if (!(DronesTraj[drone_id].pks.includes(pk))) {

                    DronesTraj[drone_id].pks.push(pk)
                    DronesTraj[drone_id].counter = 0
                    DronesTraj[drone_id].coords_drone.push(coords_drone)
                    DronesTraj[drone_id].heights.push(height);
                }
            }
            let all_ids = Object.keys(DronesTraj);
            let difference = all_ids.filter(x => !ids_tracked.includes(x));

            for (const [key, values_data] of Object.entries(DronesTraj)) {
                if (initial_draw_track === 0) {
                    init_tracks_number += values_data.pks.length
                }
                tracks_number += values_data.pks.length

                if (DronesTraj[key].counter >= DRONE_COUNTER) {
                    layers_track[key].clearLayers()
                    continue
                }
                if (!layers_track[key]) {

                    layers_track[key] = L.layerGroup();

                } else {
                    layers_track[key].clearLayers()
                }
                var coords_arr = values_data.coords_drone;
                var heights_arr = values_data.heights

                var polyline = new L.Polyline(coords_arr, {
                    color: values_data.color,
                    weight: 5,
                    opacity: 0.9,
                    smoothFactor: 0
                }).addTo(layers_track[key])

                layers_track[key] = draw_tooltip_main(layers_track[key],
                    coords = coords_arr[0],
                    icon_url = 'static/icons/route/start.svg', size = 60, tooltip_text = '')
                layers_track[key] = draw_tooltip_main(layers_track[key],
                    coords = coords_arr[coords_arr.length - 1],
                    icon_url = 'static/icons/drons/dron_top.png', size = 60,
                    tooltip_text = '', blinking = 'blinking')
                for (let j = 0; j < coords_arr.length; j++) {
                    let height = heights_arr[j];
                    let coords = coords_arr[j];
                    if (j !== 0 && j !== coords_arr.length - 1) {
                        layers_track[key] = place_text(layers_track[key], coords, height)
                    }
                    // map.addLayer(strizh_layers[strizh_name])
                }
                DronesTraj[key].counter += 1;
            }
            for (let key of Object.keys(DronesTraj)) {
                if (tracks_number !== init_tracks_number) {
                    layers_track[key].addTo(map)
                    map.addLayer(layers_track[key])
                    // sound.play();
                }
            }
            initial_draw_track = 1;
        })
    }

    refreshMarkers()
    setInterval(refreshMarkers, SECONDS_WAIT * 1000);
}