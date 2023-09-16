import json
import gitlab
from gitlab.exceptions import GitlabHttpError, GitlabGetError
import requests
from extras.scripts import *
from dcim.models import Device, Interface

name = 'JSON generator for Grafana Echarts'

#Netbox Device roles filter for inclusion in Grafana Echarts Network Topology
DEVICE_FILTER = [
    'vpc-leaf-switch',
    'border-spine',
    'leaf-switch',
    'tier1-firewall',
    'wan-router'
]

#Netbox Interface tags filter for inclusion in Grafana Echarts Network Topology
INTERFACE_FILTER = [
    'leaf-spine',
    'vpc-peer-link-primary',
    'spine-firewall',
    'wr-firewall',
]

#Netbox Interface tags filter for VXLAN nodes
VXLAN_FILTER = [
    'vpc-leaf-switch',
    'border-spine',
    'leaf-switch'
]

#Time interval for grafana interface utilization display
TIME_INTERVAL = '12h'

#Gitlab credentials
url = 'https://<Gitlab IP or FQDN>' #Update this line
token = '<Gitlab API token>' #Update this line
project_name = '<Gitlab Username>/<Gitlab Project Name>' #Update this line
gl = gitlab.Gitlab(url, private_token=token, ssl_verify=False)
project = gl.projects.get(project_name)
topology_filename = 'network_topology_as_a_code.json' #Optionally update this line

class EchartTopology(object):
    '''
    Class object that process device and interface list to a
    JSON format data using json_data() method for consumption
    of Grafana Echarts to display the network topology
    '''
    def __init__(
        self,
        device_list: list,
        interface_list: list,
    ) -> None:
        self.device_list = device_list
        self.interface_list = interface_list
    def _generate_node_url(self, device):
        '''
        Private method to generate a URL for a node during 'on-click' event
        '''
        if device.device_role.slug in VXLAN_FILTER:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Path>?<Custom Query Parameter for VXLAN devices>"
            return url_template
        else:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Path>?<Custom Query Parameter for other type of devices>"
            return url_template
    def _generate_link_url(self, interface):
        '''
        Private method to generate a URL for a node link during 'on-click' event
        '''
        if interface.device.device_role.slug in VXLAN_FILTER:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Path>?<Custom Query Parameter for VXLAN interfaces>"
            return url_template
        else:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Path>?<Custom Query Parameter for other type of interfaces>"
            return url_template
    def _generate_node_iframe(self, device):
        '''
        Private method to generate an iframe for a node during 'mouse-over' event
        '''
        if device.device_role.slug in VXLAN_FILTER:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Iframe Path>?<Custom Query Parameter for VXLAN devices>"
            iframe_template = f"""`<iframe src='{url_template}' width='600' height='250' frameborder='0'></iframe>`"""
            return iframe_template
        else:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Iframe Path>?<Custom Query Parameter for other type of devices>"
            iframe_template = f"""`<iframe src='{url_template}' width='600' height='250' frameborder='0'></iframe>`"""
            return iframe_template
    def _generate_link_iframe(self, interface):
        '''
        Private method to generate an iframe for a node link during 'mouse-over' event
        '''
        if interface.device.device_role.slug in VXLAN_FILTER:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Iframe Path>?<Custom Query Parameter for VXLAN interfaces>"
            iframe_template = f"""`<iframe src='{url_template}' width='600' height='250' frameborder='0'></iframe>`"""
            return iframe_template
        else:
            url_template = f"https://<Grafana IP address or FQDN>/<Grafana Dashboard Iframe Path>?<Custom Query Parameter for other type of interfaces>"
            iframe_template = f"""`<iframe src='{url_template}' width='600' height='250' frameborder='0'></iframe>`"""
            return iframe_template
    def _get_categories(self):
        '''
        Private method to generate a list of dict format category from device role property
        '''
        categories = list()
        for device in self.device_list:
            if device.device_role.name not in categories:
                categories.append(device.device_role.name)
        data = [ {"name": category} for category in categories ]
        return data
    def _get_nodes(self):
        '''
        Private method to generate a list of dict format nodes from device name and role
        '''
        data = [ {
            "name": device.name,
            "category": device.device_role.name,
            "url": self._generate_node_url(device),
            "iframe": self._generate_node_iframe(device)
        } for device in self.device_list ]
        return data
    def _get_links(self):
        '''
        Private method to generate a list of dict format links from interface list
        '''
        data = [ {
            "source": interface.device.name,
            "target": interface.trace()[-1][-1][0].device.name,
            "url": self._generate_link_url(interface),
            "iframe": self._generate_link_iframe(interface),
        } for interface in self.interface_list ]
        return data
    def json_data(self):
        '''
        Method to generate the JSON format data that includes the categories,
        nodes and links for Grafana Echarts formatting consumption
        '''
        data = {
            "type": "force",
            "categories": self._get_categories(),
            "nodes": self._get_nodes(),
            "links": self._get_links(),
        }
        return json.dumps(data, indent = 4)

class GrafanaEcharts(Script):

    class Meta:
        name = "Grafana Echarts -Topology Code Generator"
        description = "Update the network topology code for Grafana Echarts"

    def run(self, data, commit):
        device_list = list(Device.objects.filter(device_role__slug__in=DEVICE_FILTER, status='active'))
        interface_list = list(Interface.objects.filter(tags__name__in=INTERFACE_FILTER))
        topology = EchartTopology(device_list, interface_list)

        try:
            current_data = project.files.get(file_path=topology_filename, ref='main')
            if current_data.decode().decode() == topology.json_data():
                self.log_info('Network topology is up-to-date with Netbox records.')
            else:
                try:
                    data = project.files.get(file_path=topology_filename, ref='main')
                    data.content = topology.json_data()
                    data.save(branch='main', commit_message='Network topology updated.')
                    self.log_success('Network topology code updated in gitlab.')
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ):
                    self.log_failure('Failed updating the network topology.')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, GitlabHttpError, GitlabGetError):
            self.log_failure('Failed connecting to Gitlab.')