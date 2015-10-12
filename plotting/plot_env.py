# Main data extraction loop.  Executes in a private global environment consisting of
# the column space.

from numpy import *
import types

execfile(___utilopts.___utilpath, globals())

# XXX: This is a hack to work around an apparent bug in python. ChrisK
# discovered that if we pass down anything other than globals() and locals() in
# the exec call, functions cannot call other functions from each other that are
# defined in this environment.  It turns out the functions end up in the local
# scope of the main code section for some reason, so this picks them out and
# stuffs them in globals.
for k, v in locals().items():
    if type(v) is types.FunctionType:
        globals()[k]=v

exec(currplot.aliases)

indices = nonzero(eval(currplot.ydata[iter]))

print_dbg("Indices: "+str(indices))
currycol = get_arg(currplot.ycols, iter)
ycol = eval(currplot.ycols[currycol])[indices]
yerr = [0, 0]
if currplot.yerrcols:
    curryerr = get_arg(currplot.yerrcols, iter)
    yerr_low = list(eval(currplot.yerrcols[curryerr][0])[indices])
    yerr_high = list(eval(currplot.yerrcols[curryerr][1])[indices])
    yerr = [yerr_low, yerr_high]
    yerr_ref = 'yerr, '
else:
    yerr_ref = ''

print_dbg("data column: "+str(currplot.ycols[currycol]))
curropt = get_arg(currplot.options, iter)

if currplot.xcol is None:
    xax = arange(0, size(indices))
else:
    xax = eval(currplot.xcol)[indices]

___gdp.xax = xax
___gdp.ycol = ycol
___gdp.yerr = yerr
___gdp.yerr_ref = yerr_ref
___gdp.indices = indices
