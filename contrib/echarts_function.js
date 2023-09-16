let graph;

const gitRepoUrl = 'https://<FQDN or IP>/<Username>/<Project Name>/-/raw/<Branch>/network_topology_as_a_code.json';

function Get(Url) {
var Httpreq = new XMLHttpRequest();
Httpreq.open("GET", Url, false);
Httpreq.send();
return Httpreq.responseText;
}

graph = JSON.parse(Get(gitRepoUrl))

echartsInstance.on("click", (params) => {
window.open(
    params.data.url
);
});

return {
tooltip: {
    formatter: function (params) {
    return params.data.iframe
    }
},
legend: [
    {
    data: graph.categories.map(function (a) {
        return a.name;
    })
    }
],
series: [
    {
    name: 'Network Topology as a Code',
    type: 'graph',
    layout: 'force',
    data: graph.nodes,
    links: graph.links,
    categories: graph.categories,
    roam: true,
    force: {
        edgeLength: 150,
        repulsion: 500,
        friction: 0.2,
        gravity: 0
    },
    label: {
        show: true,
        position: 'left',
        formatter: '{b}',
    },
    autoCurveness: true,
    lineStyle: {
        color: 'source',
    },
    emphasis: {
        focus: 'adjacency',
        lineStyle: {
        width: 10
        }
    },
    draggable: true,
    }
]
};