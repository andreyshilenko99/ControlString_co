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


function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}


function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
}


function get_strizhes_ajax() {
    return $.ajax({
        url: '/geo/strizh_view/',
        async: false
    }).responseText
}

function get_skypoints_ajax() {
    return $.ajax({
        url: '/geo/skypoint_view/',
        async: false
    }).responseText
}

function get_radius_borders(radius, center_coords) {
    let r_y = radius * 0.000017784
    let r_x = radius * 0.000008998

    let max_lat = center_coords[0] + r_x
    let max_lon = center_coords[1] + r_y
    let min_lat = center_coords[0] - r_x
    let min_lon = center_coords[1] - r_y

    let c1 = L.latLng(min_lat, min_lon);
    let c2 = L.latLng(max_lat, max_lon);
    return [c1, c2]
}

// leaflet modules
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

function get_map_init(chosen_map_link, set_view = '') {
    var map = L.map(('map'))
    var strizhes_ajax = JSON.parse(get_strizhes_ajax());
    var skypoints_ajax = JSON.parse(get_skypoints_ajax());
    let ind = strizhes_ajax.features.length - 1
    // try to obtain any of the existence objects: srtizh or skypoint, else set default coords
    if (strizhes_ajax.features.length > 0) {
        var initial_coords = [strizhes_ajax.features[ind].properties.lat,
            strizhes_ajax.features[ind].properties.lon];
        var radius_border = get_radius_borders(strizhes_ajax.features[ind].properties.radius,
            initial_coords)
    } else {
        if (skypoints_ajax.features.length > 0) {
            initial_coords = [skypoints_ajax.features[ind].properties.lat,
                skypoints_ajax.features[ind].properties.lon];
            radius_border = get_radius_borders(skypoints_ajax.features[ind].properties.radius,
                initial_coords)
        } else {
            initial_coords = [60.012, 30.455];
            radius_border = [L.latLng(60.006, 30.43), L.latLng(60.018, 30.48)];
        }
    }

    // отображение карты, которая была выбрана, если не выбрана, то берем дефолтную
    if (chosen_map_link.length === 0) {
        if (map_link_default.length !== 0) {
            var map_link = map_link_default;
        } else {
            map_link = 'http://localhost:8000/static/Tiles/Satellite_1/{z}/{x}/{y}.png'
        }
    } else {
        map_link = chosen_map_link

    }
    if (set_view !== '') {
        map.fitBounds(L.latLngBounds(radius_border[1], radius_border[0]));
    } else {
        map.setView(initial_coords, 14);
    }

    L.tileLayer(map_link, {
        attribution: '&copy; Cerrera'
    }).addTo(map);
    return map
}

function get_counter_dict() {
    var strizhes_ajax = JSON.parse(get_strizhes_ajax())
    let drone_counter_obj = {}
    for (let j = 0; j < strizhes_ajax.features.length; j++) {
        var name_st = strizhes_ajax.features[j].properties.name
        drone_counter_obj[name_st] = Math.floor(strizhes_ajax.features[j].properties.seconds_drone_show / SECONDS_WAIT)
    }
    return drone_counter_obj
}

function markerFunction(name, strizh_markers) {
    if (typeof name === 'object') {
        for (let i = 0; i < name.length; i++) {
            var marker_st = strizh_markers[name[i]];
            var position = marker_st.getLatLng();
            // map.setView(position, 15);
            marker_st.openPopup();
        }
    } else {
        marker_st = strizh_markers[name];
        position = marker_st.getLatLng();
        // map.setView(position, 15);
        marker_st.openPopup();
    }

}

// отрисованная траектория должна помещаться в экран, зум устанавливается на средние координаты
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
    // map.setZoom(map.getZoom() - 1);
    // map.setView(mean_coords, map.getZoom() - 1);
    return map
}

