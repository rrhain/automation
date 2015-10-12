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
    title = 'Delvd vs Density Nov Radio'
    xcol = 'Density'
    xlabel = 'Density (nodes/km^2)'
    ycols = ['Delvd']
    ylabel = 'Delivery Ratio'
    # insert the BB's from DATA below
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']
    options=["'s-', linewidth=1"]

class BasicUcastDelayvsLoad_DensityPlot(std_plot):
    title = 'Delay vs Load Nov Radio'
    xcol = 'Density'
    xlabel = 'Density (nodes/km^2)'
    ycols = ['Delay']
    ylabel = 'Delay (sec)'
    # insert the BB's from DATA below
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']
    options=["'s-', linewidth=1"]

class BasicUcastFwdvsLoad_DensityPlot(std_plot):
    title = 'Fwd vs Density Nov Radio'
    xcol = 'Density'
    xlabel = 'Density (nodes/km^2)'
    ycols = ['Fwd']
    ylabel = 'Packets Forwarded per Node'
    # insert the BB's from DATA below
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']
    options=["'s-', linewidth=1"]

# End Basic specs


# Single transceiver runs with varying CWMax and Densities
# E.g. /home/ramanath/sims/Sim1--n40-load-CW/matrix.txt
#    Delivery
class UcastDelvdvsLoad_DensityPlot(BasicUcastDelvdvsLoad_DensityPlot):
    title = ['Delvd vs Density Nodes=50, Speed=2m/s, Load=5kbps']
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']

#    Delay
class UcastDelayvsLoad_DensityPlot(BasicUcastDelayvsLoad_DensityPlot):
    title = ['Delay vs Density Nodes=50, Speed=2m/s, Load=5kbps']
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']

# Fwd
class UcastFwdvsLoad_DensityPlot(BasicUcastFwdvsLoad_DensityPlot):
    title = ['Fwd vs Density Nodes=50, Speed=2m/s, Load=5kbps']
    ydata = ['(Tos==0)', '(Tos==1)', '(Tos==2)', '(Tos==3)']
    legend = ['CR', 'DR', 'Endemic(DrToCrEnabled)', 'Endemic(DrToCrDisabled)']

# End Single transceiver runs


plot_spec = [UcastDelvdvsLoad_DensityPlot, UcastDelayvsLoad_DensityPlot, UcastFwdvsLoad_DensityPlot]


