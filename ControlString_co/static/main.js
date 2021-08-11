var last_id = 0;

function refresh() {
    $.getJSON('/geo/data/', function (data) {
        var current_id = data.features[0].properties.pk;
        if (last_id !== current_id && last_id !== 0) {
            last_id = current_id;
            console.log('new_drone')
            $.ajax({
                url: "main",
                success: function (data) {
                    $('#detections').replaceWith($('#detections', data)); // NOTE this
                }
            });
        }
    })


}

var SECONDS_WAIT = 5; // seconds, edit here
var DRONE_COUNTER = 15 // number of iterations to clear drone
// drone display time before clearing = SECONDS_WAIT*DRONE_COUNTER
setInterval(refresh, SECONDS_WAIT * 1000);

function map_init_basic(map, options) {

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


    var dron_colors = {};
    // var layerDrones = L.layerGroup().addTo(map);
    var layerStrizhes = L.layerGroup().addTo(map);

    var data_drawn = new Set();
    var ids_drawn = new Set();
    var initial_draw = 0;
    var counter_periodic = -1;
    // var counter_drone_period = 0
    var drone_counter = {};
    var drone_layers = {};
    var strizh_layers = {};


    function refreshMarkers() {

        counter_periodic = counter_periodic + 1;

        console.log('REFRESHED')

        $.getJSON('/geo/data/', function (data) {
                let arc1;
                let circle1;
                let str1;
                let name1;
                let logoMarkerStyle = L.Icon.extend({
                    options: {
                        iconSize: [46, 46],
                        iconAnchor: [23, 23],
                        popupAnchor: [0, -46],
                        className: 'blinking'
                    }
                });

                $.getJSON('/geo/strizh_view/', function (strizh_data) {
                        let len_strizh_data = strizh_data.features.length;
                        let strizh_map_name = {};
                        let logoMarkerStyleStrizh = L.Icon.extend({
                            options: {
                                iconSize: [85, 90],
                                iconAnchor: [38, 86],
                                popupAnchor: [0, -80],
                                // className: 'blinking'
                            }
                        });

                        // каждые 10 итераций отрисовка стрижа и подписи к нему
                        for (let j = 0; j < len_strizh_data; j++) {
                            var strizh_name = strizh_data.features[j].properties.name;
                            var strizh_coords = [strizh_data.features[j].properties.lat,
                                strizh_data.features[j].properties.lon]

                            strizh_map_name[strizh_data.features[j].properties.name] = [strizh_data.features[j].properties.lat,
                                strizh_data.features[j].properties.lon, strizh_data.features[j].properties.name];
                            console.log('counter_periodic', counter_periodic)


                            if (counter_periodic === 2) {
                                counter_periodic = 0;
                                for (let i=0; i < len_strizh_data; i++) {
                                    strizh_layers[strizh_data.features[j].properties.name].clearLayers();
                                }
                            }
                            if (counter_periodic === 0) {
                                var tooltip = L.tooltip({
                                    direction: 'bottom',
                                    noWrap: true,
                                    permanent: true,
                                    opacity: 0.85
                                })
                                    .setContent(strizh_name);
                                console.log(complex_state[strizh_name])
                                console.log(complex_mode)
                                if (!strizh_layers[strizh_name]) {
                                    strizh_layers[strizh_name] = L.layerGroup().addTo(map);
                                }
                                if (complex_state[strizh_name] === 'включен') {
                                    if (complex_mode[strizh_name] === 'scan_on') {
                                        // on and scan on, jammer off (3)
                                        var col = '#17bd04'
                                        icon_url = 'static/icons/strizh_markers/green.png'
                                    }
                                    else if (complex_mode[strizh_name] === 'jammer_on') {
                                        // scan off and jammer on (5)
                                        var col = '#e5de14'
                                        icon_url = 'static/icons/strizh_markers/yellow.png'
                                    }
                                    else {
                                        // on but not active (2)
                                        var col = '#2f80ed'
                                        icon_url = 'static/icons/strizh_markers/blue.png'
                                    }
                                    // icon_url = 'static/icons/strizh_green_pulse.gif'
                                } else {
                                    // all off or not working (1)
                                    var col = '#4f4f4f'
                                    var icon_url = 'static/icons/strizh_markers/gray.png'
                                }

                                arc1 = L.circle(strizh_coords, {
                                    color: col,
                                    fillColor: col,
                                    fillOpacity: 0.1,
                                    radius: 500
                                }).addTo(strizh_layers[strizh_name]);
                                var logoMarkerStrizh = new logoMarkerStyleStrizh({
                                    iconUrl: icon_url
                                });
                                str1 = L.marker([strizh_data.features[j].properties.lat,
                                    strizh_data.features[j].properties.lon], {icon: logoMarkerStrizh})
                                    .addTo(strizh_layers[strizh_name])
                                    .bindTooltip(tooltip).openTooltip();
                            }
                            map.addLayer(strizh_layers[strizh_name])
                        }
                        let logoMarker = new logoMarkerStyle({iconUrl: 'static/icons/dron_top.png'});

                        if (data.features.length < 20) {
                            var len_arr = data.features.length;
                        } else {
                            var len_arr = 20;
                        }
                        let arr_drones = [];

                        for (let step = 0; step < len_arr; step++) {
                            arr_drones.push(data.features[step].properties.system_name)
                        }

                        for (let i = 0; i < len_arr; i++) {
                            var d_id = data.features[i].properties.pk;
                            let radius = parseFloat(data.features[i].properties.area_radius_m);
                            let area_sector_start_grad = parseFloat(data.features[i].properties.area_sector_start_grad);
                            let area_sector_end_grad = parseFloat(data.features[i].properties.area_sector_end_grad);
                            let strizh_center = [strizh_map_name[data.features[i].properties.strig_name][0],
                                strizh_map_name[data.features[i].properties.strig_name][1]];

                            // дрон нарисован
                            console.log('ids_drawn', ids_drawn)
                            if (ids_drawn.has(data.features[i].properties.pk)) {
                                return
                            }
                            // не нарисован
                            else {
                                // задан цвет
                                if (Object.keys(dron_colors).includes(data.features[i].properties.system_name)) {
                                    if (data_drawn.has(data.features[i].properties.system_name)) {
                                        // counter_drone_period = 3;
                                        drone_counter[d_id] = DRONE_COUNTER;

                                    }
                                }
                                // не задан цвет
                                else if (!Object.keys(dron_colors).includes(data.features[i].properties.system_name)) {
                                    dron_colors[data.features[i].properties.system_name] = getRandomColor();
                                }
                                // counter_drone_period = 0;
                                drone_counter[d_id] = 0;
                            }
                            data_drawn.add(data.features[i].properties.system_name);
                            ids_drawn.add(data.features[i].properties.pk);

                            if (initial_draw === 0) {
                                initial_draw = 1
                                return
                            }
                            // Отрисовка сектора с обновлением + layer Drones
                            let r_y = 0.004499 * 4 / 5
                            let r_x = 0.008892 * 4 / 5

                            if (area_sector_start_grad === -1 && area_sector_end_grad === -1) {
                                let angle = (90 - (area_sector_start_grad)) / 180 * Math.PI;
                                var d_y = 0.004499 * Math.sin(angle);
                                var d_x = 0.008892 * Math.cos(angle);
                                arc1 = L.circle(strizh_center, {
                                    color: '#0062ea',
                                    fillColor: "#e0aa4e",
                                    fillOpacity: 0.2,
                                    radius: radius
                                });
                                // arc1.addTo(layerDrones);
                                if (!drone_layers[d_id]) {
                                    drone_layers[d_id] = L.layerGroup().addTo(map);
                                }
                                arc1.addTo(drone_layers[d_id]);
                            } else {
                                let angle = (90 - (area_sector_start_grad + 30)) / 180 * Math.PI;
                                var d_y = r_y * Math.sin(angle);
                                var d_x = r_x * Math.cos(angle);
                                circle1 = L.circle(strizh_center, {
                                    radius: radius,
                                    startAngle: area_sector_start_grad,
                                    endAngle: area_sector_end_grad
                                });
                                // circle1.addTo(layerDrones);
                                if (!drone_layers[d_id]) {
                                    drone_layers[d_id] = L.layerGroup().addTo(map);
                                }
                                circle1.addTo(drone_layers[d_id]);
                            }

                            // Отрисовка подписи к дрону в секторе + layer Drones
                            //TODO current_time
                            let podpis = data.features[i].properties.detection_time.substr(0, 19) + '.  ' +
                                data.features[i].properties.system_name + '.  ' + data.features[i].properties.comment_string

                            var tooltip_drone = L.tooltip({
                                maxWidth: 2000,
                                direction: 'top',
                                // noWrap: true,
                                offset: L.point({x: 0, y: -20}),
                                permanent: true,
                                opacity: 0.85,
                                className: 'leaflet-tooltip-own'
                            })
                                .setContent(podpis);

                            // Отрисовка дрона в секторе + layer Drones
                            var drone1 = L.marker([strizh_center[0] + d_y,
                                strizh_center[1] + d_x], {icon: logoMarker});
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
        // console.log('counter_drone_period', counter_drone_period)
        console.log('drone_counter', drone_counter);
        console.log('drone_layers', drone_layers);
        // new cycle to iterate through layers
        for (const [key, value] of Object.entries(drone_counter)) {
            if (value === DRONE_COUNTER) {
                if (drone_layers[key]) {

                    drone_layers[key].clearLayers();
                }
                drone_counter[key] = 0;
            } else {
                if (drone_layers[key]) {
                    map.addLayer(drone_layers[key])
                }
                drone_counter[key] += 1;
            }
        }
    }

    refreshMarkers()
    setInterval(refreshMarkers, SECONDS_WAIT * 1000);
}