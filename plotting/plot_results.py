#!/usr/bin/python

import os
import sys
import string
import time
import warnings
import operator

from string import Template
from optparse import OptionParser

myRelPath="pirana-opnet/automation/"

parser = OptionParser()
parser.add_option("-d", dest="datestamp", action="store_true",
        help="Add date and time stamps to output file names", default=False)
parser.add_option("-D", action="store_true", dest="debug",
        help="Debug mode", default=False)
parser.add_option("-e", dest="plot_env", 
        help="Path to plot environment file", default=None)
parser.add_option("-f", dest="fname", 
        help="2D matrix input file name", default=None)
parser.add_option("-o", dest="oprefix", 
        help="Output plots to files using prefix", default="test")
parser.add_option("-p", dest="pirpath", 
        help="Path to PIRANA-current/", default="~/PIRANA-current")
parser.add_option("-q", action="store_true", dest="quiet", default=False,
        help="Quiet mode (no interactive plots)")
parser.add_option("-s", dest="plotspec", 
        help="Plot spec file", default=None)
parser.add_option("-t", dest="otype", 
        help="Output plots to files of this type (eg pdf, eps, png, etc)", default=None)
parser.add_option("-v", action="store_true", dest="verbose", default=False,
        help="Verbose mode")

(opts, args) = parser.parse_args()

# Do not require X forwarding if in quiet mode.
if opts.quiet:
    import matplotlib
    matplotlib.use('Agg')

from numpy import *
from pylab import plot, errorbar, hist

opts.pirpath = os.path.expanduser(opts.pirpath)
# opts.quiet or print("Pirana path: "+opts.pirpath)
if not opts.quiet:
    print("Pirana path: "+opts.pirpath)

automationPath = opts.pirpath+'/'+myRelPath
plotterPath = automationPath+'/plotting/'

# Use this instead of import becuase import lacks flexibility with relative
# paths.
def load_mod(path):
    try:
        # pass globals since we need exefile to make changes to the global env,
        # not the function's env.
        execfile(path, globals())
    except:
        raise NameError("Can't load plotter module: "+path)

def get_modpath(basepath, optval, modname):
    if optval:
        return(os.path.expanduser(optval))
    else:
        return(os.path.expanduser(basepath+modname))

try:
    opts.plotspec = get_modpath(plotterPath, opts.plotspec, 'plot_spec.py');

    # This is needed because plot_utils is required by both the main script and
    # by plot_env, which executes in a private global env.  The ___ prefix is to
    # prevent collisions with the data column namespace.
    ___utilopts=opts
    ___utilopts.___utilpath=plotterPath+'plot_utils.py'

    load_mod(opts.plotspec)
    load_mod(___utilopts.___utilpath)
    load_mod(automationPath+'/lib/plot_common.py')
    
    opts.plot_env = get_modpath(plotterPath, opts.plot_env, 'plot_env.py');
except NameError as inst:
    print(str(inst.args[-1]));
    exit()

class gdp:
    xax = None
    ycol = None
    yerr = None
    yerr_ref = None
    indices = None

def get_arg(mylist, iter):
    return(min(len(mylist)-1, iter))

