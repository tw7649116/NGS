#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import division, with_statement
'''
Copyright 2013, 陈同 (chentong_biology@163.com).  
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
desc = '''
Functional description:
    This is designed to do AS analysis using rMATS.

Samplefile:

    Samp    conditions
    SC_1    SC
    SC_2    SC
    SC_3    SC
    SC_11bA.SS_1    SC_11bA.SS
    SC_11bA.SS_2    SC_11bA.SS
    SC_can.SS_1 SC_can.SS
    SC_can.SS_2 SC_can.SS

compare_pair:
    SC_11bA.SS  SC
    SC_can.SS   SC
    SC_11bA.SS  SC_can.SS
'''

import sys
import os
from json import dumps as json_dumps
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
#from multiprocessing.dummy import Pool as ThreadPool

debug = 0

def fprint(content):
    print json_dumps(content,indent=1)

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "%prog -i file"
    parser = OP(usage=usages)
    parser.add_option("-i", "--input-file", dest="filein",
        metavar="FILEIN", help="sampleFile")
    parser.add_option("-c", "--compare_pair", dest="compare_pair",
        metavar="COMPARE_PAIR", help="compare_pair")
    parser.add_option("-l", "--reads-length", dest="read_len",
        help="The length of reads.")
    parser.add_option("-g", "--gtf-file", dest="gtf",
        help="GTF file.")
    parser.add_option("-F", "--force-rerun", dest="force",
        default=0, help="Force rerun evenif output directory exists. \
Default <0> meaning skip existing directory. \
Accept <1> to force running.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-d", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------


def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    file = options.filein
    compare = options.compare_pair
    read_len = options.read_len
    gtf = options.gtf
    force = int(options.force)
    verbose = options.verbose
    global debug
    debug = options.debug
    #-----------------------------------
    if file == '-':
        fh = sys.stdin
    else:
        fh = open(file)
    #--------------------------------
    sampleD = {}
    header = 1
    for line in fh:
        if header:
            header -= 1
            continue
        #------------------
        rep, samp = line.split()[:2]
        if samp not in sampleD:
            sampleD[samp] = []
        sampleD[samp].append(rep)
    #-------------END reading file----------
    #----close file handle for files-----
    if file != '-':
        fh.close()
    #-----------end close fh-----------
    for line in open(compare):
        samp1, samp2 = line.split()
        bam1 = ','.join([rep+"/accepted_hits.bam" for rep in sampleD[samp1]])
        bam2 = ','.join([rep+"/accepted_hits.bam" for rep in sampleD[samp2]])
        output = "%s_vs_%s" % (samp1, samp2)
        #read_len = "-len %s" % options.read_len
        #gtf = "-gtf %s" % options.gtf
        cmd = ["python /MPATHB/soft/rMATS.3.0.9/RNASeq-MATS.py -b1", 
                bam1, "-b2", bam2, "-o", output, "-t paired", "-len", 
                read_len, '-gtf', gtf, '&&', "pythonmail3.py -s",
                output, '&']
        #print ' '.join(cmd)
        if (not force) and os.path.exists(output):
            print >>sys.stderr, "%s alreay exists. Skipping......" % output
        else:
            if debug:
                print >>sys.stderr,  ' '.join(cmd)
            else:
                os.system(' '.join(cmd))

    ###--------multi-process------------------
    #pool = ThreadPool(5) # 5 represents thread_num
    #result = pool.map(func, iterable_object)
    #pool.close()
    #pool.join()
    ###--------multi-process------------------
    if verbose:
        print >>sys.stderr,\
            "--Successful %s" % strftime(timeformat, localtime())

if __name__ == '__main__':
    startTime = strftime(timeformat, localtime())
    main()
    endTime = strftime(timeformat, localtime())
    fh = open('python.log', 'a')
    print >>fh, "%s\n\tRun time : %s - %s " % \
        (' '.join(sys.argv), startTime, endTime)
    fh.close()
    ###---------profile the program---------
    #import profile
    #profile_output = sys.argv[0]+".prof.txt")
    #profile.run("main()", profile_output)
    #import pstats
    #p = pstats.Stats(profile_output)
    #p.sort_stats("time").print_stats()
    ###---------profile the program---------


