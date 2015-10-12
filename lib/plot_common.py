try:
    import numpy

    import pylab
except ImportError:
    print("pylab/numpy not installed, do:")
    print("   sudo apt-get install python-numpy python-scipy python-tk python-matplotlib")
    exit()

class plot_common:
    # load_data
    #   Loads a tab delimited matrix from a file.  The first line must consist
    #   of tab delimited column names to be mapped to column numbers.
    def load_data(self, fname):
        fh = open(fname, 'r')
        self.colnames = fh.readline().rstrip('\n')
        self.colnames = self.colnames.split('\t')
        fh.close()
        
        # Map column names to column numbers.
        self.colmap = dict(zip(self.colnames, range(len(self.colnames))))

        self.data = numpy.loadtxt(fname, skiprows=1, comments='#')
        # Bind column names to column data.
        self.coldata = dict(zip(self.colnames, self.data.T))


