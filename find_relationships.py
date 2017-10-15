import cv2
import numpy as np
from time import gmtime, strftime
from twilio.rest import Client
from time import sleep
import progressbar
import sys
import csv
import time
import main

global counter

def isBetween(a_x, a_y, b_x, b_y, c_x, c_y):

    dxc = c_x - a_x;
    dyc = c_y - a_y;

    dxl = b_x - a_x;
    dyl = b_y - a_y;

    cross = dxc * dyl - dyc * dxl;
    if cross >-1:
        if cross == 0:
            #print "Point on line", cross
            return True

    #print "Point does not fall on the line: ", a_x, a_y, b_x, b_y, c_x, c_y, "Cross Product: ", crossproduct
    #print "Point NOT on line", cross
    return False

    global true_averaged_neibors
def find_relationships(array,fileToOpen):
    start= strftime("%Y-%m-%d %H:%M:%S")
    print start
    global counter
    global pbarval
    print "Processing..."
    attributes = array
    image_path = fileToOpen
    image = cv2.imread(image_path,0)
    width = image.shape[1]
    height = image.shape[0]
    number_of_angles = 360
    tmp = np.zeros_like(image)
    new_image = cv2.imread(image_path+"_temp.png",0)

    #Demo
    a=attributes[1]
    centroid_x = a[1]
    centroid_y = a[2]
   # print centroid_x
   # print centroid_y
    for i in range(number_of_angles):
        N = number_of_angles
        theta = i * (360 / N)
        theta *= np.pi / 180.0
        cv2.line(tmp, (centroid_x, centroid_y),(int(centroid_x + np.cos(theta) * width),int(centroid_y - np.sin(theta) * height)), 255, 1)

    cv2.imshow('Demo/Check "Point Number 30"', tmp)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()
    lenght = len(attributes)
    counter = 0
    print "Number of Items: ", lenght
    #Calculation
    true_averaged_neibors = []
    true_neightbors = []
    for a in attributes:
        counter = counter + 1

        print counter," Items Complete"

        #take in params


        centroid_x = a[1]
        centroid_y = a[2]

        #create lines aat 360deg and loop over line params

        for i in range(number_of_angles):
            line_neighbors = []
            N = number_of_angles
            theta = i * (360 / N)
            theta *= np.pi / 180.0
            endpoint_x = int(centroid_x + np.cos(theta) * width)
            endpoint_y = int(centroid_y - np.sin(theta) * height)

            #loop ever list elems to match coords
            for b in attributes:
                if b[0] != a[0]:
                    c = b[3]
                    for cc in c:
                        mid_point_x = cc[0,0]
                        mid_point_y = cc[0,1]
                        end_x = b[1]
                        end_y = b[2]
                        point_check = isBetween(centroid_x, centroid_y, endpoint_x, endpoint_y, mid_point_x, mid_point_y)
                        if point_check == True:
                            diff_x=centroid_x-mid_point_x
                            diff_y=centroid_y-mid_point_y
                            abs_diff_x=np.abs(diff_x)
                            abs_diff_y=np.abs(diff_y)
                            x_squared=abs_diff_x**2
                            y_squared=abs_diff_y**2
                            sum_x_y=x_squared+y_squared
                            distance = np.sqrt(sum_x_y)
                            #print "distance:",distance
                            neightbors_name=b[0]
                            line_neighbors.append([neightbors_name,distance,end_x,end_y])

            try:
                line_true_value = min(line_neighbors, key = lambda t: t[1])
                #print "list of ditances ", line_neighbors, "minimum value: ", line_true_value
                #print line_true_value
                true_neightbors.append(line_true_value)
                #print true_neightbors
            except: log = ""

            #record just ditances between elems
    just_distances = []

    #true_neightbors_sorted = true_neightbors
    #true_neightbors_sorted_sorted = set()
    #[item for item in true_neightbors_sorted if item[0] not in true_neightbors_sorted_sorted and not true_neightbors_sorted_sorted.add(item[0])]
    true_neightbors_count = len(true_neightbors)
    #print "Lenght of true_neighbors_cleaned", true_neightbors_count

    #average things
    for d in range(0,true_neightbors_count):
        neighbor_average_distance = []
        neighbor_average_x = []
        neighbor_average_y = []
        for e in true_neightbors:

            if d == e[0]:
                #print d
                #print e[0], e[1]
                neighbor_average_distance.append(e[1])
                neighbor_average_x.append(e[2])
                neighbor_average_y.append(e[3])
        try:
            distance_avg=sum(neighbor_average_distance)/len(neighbor_average_distance)
            #print "distance; ",distance_avg
            x_avg = sum(neighbor_average_x)/len(neighbor_average_x)
            y_avg = sum(neighbor_average_y)/len(neighbor_average_y)
            #name = d
            just_distances.append(distance_avg)
            #print "just_distance; ",just_distances
            true_averaged_neibors.append([distance_avg, x_avg, y_avg])
        except: log = ""


    #plotting the lines
    for a in attributes:

        print "Finalizing calculation (obtaining average values)"

        centroid_x = a[1]
        centroid_y = a[2]
        cv2.drawContours(image, [c], -1, (0, 255, 0), 1)
        cv2.circle(image, (centroid_x, centroid_y), 2, (71, 99, 255), -1)
        for b in true_averaged_neibors:
            #if a[0] == b[0]:
            mid_point_x = b[1]
            mid_point_y = b[2]
            try:
                cv2.line(new_image, (centroid_x, centroid_y), (int(mid_point_x), int(mid_point_y)), 255,
                         1)
            except:
                print "Can't plot line"

    #final answer
    total_average = sum(just_distances)/len(just_distances)
    standard_deviation = np.std(just_distances)
    message = "Average Distance: ", total_average, " StDev: ",standard_deviation
    print message
    end = strftime("%Y-%m-%d %H:%M:%S")
    print end
    print "Complete"


    # send SMS notification
    account_sid = "AC285d525ccc60b903e84a0039cf96a386"
    auth_token = "ec8bc7c76b8871bd7d80349c32e045a3"
    client = Client(account_sid, auth_token)
    message_for_sms = []
    message_for_sms.append("AFM Calculation complete! , the average distance between the features is:")
    message_for_sms.append(str(int(total_average)))
    message_for_sms.append(" pixels. ")
    message_for_sms.append("The calculation started at: ")
    message_for_sms.append(str(start))
    message_for_sms.append(" and ended at: ")
    message_for_sms.append(str(end))
    message_for_sms.append(".")
    message_for_sms.append(" File name: ")
    message_for_sms.append(fileToOpen)

    message_to_send = ''.join(message_for_sms)

    print message_for_sms
    message = client.messages.create(
        to="+13479794471",
        from_="+14155247927",
        body=message_to_send)
    print(message.sid)


    cv2.imshow('Result', new_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()