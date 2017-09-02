########
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cosmo_tester.framework.fixtures import bootstrap_based_manager

from . import hello_worlds  # noqa (pytest fixture imported)


manager = bootstrap_based_manager


def test_manager_bootstrap_and_deployment(hello_worlds, attributes):  # noqa (pytest fixture, not redefinition of hello_worlds)
    for hello in hello_worlds:
        hello.verify_all()
