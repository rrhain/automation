# Library of base classes for different types of plots.

(POS_BEST, POS_UPRIGHT, POS_UPLEFT, POS_LOWLEFT, POS_LOWRIGHT, 
 POS_RIGHT, POS_CENTERLEFT, POS_CENTERRIGHT, POS_LOWCENTER, 
 POS_UPCENTER, POS_CENTER) = range(0, 11)

# The base class for all plots.
class base_plot:
    imgsize  = None #(10,5) #inches
    rcparams = {}

    title = ''

    aliases = ''

    fcn = None

    xcol = None
    xdata = None
    xerrcols = None
    xlabel = None

    ycols = []
    y2cols = None
    ydata = []
    y2data = None
    yerrcols = None
    y2errcols = None
    ylabel = None
    y2label = None

    my_axis = None
    clone_axis = None

    legend = None
    legend_pos = POS_BEST
    legend_alpha = 0.5

    options = ['']
    y2options = ['']

    disable = False
    padding = True

    postproc = None

# Standard line plot.  Put defaults here.
class std_plot(base_plot):
    fcn = 'plot'
    # options=["'s-', linewidth=1", "'v-', linewidth=3"]

# Standard error bar plot.  Put defaults here.
class std_errbar(base_plot):
    fcn = 'errorbar'

# Standard histogram plot.  Put defaults here.
class std_hist(base_plot):
    fcn = 'hist'
    #options=["bins=8"]
    padding = False

# Standard error bar plot.  Put defaults here.
class std_bar(base_plot):
    fcn = 'bar'

uniform_axes=None