# plotmat
#   Class to easily plot 2D matrices.  This class allows one to develop plot
#   specification files which describe the desired plot output in a somewhat
#   declaritive format.  Multiple plot types are supported, see plot_lib.py.
class plotmat(plot_common):
    def __init__(self, myopts):
        if not myopts.fname:
            raise IOError('No input filename, see -h for options.')

        # ISO8601 compliant while ensuring compatibility with windows and unix
        # file naming constraints.  The standard options don't do the latter.
        self.args       = myopts

        if self.args.datestamp:
            self.dt     = '_' + time.strftime("%Y%m%dT%H%M%S") + '_'
        else:
            self.dt     = '_';
    
        self.gdp = gdp

        self.load_data(self.args.fname)

    def setupPglobals(self):
        # Set the global environment for the plot loop to the column space.
        plotgenv = self.coldata

        # Used by plot_utils.py
        plotgenv['___utilopts'] = self.args

        # To pass data back to parent environment
        plotgenv['___gdp'] = self.gdp

        # Additional plotter enviornment globals
        plotgenv['xax'] = None
        plotgenv['ycol'] = None
        plotgenv['yerr'] = None
        plotgenv['yerr_ref'] = None
        plotgenv['indices'] = None
        plotgenv['get_arg'] = get_arg
        plotgenv['iter'] = 0

        return(plotgenv)


    def plothelper(self, currplot, newax=None):
        plotgenv = self.setupPglobals()
        plotgenv['currplot'] = currplot

        if currplot.postproc:
            fid = open(self.args.oprefix+self.dt+currplot.__name__+'.txt', 'w')
            fid.write('\t'.join(self.colnames)+'\n')

        for y in currplot.ydata:
            # Execute the plotter for this plot spec in plotgenv.
            execfile(self.args.plot_env, plotgenv, {})
            xax = self.gdp.xax
            ycol = self.gdp.ycol
            yerr = self.gdp.yerr
            yerr_ref = self.gdp.yerr_ref
            indices = self.gdp.indices

            # XXX Work around matplotlib bug.  I think for some reason the tick location
            # state is not properly maintained in the pylab module.  Otherwise, twinx
            # seems to work.
            if currplot.y2cols:
                ax=pylab.gca()
                ax.yaxis.tick_right()

            fcn = eval(currplot.fcn)
            curropt = get_arg(currplot.options, plotgenv['iter'])

            # have to explicitly check errorbar to to inconsistencies in matplotlib
            # interface
            if (currplot.xcol is None and fcn != errorbar) or fcn == hist:
                # if no user xax or if hist or other such plot type
                eval('fcn(ycol, '+currplot.options[curropt]+')')
            else:
                eval('fcn(xax, ycol, '+yerr_ref+currplot.options[curropt]+')')
 
            if currplot.postproc:
                savetxt(fid, currplot.postproc(xax, self.data[indices, :]),
                        delimiter='\t')

            pylab.hold(True)
            plotgenv['iter'] += 1

        if currplot.postproc:
            fid.close()

        if currplot.ylabel is None:
            pylab.ylabel(currplot.ycols[0])
        else:
            pylab.ylabel(currplot.ylabel)

        if currplot.legend == []:
            pass
        elif currplot.legend is None:
            leg = pylab.legend(currplot.ydata, loc=currplot.legend_pos)
            leg.legendPatch.set_alpha(currplot.legend_alpha)
        else:
            leg = pylab.legend(currplot.legend, loc=currplot.legend_pos)
            leg.legendPatch.set_alpha(currplot.legend_alpha)

        if currplot.my_axis and not currplot.y2cols:
            pylab.axis(currplot.my_axis)
        else:
            currplot.my_axis = pylab.axis()

        if currplot.padding:
            # Increase each boundary 2.5% so plot lines don't touch the border.
            currAxis = pylab.axis()
            padding = 0.025
            xdel = (currAxis[1] - currAxis[0])*padding
            ydel = (currAxis[3] - currAxis[2])*padding
            currAxis = map(operator.add, currAxis, (-xdel, xdel, -ydel, ydel))
            pylab.axis(currAxis)                                                     
        pylab.hold(False)

        pylab.title(currplot.title)
        if currplot.xlabel is None:
            if currplot.xcol is None:
                pylab.xlabel("Default Axis")
            else:
                pylab.xlabel(currplot.xcol)
        else:
            pylab.xlabel(currplot.xlabel)

    def minmax(self, x, y, yerr, iter, axvector):
        assert sum(mat(yerr[0] + yerr[1]) >= 0)==size(yerr) or yerr==[0,0],\
        "Error bar offsets must be positive"

        if iter:
            axvector = [min(hstack((x, axvector[0]))),
            max(hstack((x, axvector[1]))),
            min(hstack((y-yerr[0], axvector[2]))),
            max(hstack((y+yerr[1], axvector[3])))]
        else:
            axvector = [min(x), max(x), min(y-yerr[0]), max(y+yerr[1])]

        return axvector

    def find_uniform_axes(self):
        if uniform_axes:
            for currset in uniform_axes:
                plotgenv = self.setupPglobals()
                gdp = plotgenv['___gdp']
                currax = None
                for currplot in currset:
                    plotgenv['iter'] = 0
                    axvector = None
                    for y in currplot.ydata:
                        plotgenv['currplot'] = currplot
                        execfile(self.args.plot_env, plotgenv, {})
                        axvector = self.minmax(gdp.xax, gdp.ycol, gdp.yerr,
                                               plotgenv['iter'], axvector)
                        if currax:
                            if axvector[0] < currax[0]:
                                currax[0] = axvector[0]
                            if axvector[1] > currax[1]:
                                currax[1] = axvector[1] 
                            if axvector[2] < currax[2]:
                                currax[2] = axvector[2]
                            if axvector[3] > currax[3]:
                                currax[3] = axvector[3]
                        else:
                            currax = axvector
            
                        plotgenv['iter'] += 1

                for currplot in currset:
                    currplot.my_axis = currax

    # doplot
    #   Iterates through the plot specification list, displays plots and writes
    #   plots to disk.
    def doplot(self):
        plotnum = 0
        outfiles = []
       
        # Instantiate each plot class.  This makes parent classes independent of
        # their children so that changes made during plotter execution to parent
        # classes (eg setting my_axis) do not get implicitly inherited by the
        # children.
        for idx in range(len(plot_spec)):
            __name__ = plot_spec[idx].__name__
            plot_spec[idx] = plot_spec[idx]()
            plot_spec[idx].__name__ = __name__

        self.find_uniform_axes()

        for currplot in plot_spec:
            if currplot.disable:
                continue

            # reset plot defaults
            pylab.rcdefaults()
            try:
                # add user rc params
                for k,v in currplot.rcparams.items():
                    pylab.rcParams[k]=v
            except Exception as msg:
                print msg
                keys = pylab.rcParams.keys()
                keys.sort()
                print keys
     
            if currplot.clone_axis:
                my_axis = eval(currplot.clone_axis+'.my_axis')
                if my_axis:
                    if currplot.my_axis:
                        print_fcn('Using user specified axis instead of clone_axis')
                    else:
                        currplot.my_axis = my_axis
                else:
                    print_fcn('Cannot clone axis '+currplot.clone_axis+
                              ', possible ordering violation')

            # Add the current plot to the private global environment.
            pylab.figure(figsize=currplot.imgsize)

            self.plothelper(currplot)
            if currplot.y2cols:
                currplot.ycols   = currplot.y2cols
                currplot.ylabel  = currplot.y2label
                # XXX need to fix to handle legend2 correctly
                currplot.legend = []#None

                if currplot.y2options:
                    currplot.options = currplot.y2options
                if currplot.y2data:
                    currplot.ydata = currplot.y2data
                newax = pylab.twinx()
                self.plothelper(currplot, newax)

            plotnum += 1

            if self.args.otype is not None:
                prename = self.args.oprefix+self.dt 
                oname = prename+currplot.__name__
                fullname = oname+'.'+self.args.otype.lower()
                print_fcn("Saving plot to: "+fullname)
                pylab.savefig(fullname)
                outfiles.append(fullname)

        if self.args.otype and self.args.otype.find('pdf', 0, 3) == 0:
            concatout = prename+'.pdf'
            cmd_str = 'pdftk '+' '.join(outfiles)+' output '+concatout
            if (os.system(cmd_str)):
                print('Warning: cannot concatenate PDF, check your pdftk installation')
            else:
                print_fcn('Saving concatenated pdf to: '+concatout)
                print_fcn('Removing intermediate PDF files')
                os.system('rm '+' '.join(outfiles))


        if plotnum and not self.args.quiet:
            pylab.show()

plotter = plotmat(opts)
plotter.doplot()
