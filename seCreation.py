import requests, json, os, yaml, sys, time
from avi.sdk.avi_api import ApiSession

class aviSession:
  def __init__(self, fqdn, username, password, tenant):
    self.fqdn = fqdn
    self.username = username
    self.password = password
    self.tenant = tenant

  def debug(self):
    print("controller is {0}, username is {1}, password is {2}, tenant is {3}".format(self.fqdn, self.username, self.password, self.tenant))

  def getObject(self, objectUrl, objectData):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    result = api.get(objectUrl, data=objectData)
    return result.json()

if __name__ == '__main__':
#   with open(sys.argv[1], 'r') as stream:
#       avi_credentials = json.load(stream)
#   stream.close
  avi_credentials = yaml.load(sys.argv[1])
  seg = yaml.load(sys.argv[2])
  cloud_no_access_vcenter_uuid = sys.argv[3]
  network_management = sys.argv[4]
  networks_data = [sys.argv[5]]
  vcenter = yaml.load(sys.argv[6])
  vsphere_username= sys.argv[7]
  vsphere_password= sys.argv[8]
  ova_path = sys.argv[9]
  cl_name = 'Easy-Avi-CL-SE-NoAccess'
  tenant = "admin"
  if seg['numberOfSe'] == 0:
    print('no SE to create')
    exit()
#   network_mgmt = "MGMT"
#   network_data = ['vip1', 'vip2', 'vip3']
#   print(avi_credentials['controller'])
#   print(avi_credentials['password'])
#   print(seg['dhcp'])
#   print(cloud_no_access_vcenter_uuid)
#   print(network_management)
#   print(networks_data)
#   print(vcenter['server'])
#   print(vsphere_username)
#   print(vsphere_password)
  vsphere_url="https://" + vsphere_username + ":" + vsphere_password + "@" + vcenter['server']
#   print(vsphere_url)
  defineClass = aviSession(avi_credentials['controller'], avi_credentials['username'], avi_credentials['password'], tenant)
  cluster_uuid = defineClass.getObject('cluster', '')['uuid']
  print(cluster_uuid)
  data = {"cloud_uuid": cloud_no_access_vcenter_uuid}
  token = defineClass.getObject('securetoken-generate', data)
  print(token)
  print(seg['folder'])
  print(ova_path)
  os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_INSECURE=true; govc folder.create /{0}/vm/{2}'.format(vcenter['dc'], vsphere_url, seg['folder']))
  os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_INSECURE=true; govc library.create {2}'.format(vcenter['dc'], vsphere_url, cl_name))
  os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_INSECURE=true; govc library.import {2} {3}'.format(vcenter['dc'], vsphere_url, cl_name, ova_path))
  if seg['dhcp'] == True:
    for se in range (1, seg['numberOfSe'] + 1):
      print(se)
      print('dhcp is true')
      se_name = 'EasyAvi - ' + seg['name'] +  ' - SE' + str(se)
      properties = {
                    'IPAllocationPolicy': 'dhcpPolicy',
                    'IPProtocol': 'IPv4',
                    'MarkAsTemplate': False,
                    'PowerOn': False,
                    'InjectOvfEnv': False,
                    'WaitForIP': False,
                    'Name': se_name
                   }
      properties['PropertyMapping'] = [
                                        {
                                          'Key': 'AVICNTRL',
                                          'Value': avi_credentials['controller']
                                        },
                                        {
                                          'Key': 'AVISETYPE',
                                          'Value': 'NETWORK_ADMIN'
                                        },
                                        {
                                          'Key': 'AVICNTRL_AUTHTOKEN',
                                          'Value': 'placeholder'
                                        },
                                        {
                                          'Key': 'AVICNTRL_CLUSTERUUID',
                                          'Value': 'placeholder'
                                        },
                                        {
                                          'Key': 'avi.mgmt-ip.SE',
                                          'Value': ''
                                        },
                                        {
                                          'Key': 'avi.mgmt-mask.SE',
                                          'Value': ''
                                        },
                                        {
                                          'Key': 'avi.default-gw.SE',
                                          'Value': ''
                                        },
                                        {
                                          'Key': 'avi.DNS.SE',
                                          'Value': ''
                                        },
                                        {
                                          'Key': 'avi.sysadmin-public-key.SE',
                                          'Value': ''
                                        }
                                      ]
      NetworkMapping = []
      NetworkMapping.append({'Name': 'Management', 'Network': network_management})
      count = 1
      for item in networks_data:
        NetworkMapping.append({'Name': 'Data Network ' + str(count), 'Network': item})
        count += 1
      for i in range(len(networks_data) + 1, 10):
        NetworkMapping.append({'Name': 'Data Network ' + str(i), 'Network': ''})
        print(i)
      #     network = {}
      #       count = 1
      #       for item in networks_data:
      #         key_network = 'Data Network ' + str(count)
      #         network[key_network] = item
      #         count += 1
      #     #   print(network)
      #       for i in range(len(networks_data) + 1, 10):
      #         key_network = 'Data Network ' + str(i)
      #         network[key_network] = ''
      #       network['Management'] = network_management
      #       print(network)
      properties['NetworkMapping'] = NetworkMapping
      print(properties)
      with open('properties.json', 'w') as f:
          json.dump(properties, f)
      print('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc library.deploy -folder=/{0}/vm/{3} -options=./properties.json /{4}/se {5}'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], seg['folder'], cl_name, se_name))
#       os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc library.deploy -folder=/{0}/vm/{3} -options=./properties.json /{4}/se {5}'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], seg['folder'], cl_name, se_name))
#       os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc vm.change -vm {3} -c {4} -m {5}'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], se_name, seg['vcpus_per_se'], seg['memory_per_se']))
#       os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc vm.disk.change -vm {3} -size {4}'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], se_name, seg['disk_per_se']))
#       os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc vm.power -on {3}'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], se_name))
#       time.sleep(180)
#       os.system('export GOVC_DATACENTER={0}; export GOVC_URL={1}; export GOVC_GOVC_DATASTORE={2}; export GOVC_INSECURE=true; govc vm.ip {3} | tee ip.txt'.format(vcenter['dc'], vsphere_url, vcenter['datastore'], se_name))
#       with open('ip.txt', 'r') as file:
#         ip = file.read().replace('\n', '')
#   if seg['dhcp'] == False:
#     print('dhcp is false')
#   defineClass = aviSession(avi_credentials['controller'], avi_credentials['username'], avi_credentials['password'], tenant)
#   cluster_uuid = defineClass.getObject('cluster', '')['uuid']
#   print(cluster_uuid)
#   data = {"cloud_uuid": cloud_uuid}
#   token = defineClass.getObject('securetoken-generate', data)
#   print(token)
#   network = {}
#   count = 1
#   for item in network_data:
#     key_network = 'Data Network ' + str(count)
#     network[key_network] = item
#     count += 1
#   print(network)
#   for i in range(len(network_data) + 1, 10):
#     key_network = 'Data Network ' + str(i)
#     network[key_network] = 'padding'
#   network['Management'] = network_mgmt
#
#
