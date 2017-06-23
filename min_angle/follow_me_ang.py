#!/usr/bin/python

# Follow the motion of an object in front of Sharp sensor moving forward-backward

import rospy
from std_msgs.msg import Int32

# Maestro channel assignment
izq = 4
dcho = 5
# Threshold distance: below, change rotation wheel
min_dist= 13 # cm from direct measurement- 11.3 cm from calculations
min_dist_safe= min_dist+2

# LEFT WHEEL
left_fw_speed= 6500# SLOW when moving forward
left_bk_speed= 5500# SLOW when moving backward
left_fw_fast= 6800# FAST when moving forward
left_bk_fast= 5400# FAST when moving backward

# RIGHT WHEEL
right_fw_speed= 5500# SLOW when moving forward
right_bk_speed= 6500# SLOW when moving backward
right_fw_fast= 5400# FAST when moving forward
right_bk_fast= 6800# FAST when moving backward

# BEGIN CALLBACK
#Callback for first sensor
def callback(msg):
    global dist
    dist= msg.data
#Callback for second sensor
def callback2(msg):
    global dist2
    dist2= msg.data
# END CALLBACK

dist= 50  #Anything to start
dist2= 50
# Used for rospy.Rate (should equal or muliple of rate in 'control' node)
cycle = 0.15
rospy.init_node('follower_control')

# BEGIN SUBSCRIBER
sub = rospy.Subscriber('sharp_data', Int32, callback)
sub2= rospy.Subscriber('sharp_data2', Int32, callback2)
# END SUBSCRIBER
############################################
# BEGIN PUB: left and right servos speed set
write_left = rospy.Publisher('speed_left', Int32,queue_size=10)
write_right = rospy.Publisher('speed_right', Int32,queue_size=10)
# END PUB
############################################

### Preparation of lists to record trajectories
n=10 # Lenght of records
# Lists of time, distance and speed
t= [0] * n
d=[0] * n
d2=[0]* n
v=[0] * n
v2=[0] * n
t = [float(x) for x in t]
d = [float(x) for x in d]
d2= [float(x) for x in d2]
v = [float(x) for x in v]
# Initial element in each list
#t[0]= rospy.Time.now()- rospy.Duration(cycle)
t[0]= rospy.get_time()
d[0]= dist
d2[0]= dist2
v[0]= 0
# Obtain the sign of a number
sign = lambda x: (x>0) - (x<0)

# BEGIN LOOP
rate = rospy.Rate(1/cycle)
driving_forward = 1
driving_before= driving_forward

while not rospy.is_shutdown():
    # Move down all items 1 position
    for k in range(0,n-1):
        t[k+1]= t[k]
        d[k+1]= d[k]
        d2[k+1]= d2[k]
        v[k+1]= v[k]
    # Last element on top (LIFO stack)
    t[0]= rospy.get_time()
    d[0]= dist
    D0=d[0]-d[1]
    D0_2=d2[0]-d[1]
    T0=t[0]-t[1]
    v[0]=D0/T0
    v2[0]=D0_2/T0
    
    if driving_forward == 1: # If driving forward
        # GO AHEAD towards the target
        speed_L= left_fw_speed
        speed_R=right_fw_speed
        #The obstacle is the 'empty' space    
        if dist > min_dist_safe or dist2 > min_dist_safe:
            driving_forward = -1
    else:
        # Edge detected with first sensor (front-LEFT)
        if dist > min_dist_safe:
            # Rotation CLOCKWISE
            #speed_L=-1
            #speed_R=-1
            speed_L=  left_fw_fast
            speed_R= right_bk_fast
        # Edge detected with second sensor (front-RIGHT)
        elif dist2 > min_dist_safe:
            # Rotation COUNTERCLOCKWISE
            #speed_L=1
            #speed_R=1
            speed_L=  left_bk_fast
            speed_R= right_fw_fast
        # Go ahead while in the inner of the table
        elif dist < min_dist_safe and dist2 < min_dist_safe:
            driving_forward = 1

    if driving_forward <> driving_before: # driving_before was set to FORWARD
        # Rest one cycle before changing direction
        speed_L=0
        speed_R=0
        driving_before= driving_forward

    #Publish desired motions
    write_left.publish(speed_L)
    write_right.publish(speed_R)

    rate.sleep()
# END LOOP
# END ALL
