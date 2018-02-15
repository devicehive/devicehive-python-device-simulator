#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import logging
import configargparse

from device_simulator import Supervisor, JSONConfigFileParser


COMMAND_MESSAGE_TYPE = 'command'
NOTIFICATION_MESSAGE_TYPE = 'notification'
MESSAGE_TYPE_CHOICES = (COMMAND_MESSAGE_TYPE, NOTIFICATION_MESSAGE_TYPE)


parser = configargparse.ArgumentParser(
    config_file_parser_class=JSONConfigFileParser,
    auto_env_var_prefix='DHDS_')
parser.add_argument('-f', '--config', is_config_file=True,
                    env_var='DHDS_CONFIG', help='Path to config file.')
parser.add_argument('-n', '--devices', type=int, default=1,
                    help='Number of devices to simulate. Default is 1.')
parser.add_argument('-u', '--url', required=True,
                    help='DeviceHive server url in format '
                         'http://server.name/api/rest or '
                         'ws://server.name/api/websocket.')
parser.add_argument('-d', '--delay', type=float, default=1.,
                    help='Delay between messages in seconds. Default is 1.')
parser.add_argument('-b', '--base_device_name', default='python-test-',
                    help='Base device name. Default is "python-test-".')
parser.add_argument('-c', '--cleanup', default=False, action='store_true',
                    help='Delete devices after stop.')
parser.add_argument('-v', '--verbose', dest='log_level',
                    action='store_const', const=logging.DEBUG,
                    default=logging.INFO, help='Show debug information.')

credentials_group = parser.add_mutually_exclusive_group(required=True)
credentials_group.add_argument('--access_token',
                               help='DeviceHive access token.')
credentials_group.add_argument('--refresh_token',
                               help='DeviceHive refresh token.')

limit_group = parser.add_argument_group('Limit arguments')
limit_group.add_argument('--message_limit', type=int, default=0,
                         help='Number of messages to be sent before stop. '
                         'Default is 0 (infinite loop).')
limit_group.add_argument('--time_limit', type=int, default=0,
                         help='Number of seconds to work before stop. '
                         'Default is 0 (infinite loop).')

message_group = parser.add_argument_group('Message arguments')
message_group.add_argument('--message_type', choices=MESSAGE_TYPE_CHOICES,
                           default=NOTIFICATION_MESSAGE_TYPE,
                           help='Type of message to be send. '
                                'Can be either "notification" or "command". '
                                'Default is "notification".')
message_group.add_argument('--message_name', default='python-test',
                           help='Message name. Default is "python-test".')
message_group.add_argument('--message_payload', default='{"key": "value"}',
                           help='JSON-like message payload. '
                                'Default is {"key": "value"}.')

args = vars(parser.parse_args())
logging.basicConfig(
    level=args.pop('log_level'),
    format='[%(levelname)s] %(asctime)s %(threadName)s: %(message)s'
)
args.pop('config')

supervisor = Supervisor(**args)
supervisor.start()
