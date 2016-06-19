#!/usr/bin/env python

DOCUMENTATION = '''
---
module: ucs-vlans
author: "Nick Chandler (@nwchandler)"
short_description: Adds or removes VLANs from Cisco UCS
description:
  - This module allows you to ensure that appropriate VLANs
    are present or absent on Cisco Unified Computing System (UCS)
    platforms.
requirements:
  - ucsmsdk
options:
  ucs_ip:
    description:
      - IP address of the Cisco UCS server
    required: True
  ucs_user:
    description:
      - Username with which to connect to UCS
    required: True
  ucs_pass:
    description:
      - Password for account with which to connect to UCS
    required: True
  vlans:
    description
      - VLANs to add/remove/verify on UCS. Provide as a list of key/value
        pairs, where the key is the name of the VLAN, and the value is
        the VLAN ID (or number)
    required: True
  state:
    description
      - Defines whether the VLAN(s) should be present or absent
    required: False
    default: present
    choices: ['present', 'absent']
'''
try:
    from ucsmsdk.ucshandle import UcsHandle
    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
    UCSMSDK_IMPORTED = True
except ImportError:
    UCSMSDK_IMPORTED = False

def updateVlans(module):
    
    ucs_ip = module.params['ucs_ip']
    ucs_user = module.params['ucs_user']
    ucs_pass = module.params['ucs_pass']
    vlans = module.params['vlans']
    state = module.params['state']

    results = {}
    results['changed'] = False
    
    results['created'] = []
    results['removed'] = []
    
    
    # Login to UCS
    try:
        handle = UcsHandle(ucs_ip, ucs_user, ucs_pass)
    except:
        module.fail_json(msg="Could not login to UCS")
    
    try:
        # Obtain a handle for the LAN Cloud
        lancloud = handle.query_classid(class_id="FabricLanCloud")

        defined_vlans = handle.query_children(
                in_mo=lancloud[0], 
                class_id="FabricVlan"
                )

        for key, val in vlans.iteritems():
            filter_str = '(name, "%s", type="eq") and (id, %s, type="eq")' \
                        % (key, val) 
            obj = handle.query_children(
                        in_mo=lancloud[0], 
                        class_id="FabricVlan", 
                        filter_str=filter_str
                        )

            if state == 'present' and len(obj) > 0:
                pass
            elif state == 'present' and len(obj) == 0:
                vlan = FabricVlan(lancloud[0], name=key, id=str(val))
                handle.add_mo(vlan)
                handle.commit()
                results['created'].append(key)
                results['changed'] = True
            elif state == 'absent' and len(obj) > 0:
                handle.remove_mo(obj[0])
                handle.commit()
                results['changed'] = True
                results['removed'].append(key)
    except Exception, e:
        module.fail_json(msg="Could not create or validate VLANs; %s" % e)
    finally:
        handle.logout()
    return results

def main():
    module = AnsibleModule(
        argument_spec = dict(
            ucs_ip = dict(required=True),
            ucs_user = dict(required=True),
            ucs_pass = dict(required=True),
            vlans = dict(required=True),
            state = dict(required=False, \
                    default='present', \
                    choices=['present', 'absent']),
            ),
        supports_check_mode = False
    )

    if not UCSMSDK_IMPORTED:
        module.fail_json(msg="Module requires ucsmsdk")
        
    results = updateVlans(module)

    module.exit_json(**results)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
