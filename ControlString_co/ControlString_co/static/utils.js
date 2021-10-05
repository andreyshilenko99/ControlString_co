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
