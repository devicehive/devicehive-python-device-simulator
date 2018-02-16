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


import json
import time
import logging
import threading
import random
from functools import partial
from string import Template

from devicehive import Handler, DeviceHive
from .utils import Template


__all__ = ['Worker']
logger = logging.getLogger(__name__)
random.seed()


PAYLOAD = {
    'timestamp': time.time,
    'random': random.random,
    'randint': partial(random.randrange, 4294967295),
    'randbit': partial(random.getrandbits, 1)
}


class WorkerHandler(Handler):

    def __init__(self, api):
        super(WorkerHandler, self).__init__(api)
        self._connected = False

    @property
    def connected(self):
        return self._connected

    def handle_connect(self):
        self._connected = True


class Worker(threading.Thread):

    def __init__(self, supervisor, url, message_type, message_name,
                 message_payload, base_device_name, thread_index,
                 access_token=None, refresh_token=None, delay=1.,
                 cleanup=False):
        threading.Thread.__init__(self, name='Worker_%s' % thread_index)

        self._supervisor = supervisor
        self._url = url
        self._message_type = message_type
        self._message_name = message_name
        self._message_template = Template(message_payload)
        self._device_name = base_device_name + str(thread_index)
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._delay = delay
        self._cleanup = cleanup

        self._dh = None
        self._device = None
        self._payload_method = None
        self._last_message_time = 0.

    def _init(self):
        self._dh = DeviceHive(WorkerHandler)
        self._dh.connect(self._url,
                         access_token=self._access_token,
                         refresh_token=self._refresh_token,
                         transport_keep_alive=False)

        while not self._dh.handler.connected and self._supervisor.is_running:
            time.sleep(.001)

        self._device = self._dh.handler.api.put_device(self._device_name)
        method_name = 'send_%s' % self._message_type
        self._payload_method = getattr(self._device, method_name)
        self._last_message_time = time.time()

    def _get_payload(self):
        return json.loads(self._message_template.render(**PAYLOAD))

    def _send_message(self):
        start = time.time()
        last_sent = start - self._last_message_time
        if last_sent > 15.0:
            logger.warning('Previous message was sent %s seconds ago.',
                           last_sent)

        self._payload_method(self._message_name, self._get_payload())

        now = time.time()
        message_time = now - start
        if message_time > 10.0:
            logger.warning('Message send request took %s seconds.',
                           message_time)
        self._last_message_time = now

    def run(self):
        self._init()

        try:
            while self._supervisor.is_running:
                self._send_message()
                self._supervisor.counter.increment()
                time.sleep(self._delay)
        finally:
            if self._cleanup:
                self._device.remove()

            self._dh.handler.api.disconnect()
