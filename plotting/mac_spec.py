# This is the plot specification file to be edited by users.  Each class
# inherits properties from the standard plot classes defined in plot_lib.  Each
# represents an individual plot.  Classes must be added to the plot_spec list.
#
# Within each class, one can define plot parameters:
#   imgsize  -  Tuple of inches for plot size: e.g. (10,5)
#   rcparams -  global configs for pyplot's rcParams hash
#               {'legend.fontsize':'medium',
#                'axes.grid':True,
#                'grid.color':'lightgrey',
#                #'help':'print all valid keys',
#                }
#   xcol    -   Column to use for x-axis
#   xlabel  -   X-axis label.  Defaults to selected column name.
#   ycols   -   List of columns to plot.  This list will be iterated through
#               with each data selector.  If the number of items in this list is
#               less than the number of data selectors, the last column will be
#               used for all remaining data selectors.  If only one column is
#               supplied, it will be used for all data selectors.  Arithmetic
#               may be done on columns here.
#   ydata   -   List of data to plot.  This list consists of constraints
#               defining rows to select for the plot.  For line plots, each list
#               item will map to a different line.
#   ylabel  -   Y-axis label.  Defaults to first column name.
#   title   -   Plot title.
#   aliases -   Allows long column names to be aliased to more friendly names.
#               Semicolon delimited string.  Arithmetic can also be done here.
#   options -   Option string to pass to plotting primitive.  This can define
#               line type, color, weight, etc.
#   y2label   - Label for second y axis
#   y2cols    - Columns for second y axis
#   y2options - Option string for second y axis
#   disable -   Disable plotting of this spec.
#   legend  -   List of legend entries.  Defaults to the data selector
#               constraint for each plot element (eg ydata).  
#   legend_pos  - Position of the legend.  Valid values are: POS_BEST (default),
#                 POS_UPRIGHT, POS_UPLEFT, POS_LOWLEFT, POS_LOWRIGHT, POS_RIGHT,
#                 POS_CENTERLEFT, POS_CENTERRIGHT, POS_LOWCENTER, POS_UPCENTER,
#                 POS_CENTER
#   legend_alpha- Legend alpha channel [0..1].  0=transparent, 1=opaque.

from plot_lib import *

# Basic specs 1 xcvr, varying loads and densities plotted vs load

class BasicUcastDelvdvsLoad_DensityPlot(std_plot):
    title = 'Delvd vs Load Nov Radio'
    xcol = 'Load'
    xlabel = 'Load (kbps)'
    ycols = ['Delvd']
    ylabel = 'Delivery Ratio'
    # insert the BB's from DATA below
    ydata = ['(BB==447)', '(BB==800)']
    legend = ['Higher density', 'Lower density']

class BasicUcastDelayvsLoad_DensityPlot(std_plot):
    title = 'Delay vs Load Nov Radio'
    xcol = 'Load'
    xlabel = 'Load (kbps)'
    ycols = ['Delay']
    ylabel = 'Delay (sec)'
    ydata = ['(BB==447)', '(BB==800)']
    legend = ['Higher density', 'Lower density']

class BasicMcastDelvdvsLoad_DensityPlot(BasicUcastDelvdvsLoad_DensityPlot):
    ycols = ['Delvd/(GrpSize-1)']

class BasicMcastDelayvsLoad_DensityPlot(BasicUcastDelayvsLoad_DensityPlot):
    ycols = ['Delay']

# End Basic specs


# Single transceiver runs with varying CWMax and Densities
# E.g. /home/ramanath/sims/Sim1--n40-load-CW/matrix.txt
#    Delivery
class McastDelvdvsLoadBB447_CWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 Nodes, Nov Radio, BB 447']
    ydata = ['(CWMax==40) & (BB==447)', '(CWMax==400) & (BB==447)', '(CWMax==1600) & (BB==447)']
    legend = ['(5,40)', '(50,400)', '(200,1600)']

