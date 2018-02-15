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


import time
import signal
import logging
import threading

from .utils import AtomicCounter
from .worker import Worker


__all__ = ['Supervisor']
logger = logging.getLogger(__name__)


class Supervisor(object):
    def __init__(self, devices, url, message_type, message_name,
                 message_payload, base_device_name, access_token=None,
                 refresh_token=None, delay=1., message_limit=0, time_limit=0,
                 cleanup=False):
        signal.signal(signal.SIGTERM, self._sys_handler)

        self._devices = devices
        self._message_limit = message_limit
        self._time_limit = time_limit
        self._worker_kwargs = {
            'url': url,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'base_device_name': base_device_name,
            'supervisor': self,
            'message_type': message_type,
            'message_name': message_name,
            'message_payload': message_payload,
            'delay': delay,
            'cleanup': cleanup
        }
        self._counter = AtomicCounter()
        self._is_running = False
        self._workers = []

    @property
    def is_running(self):
        return self._is_running

    @property
    def counter(self):
        return self._counter

    def _stop(self):
        self._is_running = False
        [w.join() for w in self._workers]

    def _spawn_workers(self):
        logger.info('Spawning workers...')
        for i in range(self._devices):
            worker = Worker(thread_index=i, **self._worker_kwargs)
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

        logger.info('%d worker(s) have been spawned.' % self._devices)

    def _sys_handler(self, signum, frame):
        logging.info('Warm shutdown request by system call.')
        self._stop()

    def start(self):
        logger.info('Starting...')
        start_time = time.time()
        last_time = start_time
        self._is_running = True
        try:
            spawner = threading.Thread(target=self._spawn_workers,
                                       name='Spawner')
            spawner.setDaemon(True)
            spawner.start()

            last_send_counter = self._counter.value
            while True:
                time.sleep(1)
                sent_counter = self._counter.value
                now = time.time()
                sent_in_last_iteration = sent_counter - last_send_counter
                last_send_counter = sent_counter
                current_work_time = now - last_time
                sent_rate = sent_in_last_iteration / current_work_time
                alive_workers = len([w for w in self._workers if w.is_alive()])
                logger.info(
                    'Sent %d messages %.3f messages/second. Alive workers: %d',
                    sent_counter, sent_rate, alive_workers)
                last_time = now

                if 0 < self._message_limit <= sent_counter:
                    logger.info('Message limit has been reached.')
                    break

                if 0 < self._time_limit <= now - start_time:
                    logger.info('Time limit has been reached.')
                    break

                if not alive_workers:
                    logger.info('No alive workers left.')
                    break

        except KeyboardInterrupt:
            logger.info('Warm shutdown request by Ctrl-C. '
                        'Press again to use force.')
            try:
                self._stop()
            except KeyboardInterrupt:
                logger.info('May the force be with you!')
                raise

        else:
            logger.info('Shutting down...')
            self._stop()

        finally:
            total_time = time.time() - start_time
            avg_rate = self._counter.value / total_time
            logger.info('Total time: %.3f seconds, '
                        'Average rate: %.3f messages/second.',
                        total_time, avg_rate)
