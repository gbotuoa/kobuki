#!/usr/bin/env python

# experimenting for fun

import roslib
import rospy
import smach
import smach_ros
from bf_alg import *

from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient

# global turning points
turning_goals = [


]


class templateMatcher(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes = ['template_matched'])
        self.template1 = TemplateMatcher('ua_small.png')
        self.template2 = TemplateMatcher('ar_small.png')
        self.sound = SoundClient()

    def execute(self):
        rospy.loginfo('Executing template matcher on the side camera')
        if self.template1.status == 'ready2dock' or self.tempalte2.status == 'ready2dock':
            self.sound.say('found one marker')
            return 'template_matched'

class turning90(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes = ['turned'])
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()
        rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.amcl_cb)
        self.pose = None

    def amcl_cb(self):
        self.pose = msg.pose.pose

    def execute(self):
        rospy.loginfo('Turning 90 degrees')
        qo = np.array([self.pose.orientation.x, self.pose.orientation.y, self.pose.orientation.z, self.pose.orientation.w])
        qz = tf.transformations.quaternion_about_axis(-3.14159/2.0, (0,0,1))
        q = tf.transformations.quaternion_multiply(qo, qz)
        goal = self.pose
        goal.orientation.x = q[0]
        goal.orientation.y = q[1]
        goal.orientation.z = q[2]
        goal.orientation.w = q[3]
        goal = goal_pose(goal)
        self.client.send_goal(goal)
        self.client.wait_for_result()
        return 'turned'

class orbMatcher(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes = ['docked'])
        self.orb1 = OrbTracker('ua_small.png')
        self.orb2 = OrbTracker('ar_small.png')

    def execute(self):
        rospy.loginfo('Executing orb matching on front camera')
        if self.orb.status == 'docked' or self.orb2.status == 'docked':
            return 'docked'


class back2Searching(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes = ['returned'])
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()

    def execute(self):
        rospy.loginfo('Returning back to the track')
        goal = returning_points.pop(0)
        goal = goal_pose(goal)
        self.client.send_goal(goal)
        self.client.wait_for_result()
        return 'returned'

def goal_pose(pose):
    goal_pose = MoveBaseGoal()
    goal_pose.target_pose.header.frame_id = 'map'
    goal_pose.target_pose.header.stamp = rospy.Time.now()
    goal_pose.target_pose.pose.position.x = pose[0][0]
    goal_pose.target_pose.pose.position.y = pose[0][1]
    goal_pose.target_pose.pose.position.z = pose[0][2]
    goal_pose.target_pose.pose.orientation.x = pose[1][0]
    goal_pose.target_pose.pose.orientation.y = pose[1][1]
    goal_pose.target_pose.pose.orientation.z = pose[1][2]
    goal_pose.target_pose.pose.orientation.w = pose[1][3]

    return goal_pose

def main():
    rospy.init_node('simple_state_machine')

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['Done'])

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('searching', templateMatcher(),
                               transitions={'template_matched':'turning90'})
        smach.StateMachine.add('turning90', turning90(),
                               transitions={'turned': 'locking'})
        smach.StateMachine.add('locking', orbMatcher(),
                               transitions={'docked':'returning'})
        smach.StateMachine.add('returning', back2Searching(),
                               transitions={'returned':'searching'})

    sis = smach_ros.IntrospectionServer('simple_viewer', sm, '/SM_ROOT')
    sis.start()

    # Execute SMACH plan
    outcome = sm.execute()
    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    main()
