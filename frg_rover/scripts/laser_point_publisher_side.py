#!/usr/bin/env python
PKG = 'frg_rover'
import roslib; roslib.load_manifest(PKG)
#Need this for the Msgs to work
roslib.load_manifest('frg_rover_msgs')

import rospy
import numpy

from std_msgs.msg import UInt16
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from frg_rover_msgs.msg import sys_states_all
from geometry_msgs.msg import Point
    
state0 = 0
state1 = 0
state2 = 0
state3 = 0
state4 = 0
state5 = 0
state6 = 0
state7 = 0
state8 = 0
state9 = 0

scan_data = LaserScan()


# ----------------------------------------------
def update_states(data):
    global state0
    global state1
    global state2
    global state3
    global state4
    global state5
    global state6
    global state7
    global state8
    global state9

    state0 = data.state0
    state1 = data.state1
    state2 = data.state2
    state3 = data.state3
    state4 = data.state4
    state5 = data.state5
    state6 = data.state6
    state7 = data.state7
    state8 = data.state8
    state9 = data.state9

def update_scan(data):
    global scan_data
    scan_data = data
#-----------------------------------------

def publish_state():

    global state0
    global state1
    global state2
    global state3
    global state4
    global state5
    global state6
    global state7
    global state8
    global state9

    global scan_data

    rospy.Subscriber('/sys_states/sys_states_all',sys_states_all,update_states)
    rospy.Subscriber('/scan_base',LaserScan,update_scan)

    pub = rospy.Publisher('/frg_point_follower/point1',Point)

    rospy.init_node('frg_laser_point_pub', anonymous=True)

    r = rospy.Rate(10)
    point = Point()

    while not rospy.is_shutdown():

        #print scan_data.ranges[0]
        a_min = scan_data.angle_min
        a_inc = scan_data.angle_increment
        a_list = [a_min]
        a_max = a_min
        for i in range(len(scan_data.ranges)-1):
            a_max += a_inc
            a_list.append(a_max)

        # Find min and corresponding angle

        d1 = 100000
        a1 = 100000
        dx = 100000
        dy = 100000

        point_valid = 0

        for i in range(len(scan_data.ranges)):
            if d1 > scan_data.ranges[i]:
                d1 = scan_data.ranges[i]
                a1 = a_list[i]
                point_valid = 1

        if point_valid:

            dx3 =  d1 * numpy.cos(a1)
            dy3 =  d1 * numpy.sin(a1) - 0.2

            dx = 1.0 - dy3
            dy = dx3 - 1.0

            x_offset = 0.0
            y_offset = 0.15 #0.19

            point.x = dx + x_offset
            point.y = dy + y_offset
            pub.publish(point)

        r.sleep()

if __name__ == "__main__": 
    publish_state()












