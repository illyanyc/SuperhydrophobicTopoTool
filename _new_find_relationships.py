from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import cv2
from time import strftime
from twilio.rest import Client
import tkMessageBox

def triangulate(array,file,sms,overlay,values,width,height,units,phone,tri):
    #init method
    start = strftime("%Y-%m-%d %H:%M:%S")
    print start
    distances = []
    areas = []

    #bools
    send_sms = sms
    overlay_image = overlay
    _phone = phone
    _tri = tri

    #enter dimentions
    dimentions_entered = values
    if dimentions_entered == True:
        _width = float(width)
        _height = float(height)
        _units = units


    im = plt.imread(file + "_temp.png")

    #image to analyze - need height and width
    image_path = file
    image = cv2.imread(image_path, 0)
    width = image.shape[1]
    height = image.shape[0]
    working_array = []

    for a in array:
        x=a[1]
        y=a[2]
        working_array.append([x,y])

    for b in array:
        area = b[4]
        areas.append(area)

    #array of points
    attributes = np.array(working_array)
    points = np.array(attributes)

    #Delaunay magic
    tri = Delaunay(points)

    #image overlay prep
    if overlay_image == True:
        implot = plt.imshow(im)

    #plotting points
    plt.triplot(points[:,0], points[:,1], tri.simplices.copy())
    plt.plot(points[:, 0], points[:, 1], 'o')

    #for j, p in enumerate(points):

    #main calc loop
    for j, s in enumerate(tri.simplices):
        p = points[s].mean(axis=0)

        if _tri == True:
            plt.text(p[0], p[1], '#%d' % j, ha='center') # label triangles
        plt.xlim(0, width);
        plt.ylim(0, height)

    for i,s in enumerate(tri.simplices):
        s = tri.simplices[i,:]
        p_arr = points[tri.simplices[i,:]]
        print "simplex: ",s," at: ",i
        verteces = [[0,1],[0,2],[1,2]]

        for v in verteces:
            xy1=p_arr[v[0]]
            xy2=p_arr[v[1]]

            x1=xy1[0]
            y1=xy1[1]
            x2=xy2[0]
            y2=xy2[1]

            diff_x = x2-x1
            diff_y = y2-y1
            #print diff_x,diff_y
            abs_diff_x = np.abs(diff_x)
            abs_diff_y = np.abs(diff_y)
            x_squared = abs_diff_x ** 2
            y_squared = abs_diff_y ** 2
            sum_x_y = x_squared + y_squared
            distance = np.sqrt(sum_x_y)
            print "distance: ",distance
            distances.append(distance)

    # final answer
    areas_avg =np.average(areas)
    diameter = round(2*np.sqrt(areas_avg*np.pi),2)
    average = round(np.average(distances),2)
    standard_deviation = round(np.std(distances),2)
    units = "pixels"

    if dimentions_entered == True:
        ratio = _width/width
        average = round(average*ratio,2)
        standard_deviation = round(standard_deviation*ratio,2)
        diameter = round(diameter*ratio,2)
        units = _units

    end = strftime("%Y-%m-%d %H:%M:%S")
    print end

    #messagebox
    message_box = []
    message_box.append("Average Distance: ")
    message_box.append(str(average))
    message_box.append(" StDev: ")
    message_box.append(str(standard_deviation))
    message_box.append(" ")
    message_box.append(units)
    message_box.append(". The diameter of the features: ")
    message_box.append(str(diameter))
    message_box.append(" ")
    message_box.append(units)
    mb = ''.join(message_box)

    #print message
    tkMessageBox.showinfo("Results", mb)
    print "Complete"

    # send SMS notification
    work = False

    if send_sms == True:
        account_sid = "AC285d525ccc60b903e84a0039cf96a386"
        auth_token = "ec8bc7c76b8871bd7d80349c32e045a3"
        client = Client(account_sid, auth_token)
        message_for_sms = []
        message_for_sms.append("AFM Calculation complete! , the average distance between the features is:")
        message_for_sms.append(str(int(average)))
        message_for_sms.append(" +/ ")
        message_for_sms.append(str(standard_deviation))
        message_for_sms.append(" ")
        message_for_sms.append(units)
        message_for_sms.append(" The calculation started at: ")
        message_for_sms.append(str(start))
        message_for_sms.append(" and ended at: ")
        message_for_sms.append(str(end))
        message_for_sms.append(".")
        message_for_sms.append(" File name: ")
        message_for_sms.append(file)
        message_to_send = ''.join(message_for_sms)
        print message_for_sms
        message = client.messages.create(
            to=_phone,
            from_="+14155247927",
            body=message_to_send)
        print(message.sid)

    #show overlayed image
    plt.show()



