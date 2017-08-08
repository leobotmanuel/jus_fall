#!/usr/bin/python

# Follow the motion of an object in front of Sharp sensor moving forward-backward

import rospy
from std_msgs.msg import Int32

# Maestro channel assignment
izq = 4
dcho = 5
# Threshold distance: below, change rotation wheel
min_dist= 13 # cm from direct measurement- 11.3 cm from calculations
min_dist_safe= min_dist+1

# LEFT WHEEL
left_fw_speed= 6500# Slow when moving forward
left_bk_speed= 5500# Also slow when moving backward

# RIGHT WHEEL
right_fw_speed= 5500# Slow when moving forward
right_bk_speed= 6500# Also slow when moving backward

# BEGIN CALLBACK
def callback(msg):
    global dist
    dist= msg.data
# END CALLBACK

dist= 50 #Anything to start

# Used for rospy.Rate (should equal or muliple of rate in 'control' node)
cycle = 0.15

class Fall():
	def __init__(self):
		rospy.init_node('follower_control')
		rospy.on_shutdown(self.shutdown)
		# BEGIN SUBSCRIBER
		sub = rospy.Subscriber('sharp_data', Int32, callback)
		# END SUBSCRIBER
		############################################
		# BEGIN PUB: left and right servos speed set
		self.write_left = rospy.Publisher('speed_left', Int32,queue_size=10)
		self.write_right = rospy.Publisher('speed_right', Int32,queue_size=10)
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
			speed_L= left_fw_speed
			speed_R=right_fw_speed
			if dist > min_dist_safe:  #The obstacle is the 'empty' space
			# if dist < min_dist:
			    driving_forward = -1
		    else:
			# Move backward
			#speed_L=  left_bk_speed
			#speed_R= right_bk_speed

			# Do a quick rotation INSTEAD
			speed_L=-1
			speed_R=-1
		
			if dist <= min_dist_safe: # Go ahead while in the inner of the table
			#if dist >= min_dist:
			    driving_forward = 1

		    if driving_forward <> driving_before:
			# Rest one cycle before changing direction
			speed_L=0
			speed_R=0
			driving_before= driving_forward

		    #Publish desired motions
		    self.write_left.publish(speed_L)
		    self.write_right.publish(speed_R)

		    print "Driving forward  ", driving_forward
		    print "Time stamp  (s)  = ", t[0]        
		    print "Distance to target (cm)   = ", d[0]
		    print "Relative speed of target (cm/s)= ", v[0]
		    print ""
		    print "Speed_L= ", speed_L, "Speed_R =", speed_R
		    print "----------------------------------------------------------------------"
		    rate.sleep()

	def shutdown(self):
		rospy.loginfo("Stop")
		self.write_right.publish(0)
		self.write_left.publish(0)
		rospy.sleep(1)

if __name__ == '__main__':
	try:
		Fall()
	except:
		rospy.loginfo("node terminated.")

# END ALL
