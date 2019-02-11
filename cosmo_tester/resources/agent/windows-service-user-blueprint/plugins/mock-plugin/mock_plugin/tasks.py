#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

import os
import getpass

from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


@operation
def prepare_userdata(ctx, service_user, service_password, **_):
    if service_user:
        userdata = """#ps1_sysnative
&net user {user} '{password}' /add
&net localgroup "Administrators" "{user}" /add
""".format(user=service_user, password=service_password)
    else:
        userdata = ''

    ctx.logger.info("Rendered userdata:\n"
                    "------------------\n"
                    "{}\n"
                    "------------------".format(userdata))
    ctx.instance.runtime_properties['userdata'] = userdata


@operation
def test_app(ctx, service_user, **_):
    current_user = getpass.getuser()
    if service_user:
        # If service user is given, then its substring after "\" must
        # be equal to the current user.
        user_name_part = service_user
        if '\\' in user_name_part:
            user_name_part = user_name_part.split('\\', 1)[1]
            if user_name_part.lower() != current_user.lower():
                raise NonRecoverableError(
                    "service_user provided ({}) doesn't match current user "
                    "({})".format(service_user, current_user)
                )
    else:
        # If no service user is given, then the current user must
        # be identical to the value of the COMPUTERNAME environment
        # variable, with the suffix of "$".
        computer_name = os.environ['COMPUTERNAME']
        expected_user = computer_name + "$"
        if current_user != expected_user:
            raise NonRecoverableError(
                "No service_user provided, but current_user is '{}' "
                "(expected: '{}')".format(current_user,
                                          expected_user))
