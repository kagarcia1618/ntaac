# **Network Topology as a Code**

By: Kenneth Acar Garcia

## Overview

This solution originated from the concept of dynamically rendering a network topology from a network source-of-truth data source, coupled with an interactive GUI. This interface offers the flexibility to present essential network statistics either for individual devices or specific links.

## Pre-Requisite

| No.  | Application                     | Version |
|:----:|:-------------------------------:|:-------:|
| 1.   | NetBox                          | 3.5.6   |
| 2.   | Grafana                         | 9.5.2   |
| 3.   | Gitlab                          | 16.3.0  |
| 4.   | Grafana Plugin - Apache ECharts | 5.1.0   |

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
            - Target - Target device hostname
            - URL - optional field that will provide URL redirection feature once you click the link from the network topology GUI
            - Iframe - optional field that will provide embedded iframe visual once you hover over the link from the network topology GUI

    Please refer to this [link](https://github.com/kagarcia1618/ntaac) for the example NetBox custom script that generates this JSON dataset for Apache Echart's consumption.

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

Please refer to this [link](https://github.com/kagarcia1618/ntaac) for the example JSON format generated dataset.

### Grafana Plugin - Apache Echarts

- Apache Echarts is the key component that consolidates the pieces of information from NetBox, Grafana and Gitlab that renders a dynamic network topology from the JSON format data
- Apache Echarts has a parameter named `Function` that contains the code in javascript languange for ingesting the JSON format data from Gitlab repository.

Please refer to this [link](https://github.com/kagarcia1618/ntaac) for the example javascript function for grafana echarts plugin.