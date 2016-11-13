#!/usr/bin/python

# Follow the motion of an object in front of Sharp sensor moving forward-backward

import rospy
from std_msgs.msg import Int32

# Maestro channel assignment
izq = 4
dcho = 5
# Threshold distance: below, change rotation wheel
min_dist= 30 # 23.1 # Corresponds to an output of 250 from Sharp sensor

# BEGIN CALLBACK
def callback(msg):
    global dist
    dist= msg.data
# END CALLBACK

dist= 50 #Anything to start

# Used for rospy.Rate (should equal or muliple of rate in 'control' node)
cycle = 0.5
rospy.init_node('follower_control')

# BEGIN SUBSCRIBER
sub = rospy.Subscriber('sharp_data', Int32, callback)
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
v=[0] * n
t = [float(x) for x in t]
d = [float(x) for x in d]
v = [float(x) for x in v]
# Initial element in each list
#t[0]= rospy.Time.now()- rospy.Duration(cycle)
t[0]= rospy.get_time()
d[0]= dist
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
        v[k+1]= v[k]
    # Last element on top (LIFO stack)
    t[0]= rospy.get_time()
    d[0]= dist
    D0=d[0]-d[1]
    T0=t[0]-t[1]
    v[0]=D0/T0
    
    if driving_forward == 1: # If driving forward
        # GO AHEAD towards the target
        speed_L= -1
        speed_R=  1
        if dist < min_dist:
            driving_forward = -1
    else:
        # Move backward
        speed_L=  1
        speed_R= -1
        if dist >= min_dist:
            driving_forward = 1

    if driving_forward <> driving_before:
        # Rest one cycle before changing direction
        speed_L=0
        speed_R=0
        driving_before= driving_forward

    #Publish desired motions
    write_left.publish(speed_L)
    write_right.publish(speed_R)

    print "Driving forward  ", driving_forward
    print "Time stamp  (s)  = ", t[0]        
    print "Distance to target (cm)   = ", d[0]
    print "Relative speed of target (cm/s)= ", v[0]
    print ""
    print "Speed_L= ", speed_L, "Speed_R =", speed_R
    print "----------------------------------------------------------------------"
    rate.sleep()
# END LOOP
# END ALL
