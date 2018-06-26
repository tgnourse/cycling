#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gpxpy
import math
import os
import sys

# TODO: Limit to just the ascents to see the difference between them.
# TODO: Compare actual rides to the measured routes, see diff
# TODO: Compare to each of the death ride ascents.


def min_elevation(tracks):
    elevation = None
    for track in tracks:
        for segment in track.segments:
            for point in segment.points:
                if elevation is None or point.elevation < elevation:
                    elevation = point.elevation
    return elevation


def print_grade_per_meter(tracks, distance_offset=0):
    total_distance = distance_offset
    min_elev = min_elevation(tracks)
    for track in tracks:
        for segment in track.segments:
            cumulative_distance = 0
            cumulative_points = []
            for i in xrange(1, len(segment.points)):
                first_point = segment.points[i-1]
                second_point = segment.points[i]
                distance = gpxpy.geo.distance(
                    first_point.latitude, first_point.longitude, first_point.elevation,
                    second_point.latitude, second_point.longitude, second_point.elevation)

                cumulative_distance += distance
                total_distance += distance
                cumulative_points.append(first_point)

                # Smooth out the grade by only calculating for every ~ 50m
                # TODO: get the buckets exact with some extrapolation between points somehow?
                if cumulative_distance > 50:
                    average_grade = cumulative_points[0].elevation_angle(second_point)
                    print '{0}\t{1}\t{2}'.format(
                        total_distance, first_point.elevation - min_elev, average_grade)
                    cumulative_distance = 0
                    cumulative_points = []

    return total_distance


# Run this for every file input and use cumulative distance
final_distance = 0
for f in sys.argv[1:]:
    label = os.path.splitext(os.path.basename(f))[0]
    print label
    # print '{0} (m)\t{0} (%)'.format(label)
    final_distance = print_grade_per_meter(gpxpy.parse(open(f, 'r')).tracks, final_distance)


def print_grade_histogram(tracks):
    for track in tracks:
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
                # print '{0}\t{1}'.format(key, value if value else 0)

            # for point in segment.points:
            #     print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)