#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2022, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fusion_api_client
version_added: '1.0.0'
short_description:  Manage API clients in Pure Storage Fusion
description:
- Create or delete an API Client in Pure Storage Fusion.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
notes:
- Supports C(check mode).
options:
  name:
    description:
    - The name of the client.
    type: str
    required: true
  state:
    description:
    - Define whether the client should exist or not.
    default: present
    choices: [ present, absent ]
    type: str
  public_key:
    description:
    - The API clients PEM formatted (Base64 encoded) RSA public key.
    - Include the C(—–BEGIN PUBLIC KEY—–) and C(—–END PUBLIC KEY—–) lines.
    type: str
    required: true
extends_documentation_fragment:
- purestorage.fusion.purestorage.fusion
"""

EXAMPLES = r"""
- name: Create new API client foo
  purestorage.fusion.fusion_api_client:
    name: "foo client"
    public_key: "{{lookup('file', 'public_pem_file') }}"
    app_id: key_name
    key_file: "az-admin-private-key.pem"
"""

RETURN = r"""
"""

import ansible_collections.purestorage.fusion.plugins.module_utils.prerequisites
import fusion as purefusion

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.fusion.plugins.module_utils.fusion import (
    get_fusion,
    fusion_argument_spec,
)
from ansible_collections.purestorage.fusion.plugins.module_utils.errors import (
    install_fusion_exception_hook,
)


def get_client(module, fusion):
    """Get API Client - True or False"""
    id_api_instance = purefusion.IdentityManagerApi(fusion)
    try:
        clients = id_api_instance.list_api_clients()
        for client in range(0, len(clients)):
            if (
                clients[client].public_key == module.params["public_key"]
                and clients[client].display_name == module.params["name"]
            ):
                return clients[client].id
        return False
    except purefusion.rest.ApiException:
        return False


def delete_client(module, fusion):
    """Delete API Client"""
    id_api_instance = purefusion.IdentityManagerApi(fusion)

    changed = True
    if not module.check_mode:
        id_api_instance.delete_api_client(api_client_id=get_client(module, fusion))
    module.exit_json(changed=changed)


def create_client(module, fusion):
    """Create API Client"""

    id_api_instance = purefusion.IdentityManagerApi(fusion)

    changed = True
    if not module.check_mode:
        client = purefusion.APIClientPost(
            public_key=module.params["public_key"],
            display_name=module.params["name"],
        )
        id_api_instance.create_api_client(client)

    module.exit_json(changed=changed)


def main():
    """Main code"""
    argument_spec = fusion_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            public_key=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
        )
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    install_fusion_exception_hook(module)

    fusion = get_fusion(module)
    state = module.params["state"]
    client = get_client(module, fusion)
    if not client and state == "present":
        create_client(module, fusion)
    elif client and state == "absent":
        delete_client(module, fusion)
    else:
        module.exit_json(changed=False)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
