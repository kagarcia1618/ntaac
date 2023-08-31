# Network Topology as a Code

By: Kenneth Acar Garcia

## Overview

This solution originated from the concept of dynamically rendering a network topology from a network source-of-truth data source, coupled with an interactive GUI. This interface offers the flexibility to present essential network statistics either for individual devices or specific links.

## Pre-Requisite

| No.  | Application                     | Version |
|:----:|:-------------------------------:|:-------:|
| 1.   | NetBox                          | 3.5.6   |
| 2.   | Grafana                         | 9.5.2   |
| 3.   | Gitlab                          | 16.3.0  |
| 4.   | Grafana Plugin - Apache ECharts | 4.3.1   |

### NetBox

- NetBox as the network source-of-truth will host the necessary data for individual devices and specific links which includes the following details but not limited to hostname, interface name and role.
- NetBox's custom script will function as dataset generator in JSON format below. This dataset will then be committed into a local gitlab repository using python via API either manually or triggered by a device record change in NetBox.

    The dataset currently contains the following records:

    - Categories
        - List of device roles from NetBox

    - Nodes
        - Device information containing the following details
            - Name - hostname of the device
            - Category - role of the device
            - URL - optional field that will provide URL redirection feature once you click the device from the network topology GUI
            - Iframe - optional field that will provide embedded iframe visual once you hover over the device from the network topology GUI

    - Links
        - Interface information containing the following details
            - Source - Source device hostname
            - Source_int - Source device interface name
            - Target - Target device hostname
            - Target_int - Target device interface name
            - URL - optional field that will provide URL redirection feature once you click the link from the network topology GUI
            - Iframe - optional field that will provide embedded iframe visual once you hover over the link from the network topology GUI

    ```
    {
        "categories": [
            {
                "name": "Role_A"
            },
            {
                "name": "Role_B"
            },=
        ],
        "nodes": [
            {
                "name": "Device_A",
                "category": "Role_A",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"
            },
            {
                "name": "Device_B",
                "category": "Role_B",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_B&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_B&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"            },
            {
                "name": "Device_C",
                "category": "Role_B",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_C&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_C&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"            }
        ],
        "links": [
            {
                "source": "Device_A",
                "source_int": "Gi0",
                "target": "Device_B",
                "target_int: "Gi0",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&var-name=Gi0&panelId=XX&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&var-name=Gi0&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"     
            },
            {
                "source": "Device_B",
                "source_int": "Gi1",
                "target": "Device_C",
                "target_int: "Gi1",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_B&var-name=Gi1&panelId=XX&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_B&var-name=Gi1&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"     
            },
            {
                "source": "Device_A",
                "source_int": "Gi1",
                "target": "Device_C",
                "target_int: "Gi0",
                "url": "https://grafana.local/d/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&var-name=Gi1&panelId=XX&from=now-12h&to=now",
                "iframe": "`<iframe src='https://grafana.local/d-solo/.../device-utilization-dashboard/?orgId=X&var-hostname=Device_A&var-name=Gi1&panelId=XX&from=now-12h&to=now' width='600' height='250' frameborder='0'></iframe>`"  
            }
        ]
    }
    ```

### Grafana

- Grafana will be used here as the network telemetry statistics dashboard which contains the following information:
    
    - Device Statistics
        - CPU Usage
        - Memory Usage
        - Interface Usage

    - Interface Statistics
        - Inbound/Outbound Traffic Utilization

### Gitlab

- Gitlab will be used here as the repository of generated dataset in JSON format by the NetBox Custom Script
- JSON format dataset will then be fetched by Apache Echarts grafana plugin to dynamically render the network topology with interactive GUI

### Grafana Plugin - Apache Echarts

- Apache Echarts is the key component that consolidates the pieces of information from NetBox, Grafana and Gitlab that renders a dynamic network topology from the JSON format data
- Apache Echarts has a parameter named `Function` that contains the code in javascript languange for ingesting the JSON format data from Gitlab repository.

    ```
    let graph;

    const gitRepoUrl = 'https://{FQDN or IP}/{Owner}/{Project Name}/-/raw/{Branch}/{Filename}.json';

    function Get(Url) {
    var Httpreq = new XMLHttpRequest(); // a new request
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
        // selectedMode: 'single',
        data: graph.categories.map(function (a) {
            return a.name;
        })
        }
    ],
    series: [
        {
        name: 'Les Miserables',
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
            gravity: 0.25
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
    ```