$(function () { // on dom ready

    $.getJSON('/peers', function (peers) {
        let data = {edges: [], nodes: []};

        let gets = [];
        for (let i = 0; i < peers.length; i++) {
            let host = peers[i].host;
            let port = peers[i].port;
            gets.push($.ajax(`http://${host}:${port}/data`));
        }
        $.when(gets).done(function (other_peer_list) {
            for (let i = 0; i < other_peer_list.length; i++) {
                data.edges.push.apply(data.edges, other_peer_list[i].edges);
                data.nodes.push.apply(data.nodes, other_peer_list[i].nodes);
            }

            console.log(data.edges);
            console.log(data.edges[0]);
            console.log(data.edges.length);
            for (let i = 0; i < data.edges.length; i++) {
                data.edges[i].data.id = i;
            }
            console.log(data);

            displayGraph(data);
        });
    });
});

let bytesToSize = function (bytes) {
    let sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Byte';
    let i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};

let displayGraph = function (data) {
    cytoscape({
        container: document.getElementById('cy'),

        style: [
            {
                selector: 'node',
                css: {
                    'content': 'data(id)',
                    'text-valign': 'center',
                    'text-halign': 'center'
                }
            },
            {
                selector: '$node > node',
                css: {
                    'padding-top': '10px',
                    'padding-left': '10px',
                    'padding-bottom': '10px',
                    'padding-right': '10px',
                    'text-valign': 'top',
                    'text-halign': 'center'
                }
            },
            {
                selector: 'edge',
                css: {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 'data(width)',
                    'label': function (ele) {
                        return bytesToSize(parseInt(ele.data('bytes')));
                    }
                }
            }
        ],

        elements: data,
        layout: {
            name: 'dagre',
            rankDir: 'LR',
            padding: 50,
            nodeSep: 40,
            rankSep: 150,
            fit: true
        }
    });
};

})
;
