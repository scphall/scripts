#!/usr/bin/python

###############################################################################

"""
    Filtering function,
        to use instead of hadd.

    Written in python rather than its C++
    counterpart for ease and flexibility at the sacrifice of speed.

    NB: Always run as 'python filter.py'.

"""

__title__  = "filter.py"
__author__ = "Sam Hall"
__email__  = "shall@cern.ch"

###############################################################################

# Imports.
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import sys
from optparse import OptionParser
from array    import array
from messages import Messages

# Global configuration cuts.
msg = Messages([__title__, __author__, __email__])
#msg.set_debug()
config = {
    #'lab0_IPCHI2_OWNPV'     :   'max25',
    #'lab0_DIRA_OWNPV'       :   'min0.999'
}


# Functions.
def opts():
    """Get options from options parser and manage them."""
    global msg
    err = False
    # Check Environment first.
    parser = OptionParser('usage: %prog [options] [args]')
    parser.add_option( '-f', '--file', dest='fileName',
                        help='Input filename.')
    parser.add_option( '-t', '--tree', dest='treeName',
                        default='',
                        help='Input tree name.')
    parser.add_option( '-j', '--job', dest='job',
                        default=None,
                        help='Input job number.')
    parser.add_option( '-s', '--suffix', dest='suffix',
                        default='',
                        help='Suffix of new file.')
    options, args = parser.parse_args()
    if options.job is None:
        msg.error('No job number given, set with "-j".')
        err = True
    if not err:
        if options.job is not None:
            options.job = int(options.job)
    if err:
        msg.error('INPUT ERROR.-')
        msg.error(' Consult "-h" for help')
    if not 'DAVINCIROOT' in os.environ:
        msg.error('ENVIRONMENT ERROR.-')
        msg.error(' Please SetupProject DaVinci')
        err = True
    msg.debug('End of options.')
    sys.argv = []
    return options, args, err


def set_addresses(tree):
    """Set addresses using config dictionary of cuts.  The returned dictionary
    contains all branch addresses in python arrays.

    """
    global config
    bAdds = {}
    for key in config:
        bAdds.update({key : array('d',[0])})
        tree.SetBranchAddress(key, bAdds[key])
    return bAdds


def get_root_file(path):
    """Find the name of the root file in the gangadir."""
    root = []
    for d in range(10):
        root = os.listdir('%s/%d/output/'%(path, d))
        root = [x for x in root if x.endswith('.root')]
        if len(root) == 1:
            break
    root = root[0]
    msg.info('Root file found is called: %s'%(root.split('/')[-1]))
    return root, d


def get_chains(jobNo, trees):
    """Get TChain array from all root files from gangadir jobNo."""
    # Must be here otherwise there are conflictions with opts parser.
    import ROOT as r
    global msg
    chains = []
    path  = '%s/%d'%(os.getenv('GANGAJOBPATH'), jobNo)
    msg.info('Path to job directory is:-')
    msg.info(' %s'%path)
    dirs  = os.listdir(path)
    dirs  = [x for x in dirs if x.isdigit()]
    root, d = get_root_file(path)
    #
    exFile = ROOT.TFile('%s/%s/output/%s'%(path, d, root))
    treeList = exFile.GetListOfKeys()
    gil = 'GetIntegratedLuminosity'
    treeNames = [x.GetName() for x in treeList if x.GetName() != gil]
    exFile.Close()
    exFile.Delete()

    if len(treeNames) < 1:
        msg.error('No trees found (excluding GetIntegratedLuminosity).')
        return chains
    else:
        treeNames = ['%s/DecayTree'%x for x in treeNames]
        #treeNames += ['%s/MCDecayTree'%x for x in treeNames]
    #
    for dirn in dirs:
        f = '%s/%s/output/%s'%(path, dirn, root)
        if not os.path.exists(f):
            msg.info('Root file for subjob %s does not exist, ignoring.'%dirn)
    if trees != '':
        #treeNames = [x for x in treeNames if trees.count(x) > 0]
        treeNames = [trees]

    msg.info('Tree names are:-')
    for treeName in treeNames:
        msg.info(' %s-'%treeName)
    msg.raw('')

    for treeName in treeNames:
        chain = ROOT.TChain(treeName)
        for dirn in dirs:
            f = '%s/%s/output/%s'%(path, dirn, root)
            if os.path.exists(f):
                chain.Add(f)
        chain.GetEntry(0)
        chains.append(chain)
    msg.info('All chains built.')
    return chains


def main_multiple(options):
    """Main function, master of sctipt.
    Also summoned from __name__=="__main__".

    """
    # Must be here otherwise there are conflictions with opts parser.
    global config
    global msg
    msg.debug('Start of main_multiple, before ROOT import')
    msg.debug('Start of main_multiple, after ROOT import')
    chains = get_chains(options.job, options.treeName)
    path = os.getenv('ROOTFILEPATH')
    for chain in chains:
        fname = '%s/%s%s.root'%(path, chain.GetName().split('/')[0],
                                                            options.suffix)
        msg.info('Outputting %s to %s.'%(chain.GetName(), fname))
        if os.path.exists(fname):
            msg.error('The above file exists, skipping this chain.')
            continue
        outFile = ROOT.TFile(fname, 'recreate')
        tree = chain.GetTree().CloneTree(0)
        dataIn  = set_addresses(chain)
        dataOut = set_addresses(tree)
        msg.info('Chain copied and addresses set.-')
        msg.info(' Please wait while initialization takes place.')
        nentries = chain.GetEntries()
        chain.GetEntry(0)

        for entry in xrange(nentries):
            chain.GetEntry(entry)
            if(entry % 100000 == 0):
                msg.info('Done %d out of %d entries.-'%(entry,nentries))
            fill = True
            for key in config:
                if config[key].find('min') >= 0:
                    if dataIn[key][0] < float(config[key].replace('min','')):
                        fill = False
                elif dataIn[key][0] > float(config[key].replace('max','')):
                    fill = False
            if fill:
                tree.Fill()
        msg.raw('')
        outFile.cd()
        tree.Write()
        outFile.Close()
        msg.info('Finished writing to %s'%fname)
        msg.raw('')
    msg.foot()
    return 0


if __name__ == "__main__":
    options, args, err = opts()
    if err:
        msg.error('ERROR - EXIT.-')
        msg.foot()
    else:
        main_multiple(options)