class McastDelvdvsLoadBB800_CWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 nodes, Nov radio, BB 800']
    ydata = ['(CWMax==40) & (BB==800)', '(CWMax==400) & (BB==800)', '(CWMax==1600) & (BB==800)']
    legend = ['(5,40)', '(50,400)', '(200,1600)']

class McastDelvdvsLoadCW200_DensityPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 nodes, Nov radio, CW=(50,400)']
    ydata = ['(CWMax==200) & (BB==447)', '(CWMax==200) & (BB==800)']
    legend = ['Higher density', 'Lower density']

class McastDelvdvsLoadCW400_DensityPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 nodes, Nov radio, CW=(50,400)']
    ydata = ['(CWMax==400) & (BB==447)', '(CWMax==400) & (BB==800)']
    legend = ['Higher density', 'Lower density']

#    Delay
class McastDelayvsLoadBB447_CWPlot(BasicMcastDelayvsLoad_DensityPlot):
    ydata = ['(CWMax==40) & (BB==447)', '(CWMax==400) & (BB==447)', '(CWMax==1600) & (BB==447)']
    legend = ['(5,40)', '(50,400)', '(200,1600)']

class McastDelayvsLoadBB800_CWPlot(BasicMcastDelayvsLoad_DensityPlot):
    ydata = ['(CWMax==40) & (BB==800)', '(CWMax==400) & (BB==800)', '(CWMax==1600) & (BB==800)']
    legend = ['(5,40)', '(50,400)', '(200,1600)']

class McastDelayvsLoadCW200_DensityPlot(BasicMcastDelayvsLoad_DensityPlot):
    ydata = ['(CWMax==200) & (BB==447)', '(CWMax==200) & (BB==800)']
    legend = ['Higher density', 'Lower density']

class McastDelayvsLoadCW400_DensityPlot(BasicMcastDelayvsLoad_DensityPlot):
    ydata = ['(CWMax==400) & (BB==447)', '(CWMax==400) & (BB==800)']
    legend = ['Higher density', 'Lower density']

# End Single transceiver runs

# Begin 4 xcvr runs
# E.g. /home/ramanath/sims/Sim1/n40-CW50--xcvrs-load

class McastDelvdvsLoadBB447_xcvrsPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 nodes, Nov radio,  BB 447, CW=(50,400)']
    ydata = ['(NXcvrs==1) & (BB==447)', '(NXcvrs==2) & (BB==447)', '(NXcvrs==3) & (BB==447)', '(NXcvrs==4) & (BB==447)']
    legend = ['1 xcvr', '2 xcvr', '3 xcvr', '4 xcvr']

class McastDelvdvsLoadBB800_xcvrsPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, 40 nodes, Nov radio BB 800, CW=(50,400)']
    ydata = ['(NXcvrs==1) & (BB==800)', '(NXcvrs==2) & (BB==800)', '(NXcvrs==3) & (BB==800)', '(NXcvrs==4) & (BB==800)']
    legend = ['1 xcvr', '2 xcvr', '3 xcvr', '4 xcvr']

class McastDelayvsLoadBB447_xcvrsPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, 40 nodes, Nov radio,  BB 447, CW=(50,400)']
    ydata = ['(NXcvrs==1) & (BB==447)', '(NXcvrs==2) & (BB==447)', '(NXcvrs==3) & (BB==447)', '(NXcvrs==4) & (BB==447)']
    legend = ['1 xcvr', '2 xcvr', '3 xcvr', '4 xcvr']

class McastDelayvsLoadBB800_xcvrsPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, 40 nodes, Nov radio BB 800, CW=(50,400)']
    ydata = ['(NXcvrs==1) & (BB==800)', '(NXcvrs==2) & (BB==800)', '(NXcvrs==3) & (BB==800)', '(NXcvrs==4) & (BB==800)']
    legend = ['1 xcvr', '2 xcvr', '3 xcvr', '4 xcvr']

