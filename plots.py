from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
matplotlib.use('TkAgg')

def histogram_plot(d,units,plot_name,x_axis):

    average = np.average(d)
    stdev = np.std(d)
    mean_ = []

    mean_.append("Mean: ")
    mean_.append(str(average))
    mean_.append(" Stdev: ")
    mean_.append(str(stdev))
    mean_.append(" ")
    mean_.append(str(units))
    mean_label = ''.join(mean_)
    fig, ax = plt.subplots()
    d_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=15)
    x_label = x_axis+str(units)
    plt.xlabel(x_label,fontsize=21)
    plt.ylabel('Count, n',fontsize=21)
    plt.title(plot_name, fontsize=24)

    plt.grid(True)
    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))

    # Change the colors of bars at the edges...
    fiftyfifth, _fiftyfifth = np.percentile(d, [50, 50])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < fiftyfifth:
            patch.set_facecolor('grey')
        elif leftside > _fiftyfifth:
            patch.set_facecolor('grey')

    # Label the raw counts and the percentages below the x-axis...

    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    #for count, x in zip(counts, bin_centers):
        # Label the raw counts
        #ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
         #           xytext=(0, 65), textcoords='offset points', va='top', ha='center',rotation=90)

        # Label the percentages
        #percent = '%1.0f%%' % (100 * float(count) / counts.sum())
        #ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
        #           xytext=(0, 45), textcoords='offset points', va='top', ha='center')
    plt.axvline(x=average, color="red", linestyle='dashed', linewidth=2)
    #plt.text(0, 0, mean_label, color='black', bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
    plt.xticks(rotation=70, fontsize=18)
    plt.yticks(fontsize=18)

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show(d_plot)

    message_box(x_axis,units,average,stdev)

def message_box(x_axis,units,avg,stdev):
    try:
        message_box1 = x_axis+str(round(avg,0))+" "+units+" StDev: "+str(round(stdev,0))+" "+units
        print message_box1
    except: print ""