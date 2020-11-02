# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Esa Niemi
# Heavily based on Daniel Thompson's Heart and Stopwatch apps

import wasp
import machine
import ppg

class SportsApp():
    """
    General purpose sports app. 
    Shows a clock widget, HR, steps and a stopwatch with a start-stop-reset -loop operated by touching the screen.
    """
    NAME = 'Sports'

    def foreground(self):
        """Activate the application."""
        wasp.watch.hrs.enable()

        # There is no delay after the enable because the redraw should
        # take long enough it is not needed
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('PPG graph', 0, 6, width=240)

        wasp.system.request_tick(1000 // 8)

        self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())

    def background(self):
        wasp.watch.hrs.disable()
        del self._hrdata

    def _subtick(self, ticks):
        """Notify the application that its periodic tick is due."""
        draw = wasp.watch.drawable

        spl = self._hrdata.preprocess(wasp.watch.hrs.read_hrs())

        if len(self._hrdata.data) >= 240:
            draw.string('{} bpm'.format(self._hrdata.get_heart_rate()),
                        0, 6, width=240)

    def tick(self, ticks):
        """This is an outrageous hack but, at present, the RTC can only
        wake us up every 125ms so we implement sub-ticks using a regular
        timer to ensure we can read the sensor at 24Hz.
        """
        # keep watch awake
        wasp.system.keep_awake()

        t = machine.Timer(id=1, period=8000000)
        t.start()
        self._subtick(1)
        wasp.system.keep_awake()

        while t.time() < 41666:
            pass
        self._subtick(1)

        while t.time() < 83332:
            pass
        self._subtick(1)

        t.stop()
        del t
