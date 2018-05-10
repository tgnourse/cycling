#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import gpxpy

gpx_file = open(sys.argv[1], 'r')
gpx = gpxpy.parse(gpx_file)

# TODO: Limit to just the ascents to see the difference between them.
# TODO: Compare actual rides to the measured routes, see diff
# TODO: Compare to each of the death ride ascents.

for track in gpx.tracks:
    for segment in track.segments:
        grade_histogram = {}
        for i in xrange(1, len(segment.points)):
            first_point = segment.points[i-1]
            second_point = segment.points[i]
            angle_rad = gpxpy.geo.elevation_angle(first_point, second_point, True)
            distance = gpxpy.geo.distance(
                first_point.latitude, first_point.longitude, first_point.elevation,
                second_point.latitude, second_point.longitude, second_point.elevation)
            angle_percent = math.tan(angle_rad)*100
            angle_histo = round(angle_percent)
            if grade_histogram.get(angle_histo):
                grade_histogram[angle_histo] = grade_histogram.get(angle_histo) + distance
            else:
                grade_histogram[angle_histo] = distance
            # print '{0}°, {1}%, {2}m'.format(angle_rad, math.tan(angle_rad)*100, distance)

        elevations = list(map((lambda point: point.elevation), segment.points))
        uphill, downhill = gpxpy.geo.calculate_uphill_downhill(elevations)
        print '{0}m up, {1}m down, {2}m length, {3} seconds'.format(
            uphill, downhill, segment.length_3d(), segment.get_duration())
        # for key in sorted(grade_histogram):
        #     value = grade_histogram[key]
        #     if value > 100:
        #         print '{0}\t{1}'.format(key, value)

        for key in xrange(-15, 16):
            value = grade_histogram.get(key)
            print '{0}\t{1}'.format(key, value if value else 0)

        # for point in segment.points:
        #     print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)