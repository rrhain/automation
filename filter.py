#!/usr/bin/python

import os

#from optparse import OptionParser
import optparse

myRelPath="pirana-opnet/automation/"

class OptionParser (optparse.OptionParser):
    def check_required (self, opt):
        option = self.get_option(opt)
        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("Required %s option not supplied" % option)

parser = OptionParser()
parser.add_option("-b", dest="black", 
        help="Blacklist tokens (prioritized over whitelist)", default=None)
parser.add_option("-f", dest="fname", 
        help="2D matrix input file name", default=None)
parser.add_option("-o", dest="oname", 
        help="2D filtered matrix output file name", default=None)
parser.add_option("-p", dest="pirpath", 
        help="Path to PIRANA-current/", default="~/PIRANA-current")
parser.add_option("-w", dest="white", 
        help="Whitelist tokens", default=None)

(opts, args) = parser.parse_args()

required_opts=['-f', '-o']
for opt in required_opts:
    parser.check_required(opt)

opts.pirpath = os.path.expanduser(opts.pirpath)
print("Pirana path: "+opts.pirpath)
automationPath = opts.pirpath+'/'+myRelPath
execfile(automationPath+'/lib/plot_common.py', globals())

class filtermat(plot_common):
    def __init__(self, myopts):
        if not myopts.black and not myopts.white:
            raise IOError(
                'One or both of -b and -w options required (see -h for help)')

        self.args = myopts

        self.black = self.readlist(self.args.black)
        self.white = self.readlist(self.args.white)

        try:
            self.load_data(self.args.fname)
        except TypeError:
            print('Failed to load input file (see -f option)')
            exit()

        if len(self.white) == 0:
            self.white = frozenset(self.colnames)

    def readlist(self, fname):
        try:
            with open(fname, 'r') as f:
                data = f.readlines()
        except:
            return(set([]))
        
        return(frozenset(map(lambda x: x.rstrip('\n\t '), data)))

    def cullmat(self):
        outtoks=list(self.white - self.black)
        outtoks.sort(key=str.lower)
        outcols=[]
        for tok in outtoks:
            try:
                outcols.append(self.colmap[tok]+1)
            except KeyError as inst:
                print("WARNING: "+str(inst.args[-1])+
                      " is not a valid token, skipping...")

        if not outcols:
            print("WARNING: Output is an empty matrix, exiting...")
            exit()
        
        # Do this using unix cut to preserve exactly all attributes of the
        # original column formats.  numpy.savetxt will result in slightly
        # different column formatting, and python doesn't seem to have a native
        # cut utility to act on files and I don't feel like cooking one up.
        cmd = 'cut -f'+','.join(map(str, outcols))+' '+self.args.fname+'>'+self.args.oname
        print("Executing: "+cmd)
        os.system(cmd)

myfilter = filtermat(opts)
myfilter.cullmat()
