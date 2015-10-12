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
#   y2cols    - Columns for second y axis
#   y2label   - Label for second y axis
#   y2options - Option strings for series on the second y axis
#   disable -   Disable plotting of this spec.
#   legend  -   List of legend entries.  Defaults to the data selector
#               constraint for each plot element (eg ydata).
#   legend_pos  - Position of the legend.  Valid values are: POS_BEST (default),
#                 POS_UPRIGHT, POS_UPLEFT, POS_LOWLEFT, POS_LOWRIGHT, POS_RIGHT,
#                 POS_CENTERLEFT, POS_CENTERRIGHT, POS_LOWCENTER, POS_UPCENTER,
#                 POS_CENTER
#   legend_alpha- Legend alpha channel [0..1].  0=transparent, 1=opaque.

from plot_lib import *

class GenPlot(std_plot):
    title = 'SHARE Plot'
    aliases = 'Var = SYSMGR_MACMacPhyDelayTicks; Foo = SYSMGR_MACPhyCCADelayTicks'
    ycols = ['Rcv/BB'] # Ensemble divide
    ydata = ['(Var < 10) & (Foo == 5)', '(Var > 200) & (Foo > 40)']

class MyDlvd(std_plot):
    title = 'Delivery Ratio vs Data Rate for Duty Cycle 10%'
    xcol = 'Data_Rate'
    ycols = ['Recv']
    ydata = ['(Contention_Range == 250) & (Duty_Cycle == 10)', '(Contention_Range == 500) & (Duty_Cycle == 10)']
    legend = ['CR=250', 'CR=500']
    options=['linestyle="dashed"']


class TestHist(std_bar):
    title = '10% Duty Cycle'
    xcol = 'Data_Rate'
    ycols = ['Data_Gen_Fwd']
    ydata = ['(Duty_Cycle == 10)']

# Plot classes must be added to this list to be processed.
plot_spec = [MyDlvd, TestHist]
#plot_spec = [MyDelay, MyDelayNew, AnotherOne]
