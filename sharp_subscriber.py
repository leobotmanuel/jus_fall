#!/usr/bin/env python
# BEGIN ALL
#!/usr/bin/env python


import rospy
from std_msgs.msg import Int32


# BEGIN CALLBACKs
def callback(msg):
    print ""
    print "--------- distance LEFT sensor (channel 0)=", msg.data, "cm"

def callback2(msg):
    print "--------- distance RIGHT sensor (channel 3)=", msg.data, "cm"    
# END CALLBACKs

rospy.init_node('sharp_reader')

# BEGIN SUBSCRIBER
sub = rospy.Subscriber('sharp_data', Int32, callback)
sub2= rospy.Subscriber('sharp_data2', Int32, callback2)
# END SUBSCRIBER

rospy.spin()
# END ALL
