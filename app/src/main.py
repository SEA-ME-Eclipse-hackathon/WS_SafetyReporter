# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""A sample skeleton vehicle app."""

import asyncio
import json
import logging
import signal

from SafetyChecker import SafetyChecker
from vehicle import Vehicle, vehicle  # type: ignore
from velocitas_sdk.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vehicle_app import VehicleApp, subscribe_data_points

# Configure the VehicleApp logger with the necessary log config and level.
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("DEBUG")
logger = logging.getLogger(__name__)

SAFETY_FATAL_TOPIC = "safety/fatal"
LOGGER_LOG_TOPIC = "loggerapp/log"


class SafetyReporterApp(VehicleApp):
    """ """

    def __init__(self, vehicle_client: Vehicle):
        # SafetyReporterApp inherits from VehicleApp.
        super().__init__()
        self.Vehicle = vehicle_client
        self.SafetyChecker = SafetyChecker()

    async def on_start(self):
        """Run when the vehicle app starts"""

    @subscribe_data_points("Vehicle.Speed")
    async def on_speed_change(self, data: DataPointReply):
        speed = data.get(self.Vehicle.Speed).value
        if self.SafetyChecker.is_speed_safe(speed) is False:
            await self.publish_event(
                SAFETY_FATAL_TOPIC, json.dumps({"cause": "speed drops dramatically"})
            )

    @subscribe_data_points(
        """Vehicle.Cabin.Seat.Row1.Pos1.Airbag.IsDeployed,
        Vehicle.Cabin.Seat.Row1.Pos2.Airbag.IsDeployed,
        Vehicle.Cabin.Seat.Row1.Pos3.Airbag.IsDeployed,
        Vehicle.Cabin.Seat.Row2.Pos1.Airbag.IsDeployed,
        Vehicle.Cabin.Seat.Row2.Pos2.Airbag.IsDeployed,
        Vehicle.Cabin.Seat.Row2.Pos3.Airbag.IsDeployed
        """,
        """Vehicle.Cabin.Seat.Row1.Pos1.Airbag.IsDeployed == true OR
        Vehicle.Cabin.Seat.Row1.Pos2.Airbag.IsDeployed == true OR
        Vehicle.Cabin.Seat.Row1.Pos3.Airbag.IsDeployed == true OR
        Vehicle.Cabin.Seat.Row2.Pos1.Airbag.IsDeployed == true OR
        Vehicle.Cabin.Seat.Row2.Pos2.Airbag.IsDeployed == true OR
        Vehicle.Cabin.Seat.Row2.Pos3.Airbag.IsDeployed == true
        """,
    )
    async def on_airbag_trigger(self, data: DataPointReply):
        r1p1 = data.get(self.Vehicle.Cabin.Seat.Row1.Pos1.Airbag.IsDeployed).value
        r1p2 = data.get(self.Vehicle.Cabin.Seat.Row1.Pos2.Airbag.IsDeployed).value
        r1p3 = data.get(self.Vehicle.Cabin.Seat.Row1.Pos3.Airbag.IsDeployed).value
        r2p1 = data.get(self.Vehicle.Cabin.Seat.Row2.Pos1.Airbag.IsDeployed).value
        r2p2 = data.get(self.Vehicle.Cabin.Seat.Row2.Pos2.Airbag.IsDeployed).value
        r2p3 = data.get(self.Vehicle.Cabin.Seat.Row2.Pos3.Airbag.IsDeployed).value

        await self.publish_event(
            LOGGER_LOG_TOPIC,
            f"""airbag triggered : r1p1: ${r1p1} r1p2: ${r1p2} r1p1: ${r1p3} \
r2p1: ${r2p1} r2p2: ${r2p2} r2p3: ${r2p3}""",
        )
        await self.publish_event(
            SAFETY_FATAL_TOPIC, json.dumps({"cause": "airbag triggered"})
        )


async def main():
    """Main function"""
    logger.info("Starting SafetyReporterApp...")
    # Constructing SafetyReporterApp and running it.
    vehicle_app = SafetyReporterApp(vehicle)
    await vehicle_app.run()


LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
