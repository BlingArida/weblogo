#!/usr/bin/env python

"""
WebLogo, an application for generating sequence logos, graphical representations of sequence conservation within amino acid or nucleic acid multiple sequence alignments. WebLogo makes extensive use of the CoreBio python toolkit for computational biology.. 

WebLogo: http://code.google.com/p/weblogo/
CoreBio: http://code.google.com/p/corebio/
"""

import sys

from distutils.core import setup
from distutils.core import Extension
from distutils.command.build import build
from distutils.command.install_data import install_data


# check dependancies
if not hasattr(sys, 'version_info') or sys.version_info < (2,3,0,'final'):
    raise SystemExit,  \
        "Dependancy error: WebLogo requires Python 2.3 or later."
 

from weblogo import __version__


def main() :           
    setup(
        name         = "weblogo",
        version          =  __version__,
        description      = "Sequence Logos Redrawn",
        long_description  = __doc__,
        maintainer       = "Gavin Crooks",
        maintainer_email = "gec@threeplusone.com",
        url              = "http://code.google.com/p/weblogo/",    
        download_url     = 'http://corebio.googlecode.com/svn/dist/weblogo-%s.tar.gz' % __version__ ,
        classifiers      =[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Programming Language :: Python',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        
        scripts = [
            'weblogo.py', 
            ],
        
        packages  = [ 
            'weblogo'
            ],
            
        data_files = ['weblogo/weblogo_htdocs/*.*',],
        
        cmdclass= {"install_data" : _install_data},        
    )







# Python 2.3 compatability 
# Rework the install_data command to act like the package_data distutils
# command included with python 2.4.
# Adapted from biopython, which was adapted from mxtexttools
class _install_data(install_data):
    def finalize_options(self):
        if self.install_dir is None:
            installobj = self.distribution.get_command_obj('install')
            # Use install_lib rather than install_platlib because we are
            # currently a pure python distribution (No c extensions.)
            self.install_dir = installobj.install_lib 
            #print installobj.install_lib 
        install_data.finalize_options(self)

    def run (self):
        import glob
        import os
        if not self.dry_run:
            self.mkpath(self.install_dir)
        data_files = self.get_inputs()
        for entry in data_files:
            if type(entry) is not type(""):
                raise ValueError("data_files must be strings")
            # Unix- to platform-convention conversion
            entry = os.sep.join(entry.split("/"))
            filenames = glob.glob(entry)
            for filename in filenames:
                dst = os.path.join(self.install_dir, filename)
                dstdir = os.path.split(dst)[0]
                if not self.dry_run:
                    self.mkpath(dstdir)
                    outfile = self.copy_file(filename, dst)[0]
                else:
                    outfile = dst
                self.outfiles.append(outfile)
  
if __name__ == '__main__' :
    main()
    
 