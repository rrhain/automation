import sys

def print_fcn(mystr, *args):
    if ___utilopts.quiet:
        pass
    else:
        sys.stdout.write(mystr+'\n', *args)
 
def print_dbg(mystr, *args):
    if ___utilopts.debug:
        sys.stdout.write("DBG: "+mystr+'\n', *args)
    else:
        pass
