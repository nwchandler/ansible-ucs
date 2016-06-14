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
  - ucssdk
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

from UcsSdk import *
from UcsSdk.MoMeta.FabricLanCloud import FabricLanCloud
from UcsSdk.MoMeta.FabricVlan import FabricVlan

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
        handle = UcsHandle()
        login_status = handle.Login(
                ucs_ip,
                ucs_user,
                ucs_pass
        )
    except:
        module.fail_json(msg="Could not login to UCS")
    
    try:
        # Obtain a handle for the LAN Cloud
        lanCloud = handle.GetManagedObject(
                None,
                FabricLanCloud.ClassId()
        )

        for key, val in vlans.iteritems():

            obj = handle.GetManagedObject(
                    lanCloud,
                    FabricVlan.ClassId(),
                    {
                            FabricVlan.ID:val,
                            FabricVlan.NAME:key
                    }
            )

            if state == 'present' and len(obj) > 0:
                pass
            elif state == 'present' and len(obj) == 0:
                handle.AddManagedObject(     
                        lanCloud,                       
                        FabricVlan.ClassId(),
                        {
                                FabricVlan.ID:val,           
                                FabricVlan.NAME:key
                        }
                )
                results['created'].append(key)
                results['changed'] = True
            elif state == 'absent' and len(obj) > 0:
                handle.RemoveManagedObject(obj)
                results['changed'] = True
                results['removed'].append(key)
    except:
        module.fail_json(msg="Could not create or validate VLANs")
    finally:
        handle.Logout()
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

    results = updateVlans(module)

    module.exit_json(**results)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
