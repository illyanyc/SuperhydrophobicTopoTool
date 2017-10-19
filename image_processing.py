# image_processing.py method is called to perform Delaunay
# triangulation on the center's of mass; plot lines, calculate lines
# lenght.
#
# The method reult is: Delaunay plot, Distribution of Feature's Widths,
# Distribution of Feature's Pitch, Distribution of Distance between
# the features.
# ----------------------------------------------------------------------

from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from time import strftime
from twilio.rest import Client
from matplotlib.ticker import FormatStrFormatter
import ctypes
import pyperclip
from operator import itemgetter
from easygui import msgbox
import os
import tkMessageBox
from shapely.geometry import LineString, Point, LinearRing, Polygon
from shapely import geometry
matplotlib.use('TkAgg')


def triangulate(array,file,sms,overlay,values,width,height,units,phone,tri,circle_coutours):
    #init method
    #region
    start = strftime("%Y-%m-%d %H:%M:%S")
    print start
    feature_pitch = []
    feature_distance = []
    feature_areas = []
    txt_doc = []
    #bools
    send_sms = sms
    overlay_image = overlay
    _phone = phone
    _tri = tri
    #endregion

    #if dimentions are entered: pixel to distance conversion ratio
    #region
    dimentions_entered = values
    if dimentions_entered == True:
        _width = float(width)
        _height = float(height)
        _units = units
    #endregion

    im = plt.imread(file + "_temp.png")
    countours=circle_coutours

    #preparing the image file for analysis
    #region
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
        feature_areas.append(area)

    #array of points
    attributes = np.array(working_array)
    points = np.array(attributes)
    # endregion

    #Delaunay triangulation
    #region
    tri = Delaunay(points)

    #image overlay prep
    if overlay_image == True:
        implot = plt.imshow(im)

    #plotting points
    plt.triplot(points[:,0], points[:,1], tri.simplices.copy(), color='r')
    plt.plot(points[:, 0], points[:, 1], 'o', color='w')


    #get areas as average_diameter
    feature_diameters = []
    for i in feature_areas:
        d = round(2 * np.sqrt(i / np.pi), 2)
        feature_diameters.append(d)
    # for j, p in enumerate(points):
    #endregion

    #plot points, calculate distances between points
    #region
    for j, s in enumerate(tri.simplices):
        p = points[s].mean(axis=0)

        if _tri == True:
            plt.text(p[0], p[1], '#%d' % j, ha='center') # label triangles

        plt.xlim(0, width);
        plt.ylim(0, height)

        verteces_and_closest_point = []

    for i,s in enumerate(tri.simplices):
        s = tri.simplices[i,:]
        p_arr = points[tri.simplices[i,:]]
        print "simplex: ",s," at: ",i

        verteces = [[0,1],[0,2],[1,2]]

        poly = geometry.Polygon([[p[0], p[1]] for p in p_arr])
        print(poly.wkt)


        Polygon([(1, 1), (2, 3), (3, 1)])
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
            pitch = np.sqrt(sum_x_y)
            print "pitch: ",pitch

            feature_pitch.append(pitch)


    #endregion

    #final answer
    #region
    areas_avg =np.average(feature_areas)
    average_diameter = np.average(feature_diameters)
    average_pitch = round(np.average(feature_pitch),2)
    stdev_pitch = round(np.std(feature_pitch),2)
    stdev_diameter=round(np.std(feature_diameters))
    units = "pixels"

    _feature_diameters = []
    _feature_pitch = []

    if dimentions_entered == True:
        ratio = _width/width
        average_pitch = round(average_pitch*ratio,2)
        stdev_pitch = round(stdev_pitch*ratio,2)
        average_diameter = round(average_diameter*ratio,2)
        units = _units

        for i in feature_diameters:
            new_i=round(i*ratio,2)
            _feature_diameters.append(new_i)

        for i in feature_pitch:
            new_i=round(i*ratio,2)
            _feature_pitch.append(new_i)

    #endregion

    #final answer message
    #region
    _box = []
    _box.append("Average Pitch: ")
    _box.append(str(average_pitch))
    _box.append(" ")
    _box.append(units)
    _box.append(" StDev: ")
    _box.append(str(stdev_pitch))
    _box.append(" ")
    _box.append(units)
    t_box = ''.join(_box)
    plt.text(50,50, t_box, color='black',
             bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))

    end = strftime("%Y-%m-%d %H:%M:%S")
    print end


    #endregion

    #send SMS notification
    #region
    work = False

    if send_sms == True:
        account_sid = "AC285d525ccc60b903e84a0039cf96a386"
        auth_token = "ec8bc7c76b8871bd7d80349c32e045a3"
        client = Client(account_sid, auth_token)
        message_for_sms = []
        message_for_sms.append("AFM Calculation complete! , the average_distance distance between the features is:")
        message_for_sms.append(str(int(average_pitch)))
        message_for_sms.append(" +/ ")
        message_for_sms.append(str(stdev_pitch))
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
    #endregion

    #show overlayed image
    plt.show()


    #Plots:


    #plotting daimeter distributions
    #region
    if dimentions_entered == True:
        d = _feature_diameters
    else: d = feature_diameters

    mean_ = []
    mean_.append("Mean Diameter: ")
    mean_.append(str(average_diameter))
    mean_.append(" Stdev: ")
    mean_.append(str(stdev_diameter))
    mean_.append(" ")
    mean_.append(str(units))
    mean_label = ''.join(mean_)
    fig, ax = plt.subplots()
    d_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=20)
    x_label = "Diameter, "+str(units)
    plt.xlabel(x_label)
    plt.ylabel('Count, n')
    plt.title('Distribution of feature diameters')

    plt.grid(True)
    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

    # Change the colors of bars at the edges...
    twentyfifth, seventyfifth = np.percentile(d, [25, 75])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < twentyfifth:
            patch.set_facecolor('green')
        elif leftside > seventyfifth:
            patch.set_facecolor('yellow')

    # Label the raw counts and the percentages below the x-axis...

    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 65), textcoords='offset points', va='top', ha='center')

        # Label the percentages
        percent = '%0.0f%%' % (100 * float(count) / counts.sum())
        ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 45), textcoords='offset points', va='top', ha='center')
    plt.axvline(x=average_diameter, color="red", linestyle='dashed', linewidth=2)
    plt.text(0, 0, mean_label, color='black', bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
    plt.xticks(rotation=70)

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show(d_plot)
    #endregion

    #plotting feature's pitch
    # region
    if dimentions_entered == True:
        d = _feature_pitch
    else: d = feature_pitch

    _mean = []
    _mean.append("Mean Pitch: ")
    _mean.append(str(average_pitch))
    _mean.append(" Stdev: ")
    _mean.append(str(stdev_pitch))
    _mean.append(" ")
    _mean.append(str(units))
    mean_label = ''.join(_mean)
    fig, ax = plt.subplots()
    f_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=20)
    x_label = "Pitch, " + str(units)
    plt.xlabel(x_label)
    plt.ylabel('Count, n')
    plt.title('Distribution of feature pitch')

    plt.grid(True)
    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

    # Change the colors of bars at the edges...
    twentyfifth, seventyfifth = np.percentile(d, [25, 75])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < twentyfifth:
            patch.set_facecolor('g')
        elif leftside > seventyfifth:
            patch.set_facecolor('yellow')
    max_y_bin = np.max(bins)
    # Label the raw counts and the percentages below the x-axis...
    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 65), textcoords='offset points', va='top', ha='center')

        # Label the percentages
        percent = '%0.0f%%' % (100 * float(count) / counts.sum())
        ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 45), textcoords='offset points', va='top', ha='center')
    plt.axvline(x=average_pitch, color="red", linestyle='dashed', linewidth=2)
    plt.text(0, 0, mean_label, color='black',
             bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
    plt.xticks(rotation=70)

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show(f_plot)
    #endregion

    #calculating and plotting distance between features
    # region
    if dimentions_entered == True:
        d = _feature_pitch
    else:
        d = feature_pitch

    _distances_minus_variationCoefficient = []

    distance_minus_diameter_ratio = (average_pitch - average_diameter) / average_pitch

    for i in d:
        new_i = i * distance_minus_diameter_ratio
        _distances_minus_variationCoefficient.append(new_i)

    stdev_feature_real_distance = round(np.std(_distances_minus_variationCoefficient),2)
    average_feature_real_distane = round(np.average(_distances_minus_variationCoefficient),2)

    _mean = []
    _mean.append("Mean Distance: ")
    _mean.append(str(average_feature_real_distane))
    _mean.append(" Stdev: ")
    _mean.append(str(stdev_feature_real_distance))
    _mean.append(" ")
    _mean.append(str(units))
    mean_label = ''.join(_mean)
    fig, ax = plt.subplots()
    f_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=20)
    x_label = "Distance, " + str(units)
    plt.xlabel(x_label)
    plt.ylabel('Count, n')
    plt.title('Distribution of distance between features')

    plt.grid(True)
    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

    # Change the colors of bars at the edges...
    twentyfifth, seventyfifth = np.percentile(d, [25, 75])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < twentyfifth:
            patch.set_facecolor('g')
        elif leftside > seventyfifth:
            patch.set_facecolor('yellow')
    max_y_bin = np.max(bins)
    # Label the raw counts and the percentages below the x-axis...
    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 65), textcoords='offset points', va='top', ha='center')

        # Label the percentages
        percent = '%0.0f%%' % (100 * float(count) / counts.sum())
        ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, 45), textcoords='offset points', va='top', ha='center')
    plt.axvline(x=average_feature_real_distane, color="red", linestyle='dashed', linewidth=2)
    plt.text(0, 0, mean_label, color='black',
             bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
    plt.xticks(rotation=70)

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show(f_plot)
    # endregion
    #result terminal print-out
    #region
    # messagebox

    #message box string builder
    message_box = "Average Pitch: "+str(average_pitch)+" "+units+" StDev: "+str(stdev_pitch)+" "+units+"; Average Distance between Features: "+str(average_feature_real_distane)+" "+units+" StDev: "+str(stdev_feature_real_distance)+" "+units+"; Average diameter of the features: "+str(average_diameter)+" "+units+" StDev: "+str(stdev_diameter)+" "+units
    mb = message_box

    print mb
    pyperclip.copy("Pitch,"+str(average_pitch)+","+str(stdev_pitch)+",Distance,"+str(average_feature_real_distane)+","+str(stdev_feature_real_distance)+",Diameter,"+str(average_diameter)+","+str(stdev_diameter)+",Units:"+units)
    print "Complete"
    #endregion





