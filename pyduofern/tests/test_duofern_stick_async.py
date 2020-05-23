#!/usr/bin/env python3
# coding=utf-8
#   python interface for dufoern usb stick
#   Copyright (C) 2017 Paul Görgen
#   Rough python re-write of the FHEM duofern modules by telekatz, also licensed under GPLv2
#   This re-write contains only negligible amounts of original code
#   apart from some comments to facilitate translation of the not-yet
#   translated parts of the original software. Modification dates are
#   documented as submits to the git repository of this code, currently
#   maintained at https://github.com/gluap/pyduofern.git

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

import asyncio
import logging
import os
import tempfile

import pytest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from pyduofern import DuofernStickAsync, DuofernException, duoACK  # import DuofernStickAsync


# from pyduofern.duofern_stick import DuofernStickAsync


@pytest.fixture(
    params=[os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files', 'duofern.json'),
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files', 'duofern_recording.json'),
            tempfile.mktemp()])
def configfile(request):
    return request.param


@pytest.fixture(scope="function", params=[True, False])
def looproto(request, configfile):
    loop = asyncio.get_event_loop()

    proto = DuofernStickAsync(loop, system_code="ffff", config_file_json=configfile,
                              recording=request.param)
    return loop, proto


class TransportMock:
    def __init__(self, proto):
        super(TransportMock).__init__()
        self.proto = proto
        self.unittesting = True

    async def write(self, data):
        logger.warning("writing {} detected by mock writer".format(data))
        if data != bytearray.fromhex(duoACK):
            await self.proto.data_received(bytearray.fromhex(duoACK))
        self.proto._ready.set()



def test_raises_when_run_without_code():
    loop = asyncio.get_event_loop()

    with pytest.raises(DuofernException):
        proto = DuofernStickAsync(loop, config_file_json=tempfile.mktemp(), recording=False)


def test_raises_when_run_with_wrong_code():
    loop = asyncio.get_event_loop()

    with pytest.raises(AssertionError):
        proto = DuofernStickAsync(loop,
                                  config_file_json=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files',
                                                                'duofern.json'),
                                  recording=False, system_code="faaf")


def test_raises_when_run_with_long_code():
    loop = asyncio.get_event_loop()

    with pytest.raises(AssertionError):
        proto = DuofernStickAsync(config_file_json=tempfile.mktemp(), recording=False, system_code="faaaf")
