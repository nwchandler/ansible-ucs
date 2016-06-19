#!/usr/bin/env python

DOCUMENTATION = '''
---
module: ucs-ntp
author: "Nick Chandler (@nwchandler)"
short_description: Adds or removes NTP servers from Cisco UCS
description:
  - This module allows you to ensure that appropriate NTP servers
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
  ntp:
    description
      - NTP servers to add/remove/verify on UCS. Provide as a list of 
        values. Either IP addresses or hostnames/FQDN's will work.
    required: True
  state:
    description
      - Defines whether the server(s) should be present or absent
    required: False
    default: present
    choices: ['present', 'absent']
'''

try:
    from ucsmsdk.ucshandle import UcsHandle
    from ucsmsdk.mometa.comm.CommNtpProvider import CommNtpProvider
    UCSMSDK_IMPORTED = True
except ImportError:
    UCSMSDK_IMPORTED = False

def updateNtp(module):
    
    ucs_ip = module.params['ucs_ip']
    ucs_user = module.params['ucs_user']
    ucs_pass = module.params['ucs_pass']
    ntp = module.params['ntp']
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
        # Obtain a handle for the Timezone object
        tz = handle.query_classid(class_id="CommDateTime")

        if type(ntp) != list:
            ntp = list(ntp)

        for server in ntp:
            filter_str = '(name, "%s", type="eq")' % (server)
            obj = handle.query_children(
                        in_mo=tz[0], 
                        class_id="CommNtpProvider",
                        filter_str=filter_str
                        )

            if state == 'present' and len(obj) > 0:
                pass
            elif state == 'present' and len(obj) == 0:
                ntp_server = CommNtpProvider(tz[0], name=server)
                handle.add_mo(ntp_server)
                handle.commit()
                results['created'].append(server)
                results['changed'] = True
            elif state == 'absent' and len(obj) > 0:
                handle.remove_mo(obj[0])
                handle.commit()
                results['changed'] = True
                results['removed'].append(server)
    except Exception, e:
        module.fail_json(msg="Could not create or validate servers; %s" % e)
    finally:
        handle.logout()
    return results

def main():
    module = AnsibleModule(
        argument_spec = dict(
            ucs_ip = dict(required=True),
            ucs_user = dict(required=True),
            ucs_pass = dict(required=True),
            ntp = dict(required=True),
            state = dict(required=False, \
                    default='present', \
                    choices=['present', 'absent']),
            ),
        supports_check_mode = False
    )

    if not UCSMSDK_IMPORTED:
        module.fail_json(msg="Module requires ucsmsdk")

    results = updateNtp(module)

    module.exit_json(**results)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