class McastDelvdvsGrpSizeBB447_xcvrsPlot(McastDelvdvsLoadBB447_xcvrsPlot):
    title = ['Delvd vs GrpSize, 40 nodes, Nov radio, BB 447, CW=(50,400)']
    xcol = 'GrpSize'
    xlabel = ['Group size']

class McastDelvdvsGrpSizeBB800_xcvrsPlot(McastDelvdvsLoadBB800_xcvrsPlot):
    title = ['Delvd vs GrpSize, 40 nodes, Nov radio, BB 800, CW=(50,400)']
    xcol = 'GrpSize'
    xlabel = ['Group size']

# End 4 xcvr runs


# Begin Adaptive CW
# This compares 3 adaptive schemes and 3 fixed schemes with 2x2 combinations of GrpSize and Density

# Delivery

class McastDelvdvsLoadBB447GrpSize10_AdaptiveCWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, BB 447, GrpSz 10']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelvdvsLoadBB447GrpSize40_AdaptiveCWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, BB 447, GrpSz 40']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelvdvsLoadBB800GrpSize10_AdaptiveCWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, BB 800, GrpSz 10']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelvdvsLoadBB800GrpSize40_AdaptiveCWPlot(BasicMcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Load, BB 800, GrpSz 40']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


# Delay

class McastDelayvsLoadBB447GrpSize10_AdaptiveCWPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, BB 447, GrpSz 10']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==447) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==447) & (GrpSize==10)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelayvsLoadBB447GrpSize40_AdaptiveCWPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, BB 447, GrpSz 40']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==447) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==447) & (GrpSize==40)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelayvsLoadBB800GrpSize10_AdaptiveCWPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, BB 800, GrpSz 10']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==800) & (GrpSize==10)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==800) & (GrpSize==10)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


class McastDelayvsLoadBB800GrpSize40_AdaptiveCWPlot(BasicMcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Load, BB 800, GrpSz 40']
    ydata = ['(CWMaxHOL==40) & (CWMaxLOL==1600) & (CWMinHOL==5) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)', 
             '(CWMaxHOL==1600) & (CWMaxLOL==1600) & (CWMinHOL==200) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==40) & (CWMinHOL==5) & (CWMinLOL==5) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==400) & (CWMinHOL==50) & (CWMinLOL==50) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==40) & (CWMaxLOL==400) & (CWMinHOL==5) & (CWMinLOL==50) & (BB==800) & (GrpSize==40)',
             '(CWMaxHOL==400) & (CWMaxLOL==1600) & (CWMinHOL==50) & (CWMinLOL==200) & (BB==800) & (GrpSize==40)']
    legend = ['(A 5,40,200,1600)', '(F 200,1600)', '(F 5,40)', '(F 50,400)', '(A 5,40,50,400)', '(A 50,400,200,1600)']


#plot_spec = [DelvdPlot,DelayPlot]
#plot_spec = [McastDelvdvsLoadBB800_CWPlot,McastDelayvsLoadBB800_CWPlot]

#plot_spec = [McastDelvdvsLoadBB447_xcvrsPlot,McastDelvdvsLoadBB800_xcvrsPlot,McastDelayvsLoadBB447_xcvrsPlot,McastDelayvsLoadBB800_xcvrsPlot]
#plot_spec = [McastDelvdvsGrpSizeBB447_xcvrsPlot,McastDelvdvsGrpSizeBB800_xcvrsPlot]

plot_spec = [McastDelvdvsLoadBB447GrpSize10_AdaptiveCWPlot,McastDelvdvsLoadBB447GrpSize40_AdaptiveCWPlot,
             McastDelvdvsLoadBB800GrpSize10_AdaptiveCWPlot,McastDelvdvsLoadBB800GrpSize40_AdaptiveCWPlot,
             McastDelayvsLoadBB447GrpSize10_AdaptiveCWPlot,McastDelayvsLoadBB447GrpSize40_AdaptiveCWPlot,
             McastDelayvsLoadBB800GrpSize10_AdaptiveCWPlot,McastDelayvsLoadBB800GrpSize40_AdaptiveCWPlot]