function draw_tooltip_main(layer_group, coords, icon_url, size, tooltip_text, is_strizh = false, blinking = '') {
    var tooltip_strizh = new L.Tooltip({
        direction: 'bottom',
        permanent: true,
        noWrap: true,
        opacity: 1
    });
    if (!is_strizh) {
        var logoMarkerStyleStrizh = L.Icon.extend({
            options: {
                iconSize: [size, size],
                iconAnchor: [size / 2, size / 2],
                popupAnchor: [0, size],
                className: blinking
            }
        });
    } else {
        logoMarkerStyleStrizh = L.Icon.extend({
            options: {
                iconSize: [size, size],
                iconAnchor: [size / 2, size],
                popupAnchor: [0, -1 * size],
                className: blinking
            }
        });
    }
    var logoMarkerStrizh = new logoMarkerStyleStrizh({
        iconUrl: icon_url
    });
    var mark = L.marker(coords,
        {icon: logoMarkerStrizh})
        .addTo(layer_group)
    if (tooltip_text) {
        tooltip_strizh.setContent(tooltip_text);
        mark.bindTooltip(tooltip_strizh).openTooltip().on('click', clickZoom);
    }
    return layer_group
}

function draw_tooltip_journal(layer_group, coords, icon_url, size, tooltip_text, is_strizh = false, blinking = '') {
    var tooltip_strizh = new L.Tooltip({
        direction: 'bottom',
        permanent: true,
        noWrap: true,
        opacity: 1
    });
    if (!is_strizh) {
        var logoMarkerStyleStrizh = L.Icon.extend({
            options: {
                iconSize: [size, size],
                iconAnchor: [size / 2, size / 2],
                popupAnchor: [0, size],
                className: blinking
            }
        });
    } else {
        logoMarkerStyleStrizh = L.Icon.extend({
            options: {
                iconSize: [size, size],
                iconAnchor: [size / 2, size],
                popupAnchor: [0, -1 * size],
                className: blinking
            }
        });
    }
    var logoMarkerStrizh = new logoMarkerStyleStrizh({
        iconUrl: icon_url
    });
    var mark = L.marker(coords,
        {icon: logoMarkerStrizh})
        .addTo(layer_group)
    if (tooltip_text) {
        tooltip_strizh.setContent(tooltip_text);
        mark.bindTooltip(tooltip_strizh).openTooltip().on('click', clickZoom);
    }
    return layer_group
}

function place_text(layer_group, coords, text) {
    var tooltip_ = new L.tooltip({
        direction: 'center',
        noWrap: true,
        permanent: true,
        opacity: 1,
        offset: L.point({x: -12, y: -12}),
        className: 'leaflet-tooltip-height'
    }).setContent(text.toString());

    L.marker(coords, {
        opacity: 0,
    })
        .addTo(layer_group)
        .bindTooltip(tooltip_)
        .openTooltip();
    return layer_group
}


function place_number_detection(layer_group, coords, text, height) {

    console.log('coords', coords)
    console.log('coords latlng', [coords.lat, coords.lng])
    var buildingPoints = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [coords.lng, coords.lat]
            },
            "properties": {
                "text": text,
                "radius": 20,
                "height": height
            }
        }
    ];
    var Classroomsamount = new L.geoJson(buildingPoints, {
        pointToLayer: function (feature, latlng) {
            return new L.CircleMarker([latlng.lat, latlng.lng], {radius: feature.properties.radius});
        },
        onEachFeature: function (feature, layer) {
            var text2 = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
                .setContent(feature.properties.text)
                .setLatLng(layer.getLatLng());

            console.log('layer.getLatLng()', layer.getLatLng())
            text2.addTo(layer_group);
            // var height_tooltip = L.tooltip({
            //     direction: 'center',
            //     noWrap: true,
            //     permanent: true,
            //     opacity: 1,
            //     offset: L.point({x: -12, y: -12}),
            //     className: 'leaflet-tooltip-height'
            // })
            //     .setContent(feature.properties.height)
            //     .setLatLng(layer.getLatLng());
            // height_tooltip.addTo(layer_group);

        }
    }).addTo(layer_group);


    // height_tooltip.addTo(layer_group);

    return layer_group
}


