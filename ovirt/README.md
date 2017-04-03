# oVirt/RHEV Dynamic Inventory
![img](../img/ovirt.png)

Dynamic inventories for RHEV/oVirt to use it from Ansible

## Requirements

- [oVirt Python SDK](http://www.ovirt.org/develop/release-management/features/infra/python-sdk/) < version 4.0
- Credentials to access to an installation of oVirt or RHEV.

## How this works
We have 2 main functionalities , the first one is that this module works with ansible.cfg file in two new sections:
- ovirt
- ovirt-classifier

The first one is to set where are the ovirt-manager to log in. The second one is to select which groups will contain the Dynamic Inventory based on a pattern with a variable called **basename**, and suffixes to complete the nodename, lets go on a real example:

This is our nodes inside of oVirt-Manager:
![img](../img/ovirt_screen_nodes.jpg)

- Input:

```
python rhev36.py
```

- Output:

```
[SPLUNK_INDEXER]
cvs3tsk01
[RABBITMQ]
cvs3tmq01
cvs3tmq03
[KAFKA]
cvs3tkf02
[HEAT]
cvs3the02
cvs3the03
[CINDER-STORAGE]
cvs3tci02
[NTP-SERVERS]
cvs3tti02
[RALLY]
cvs3tra01
[INTERNAL-HAPROXY-MASTER]
cvs3tha03
[NEUTRON-AGENTS]
cvs3tns02
```

- Ansible.cfg sample:

```
[ovirt]
host = 'https://ovirt36'            ## Connection URL
port = 443                          ## Connection port
user = 'admin@internal'             ## Auth
passw = 'unix1234'                  ## Auth
ssl_insecure = True                 ## SSL Queries against ovirt
logfile = 'DynInvOvirt.log'         ## Logfile name
grp_upper = False                   ## Group name on upppercase also on children ones

[ovirt-classifier]
basename = 'cvs3t'
group_rabbitmq = 'mq'
group_neutron-agents = 'ns'
group_cinder-storage = 'ci'
group_heat = 'he'
group_internal-haproxy-master = 'ha'
group_ntp-servers = 'ti'
group_kafka = 'kf'
group_rally = 'ra'
```

As you see the patter "group_XXX" will create a group name called XXX and the value will be the concatenation between **basename** + the group_XXX value (EG):

```
[ovirt-classifier]
basename = 'testnode_'
group_rabbitmq_nodes = 'rabbit'
```

This formation will create this structure:
```
[RABBITMQ_NODES]
testnode_rabbit01
testnode_rabbit02
testnode_rabbit03
testnode_rabbit11
testnode_rabbit_dev_01
```

### Support for Children groups
What means that, yeah, we can group other groups to create hierarchy, just use the following syntax

- Input:
```
[ovirt-classifier]
basename = 'cvs3t'
group_ansible = 'an'
group_satellite= 'sc'
group_database = 'md'
group_rabbitmq = 'mq'
group_mail = 'ma'
children_test = 'ansible', 'vars', 'ntp'
children_test2 = 'lol', 'onnud', 'otp'
children_test4 = 'dunno', 'testp'
children_test7 = 'ansible', 'lol' , '3D'
children_test4 = 'ansible2'
```

- Output:
```
[test:children]
ansible
vars
ntp
[test7:children]
ansible
lol
3D
[rabbitmq]
cvs3tmq01
cvs3tmq03
[test2:children]
lol
onnud
otp
[None]
copmute_node_01
copmute_node_02
cvs3tci02
cvs3tha03
cvs3the02
cvs3the03
cvs3tkf02
cvs3tns02
cvs3tra01
cvs3tsk01
cvs3tti02
test_01
test_02
[test4:children]
ansible2
```

_NOTE: if you repeat the group, the inventory will take the last as valid one (EG)_

- Input:
```
[ovirt-classifier]
children_test2 = 'ansible', 'vars', 'ntp'
children_test2 = 'lol', 'onnud', 'tp'
children_test2 = 'dunno', 'testp'
children_test2 = 'ansible', 'lol' , '3D'
children_test2 = 'ansible2'
```

- Output:
```
...
[test2:children]
ansible2
...
```
