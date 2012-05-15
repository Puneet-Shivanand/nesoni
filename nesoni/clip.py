
"""

Clip based on quality and presence of adaptor sequence

"""

import sys, os, itertools, collections

from nesoni import grace, io, bio

ADAPTORS = """
#2011-01-11 Illumina adapter sequences

TruSeq-Adapter Universal AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
TruSeq-Adapter Index 1 GATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 2 GATCGGAAGAGCACACGTCTGAACTCCAGTCACCGATGTATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 3 GATCGGAAGAGCACACGTCTGAACTCCAGTCACTTAGGCATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 4 GATCGGAAGAGCACACGTCTGAACTCCAGTCACTGACCAATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 5 GATCGGAAGAGCACACGTCTGAACTCCAGTCACACAGTGATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 6 GATCGGAAGAGCACACGTCTGAACTCCAGTCACGCCAATATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 7 GATCGGAAGAGCACACGTCTGAACTCCAGTCACCAGATCATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 8 GATCGGAAGAGCACACGTCTGAACTCCAGTCACACTTGAATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 9 GATCGGAAGAGCACACGTCTGAACTCCAGTCACGATCAGATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 10 GATCGGAAGAGCACACGTCTGAACTCCAGTCACTAGCTTATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 11 GATCGGAAGAGCACACGTCTGAACTCCAGTCACGGCTACATCTCGTATGCCGTCTTCTGCTTG
TruSeq-Adapter Index 12 GATCGGAAGAGCACACGTCTGAACTCCAGTCACCTTGTAATCTCGTATGCCGTCTTCTGCTTG

#Oligonucleotide sequences for TruSeq Small RNA Sample Prep Kits
TruSeq-sRNA RNA 5' Adapter (RA5), part # 15013205 GUUCAGAGUUCUACAGUCCGACGAUC
TruSeq-sRNA RNA 3' Adapter (RA3), part # 15013207 TGGAATTCTCGGGTGCCAAGG
TruSeq-sRNA RNA RT Primer (RTP), part # 15013981 GCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer (RP1), part # 15005505 AATGATACGGCGACCACCGAGATCTACACGTTCAGAGTTCTACAGTCCGA
TruSeq-sRNA RNA PCR Primer, Index 1 (RPI1) CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 2 (RPI2) CAAGCAGAAGACGGCATACGAGATACATCGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 3 (RPI3) CAAGCAGAAGACGGCATACGAGATGCCTAAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 4 (RPI4) CAAGCAGAAGACGGCATACGAGATTGGTCAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 5 (RPI5) CAAGCAGAAGACGGCATACGAGATCACTGTGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 6 (RPI6) CAAGCAGAAGACGGCATACGAGATATTGGCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 7 (RPI7) CAAGCAGAAGACGGCATACGAGATGATCTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 8 (RPI8) CAAGCAGAAGACGGCATACGAGATTCAAGTGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 9 (RPI9) CAAGCAGAAGACGGCATACGAGATCTGATCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 10 (RPI10) CAAGCAGAAGACGGCATACGAGATAAGCTAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 11 (RPI11) CAAGCAGAAGACGGCATACGAGATGTAGCCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 12 (RPI12) CAAGCAGAAGACGGCATACGAGATTACAAGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 13 (RPI13) CAAGCAGAAGACGGCATACGAGATTTGACTGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 14 (RPI14) CAAGCAGAAGACGGCATACGAGATGGAACTGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 15 (RPI15) CAAGCAGAAGACGGCATACGAGATTGACATGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 16 (RPI16) CAAGCAGAAGACGGCATACGAGATGGACGGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 17 (RPI17) CAAGCAGAAGACGGCATACGAGATCTCTACGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 18 (RPI18) CAAGCAGAAGACGGCATACGAGATGCGGACGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 19 (RPI19) CAAGCAGAAGACGGCATACGAGATTTTCACGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 20 (RPI20) CAAGCAGAAGACGGCATACGAGATGGCCACGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 21 (RPI21) CAAGCAGAAGACGGCATACGAGATCGAAACGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 22 (RPI22) CAAGCAGAAGACGGCATACGAGATCGTACGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 23 (RPI23) CAAGCAGAAGACGGCATACGAGATCCACTCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 24 (RPI24) CAAGCAGAAGACGGCATACGAGATGCTACCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 25 (RPI25) CAAGCAGAAGACGGCATACGAGATATCAGTGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 26 (RPI26) CAAGCAGAAGACGGCATACGAGATGCTCATGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 27 (RPI27) CAAGCAGAAGACGGCATACGAGATAGGAATGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 28 (RPI28) CAAGCAGAAGACGGCATACGAGATCTTTTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 29 (RPI29) CAAGCAGAAGACGGCATACGAGATTAGTTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 30 (RPI30) CAAGCAGAAGACGGCATACGAGATCCGGTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 31 (RPI31) CAAGCAGAAGACGGCATACGAGATATCGTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 32 (RPI32) CAAGCAGAAGACGGCATACGAGATTGAGTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 33 (RPI33) CAAGCAGAAGACGGCATACGAGATCGCCTGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 34 (RPI34) CAAGCAGAAGACGGCATACGAGATGCCATGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 35 (RPI35) CAAGCAGAAGACGGCATACGAGATAAAATGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 36 (RPI36) CAAGCAGAAGACGGCATACGAGATTGTTGGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 37 (RPI37) CAAGCAGAAGACGGCATACGAGATATTCCGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 38 (RPI38) CAAGCAGAAGACGGCATACGAGATAGCTAGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 39 (RPI39) CAAGCAGAAGACGGCATACGAGATGTATAGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 40 (RPI40) CAAGCAGAAGACGGCATACGAGATTCTGAGGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 41 (RPI41) CAAGCAGAAGACGGCATACGAGATGTCGTCGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 42 (RPI42) CAAGCAGAAGACGGCATACGAGATCGATTAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 43 (RPI43) CAAGCAGAAGACGGCATACGAGATGCTGTAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 44 (RPI44) CAAGCAGAAGACGGCATACGAGATATTATAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 45 (RPI45) CAAGCAGAAGACGGCATACGAGATGAATGAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 46 (RPI46) CAAGCAGAAGACGGCATACGAGATTCGGGAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 47 (RPI47) CAAGCAGAAGACGGCATACGAGATCTTCGAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA
TruSeq-sRNA RNA PCR Primer, Index 48 (RPI48) CAAGCAGAAGACGGCATACGAGATTGCCGAGTGACTGGAGTTCCTTGGCACCCGAGAATTCCA

Genomic DNA Adapter GATCGGAAGAGCTCGTATGCCGTCTTCTGCTTG
Genomic DNA Adapter ACACTCTTTCCCTACACGACGCTCTTCCGATCT
Genomic DNA PCR Primer AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
Genomic DNA PCR Primer CAAGCAGAAGACGGCATACGAGCTCTTCCGATCT
Genomic DNA Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT

PE Adapter GATCGGAAGAGCGGTTCAGCAGGAATGCCGAG
PE Adapter ACACTCTTTCCCTACACGACGCTCTTCCGATCT
PE PCR Primer 1.0 AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
PE PCR Primer 2.0 CAAGCAGAAGACGGCATACGAGATCGGTCTCGGCATTCCTGCTGAACCGCTCTTCCGATCT
PE Read 1 Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT
PE Read 2 Sequencing Primer CGGTCTCGGCATTCCTGCTGAACCGCTCTTCCGATCT

Multiplexing Adapter GATCGGAAGAGCACACGTCT
Multiplexing Adapter ACACTCTTTCCCTACACGACGCTCTTCCGATCT
Multiplexing PCR Primer 1.0 AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
Multiplexing PCR Primer 2.0 GTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT
Multiplexing Read 1 Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT
Multiplexing Index Read Sequencing Primer GATCGGAAGAGCACACGTCTGAACTCCAGTCAC
Multiplexing Read 2 Sequencing Primer GTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT
Multiplexing PCR Primer, Index 1 CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTC
Multiplexing PCR Primer, Index 2 CAAGCAGAAGACGGCATACGAGATACATCGGTGACTGGAGTTC
Multiplexing PCR Primer, Index 3 CAAGCAGAAGACGGCATACGAGATGCCTAAGTGACTGGAGTTC
Multiplexing PCR Primer, Index 4 CAAGCAGAAGACGGCATACGAGATTGGTCAGTGACTGGAGTTC
Multiplexing PCR Primer, Index 5 CAAGCAGAAGACGGCATACGAGATCACTGTGTGACTGGAGTTC
Multiplexing PCR Primer, Index 6 CAAGCAGAAGACGGCATACGAGATATTGGCGTGACTGGAGTTC
Multiplexing PCR Primer, Index 7 CAAGCAGAAGACGGCATACGAGATGATCTGGTGACTGGAGTTC
Multiplexing PCR Primer, Index 8 CAAGCAGAAGACGGCATACGAGATTCAAGTGTGACTGGAGTTC
Multiplexing PCR Primer, Index 9 CAAGCAGAAGACGGCATACGAGATCTGATCGTGACTGGAGTTC
Multiplexing PCR Primer, Index 10 CAAGCAGAAGACGGCATACGAGATAAGCTAGTGACTGGAGTTC
Multiplexing PCR Primer, Index 11 CAAGCAGAAGACGGCATACGAGATGTAGCCGTGACTGGAGTTC
Multiplexing PCR Primer, Index 12 CAAGCAGAAGACGGCATACGAGATTACAAGGTGACTGGAGTTC

sRNA RT Primer CAAGCAGAAGACGGCATACGA
sRNA 5' RNA Adapter GUUCAGAGUUCUACAGUCCGACGAUC
sRNA 3' RNA Adapter P-UCGUAUGCCGUCUUCUGCUUGUidT
sRNA v1.5 Small RNA 3' Adapter ATCTCGTATGCCGTCTTCTGCTTG
sRNA PCR Primer 1 CAAGCAGAAGACGGCATACGA
sRNA PCR Primer 2 AATGATACGGCGACCACCGACAGGTTCAGAGTTCTACAGTCCGA
sRNA Sequencing Primer CGACAGGTTCAGAGTTCTACAGTCCGACGATC

#Older sequences
#Genomic Adapter1 a GATCGGAAGAGCTCGTATGCCGTCTTCTGCTTG
#Genomic Adapter1 b ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Genomic PCR Primer1 a AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Genomic PCR Primer1 b CAAGCAGAAGACGGCATACGAGCTCTTCCGATCT
#Genomic DNA Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Multiplexing DNA oligonucleotide sequences
#Multiplexing Adapter1 a GATCGGAAGAGCACACGTCT
#Multiplexing Adapter1 b ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Multiplexing PCR Primer 1.01 AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Multiplexing PCR Primer 2.01 GTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT
#Multiplexing Read 1 Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#Multiplexing Index Read Sequencing Primer GATCGGAAGAGCACACGTCTGAACTCCAGTCAC
#Multiplexing Read 2 Sequencing Primer GTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT
#Multiplexing PCR Primer Index 1 CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTC
#Multiplexing PCR Primer Index 2 CAAGCAGAAGACGGCATACGAGATACATCGGTGACTGGAGTTC
#Multiplexing PCR Primer Index 3 CAAGCAGAAGACGGCATACGAGATGCCTAAGTGACTGGAGTTC
#Multiplexing PCR Primer Index 4 CAAGCAGAAGACGGCATACGAGATTGGTCAGTGACTGGAGTTC
#Multiplexing PCR Primer Index 5 CAAGCAGAAGACGGCATACGAGATCACTGTGTGACTGGAGTTC
#Multiplexing PCR Primer Index 6 CAAGCAGAAGACGGCATACGAGATATTGGCGTGACTGGAGTTC
#Multiplexing PCR Primer Index 7 CAAGCAGAAGACGGCATACGAGATGATCTGGTGACTGGAGTTC
#Multiplexing PCR Primer Index 8 CAAGCAGAAGACGGCATACGAGATTCAAGTGTGACTGGAGTTC
#Multiplexing PCR Primer Index 9 CAAGCAGAAGACGGCATACGAGATCTGATCGTGACTGGAGTTC
#Multiplexing PCR Primer Index 10 CAAGCAGAAGACGGCATACGAGATAAGCTAGTGACTGGAGTTC
#Multiplexing PCR Primer Index 11 CAAGCAGAAGACGGCATACGAGATGTAGCCGTGACTGGAGTTC
#Multiplexing PCR Primer Index 12 CAAGCAGAAGACGGCATACGAGATTACAAGGTGACTGGAGTTC
#PE Adapter1 a GATCGGAAGAGCGGTTCAGCAGGAATGCCGAG
#PE Adapter1 b ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#PE PCR Primer 1.01 AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT
#PE PCR Primer 2.01 CAAGCAGAAGACGGCATACGAGATCGGTCTCGGCATTCCTGCTGAACCGCTCTTCCGATCT
#PE Read 1 Sequencing Primer ACACTCTTTCCCTACACGACGCTCTTCCGATCT
#PE Read 2 Sequencing Primer CGGTCTCGGCATTCCTGCTGAACCGCTCTTCCGATCT
DpnII Gex Adapter 1 a GATCGTCGGACTGTAGAACTCTGAAC
DpnII Gex Adapter 1 b ACAGGTTCAGAGTTCTACAGTCCGAC
DpnII Gex Adapter 2 a CAAGCAGAAGACGGCATACGANN
DpnII Gex Adapter 2 b TCGTATGCCGTCTTCTGCTTG
DpnII Gex PCR Primer 1 CAAGCAGAAGACGGCATACGA
DpnII Gex PCR Primer 2 AATGATACGGCGACCACCGACAGGTTCAGAGTTCTACAGTCCGA
DpnII Gex Sequencing Primer CGACAGGTTCAGAGTTCTACAGTCCGACGATC
NlaIII Gex Adapter 1 a TCGGACTGTAGAACTCTGAAC
NlaIII Gex Adapter 1 b ACAGGTTCAGAGTTCTACAGTCCGACATG
NlaIII Gex Adapter 2 a CAAGCAGAAGACGGCATACGANN
NlaIII Gex Adapter 2 b TCGTATGCCGTCTTCTGCTTG
NlaIII Gex PCR Primer 1 CAAGCAGAAGACGGCATACGA
NlaIII Gex PCR Primer 2 AATGATACGGCGACCACCGACAGGTTCAGAGTTCTACAGTCCGA
NlaIII Gex Sequencing Primer CCGACAGGTTCAGAGTTCTACAGTCCGACATG
#sRNA RT Primer CAAGCAGAAGACGGCATACGA
#sRNA RNA Adapter a GUUCAGAGUUCUACAGUCCGACGAUC
#sRNA RNA Adapter b UCGUAUGCCGUCUUCUGCUUGUT
#sRNA PCR Primer 1 CAAGCAGAAGACGGCATACGA
#sRNA PCR Primer 2 AATGATACGGCGACCACCGACAGGTTCAGAGTTCTACAGTCCGA
#sRNA Sequencing Primer CGACAGGTTCAGAGTTCTACAGTCCGACGATC

"""


class Matcher(object):
    def __init__(self, seqs, names, max_error):
        self.max_error = max_error        
        self.names = names

        self.transitions = {'A':[], 'C':[], 'G':[], 'T':[] } # base -> id -> (new state id, emission)

        state_ids = { }

        def advance( state, base ):
            """ returns ( [new_state], [emit] ) """
        
            seq_no, pos, errors = state
            
            if seqs[seq_no][pos] != 'N' and seqs[seq_no][pos] != base:
                errors += 1
            
            if errors > max_error:
                return ( [], [] )
            
            pos += 1
            if pos == len(seqs[seq_no]):
                return ( [], [ (errors, seq_no) ] )
            else:
                return ( [ (seq_no, pos, errors) ], [] )


        todo = [ ]        
        def get_id(state):
            state = tuple(sorted(state))
            if state not in state_ids:
                state_ids[state] = len(state_ids)
                for base in 'ACGT':
                    self.transitions[base].append( None )
                todo.append(state)
            return state_ids[state]

        initial = [ ]
        for i in xrange(len(seqs)):
            for j in xrange(len(seqs[i])):
                initial.append( (i,j,0) )
        initial = tuple(sorted(initial))
        
        self.initial_id = get_id(initial)

        while todo:
            from_state = todo.pop(-1)
            from_id = get_id(from_state)
            
            for base in 'ACGT':
                 new_state = [ ]
                 emit = [ ]
                 for sub_state in from_state:
                     sub_new, sub_emit = advance(sub_state, base)
                     new_state.extend(sub_new)
                     emit.extend(sub_emit)
                 new_id = get_id(new_state)
                 self.transitions[ base ][ from_id ] = (new_id, sorted(emit))
    
    def match(self, seq):
        state = self.initial_id
        
        emit = None
        for i, base in enumerate(seq):        
            state, this_emit = self.transitions[ base ][ state ]
            if this_emit:
                emit = (i+1, this_emit)
        return emit


CLIP_HELP = """

Clip adaptors and low quality bases from Illumina reads or read pairs.

Usage:

    nesoni clip: [options] output_prefix \\
        [reads: single.fq[.gz]] \\
        [pairs: left.fq[.gz] right.fq[.gz]] \\
        [interleaved: interleaved.fq[.gz]]

Options:
  
  --adaptors         - Which adaptors to use.
                       Comma seperated list from:
                          truseq-adapter,truseq-srna,genomic,multiplexing,pe,srna,dpnii,nlaiii
                       or "none".
                       Default: truseq-adapter,truseq-srna,genomic,multiplexing,pe,srna
  
  --match NNN        - Minimum length adaptor match
                       Default: 10
                       
  --max-errors N     - Maximum errors in adaptor match
                       Note: slow for N > 1
                       Default: 1
  
  --clip-ambiguous yes/no - Clip ambiguous bases, eg N
                       Default: yes
  
  --quality NNN      - Quality cutoff
                       Default: 10
  
  --qoffset NNN      - Quality character offset
                       sanger: 33, solexa: 59, illumina: 64
                       Default: guess
  
  --length NNN       - Reads shorter than this will be discarded
                       Default: 24
  
  --homopolymers yes/no - Disallow reads containing all the same base
                       Default: no (i.e. homopolymers allowed) 
  
  --trim-start NNN   - Trim NNN bases from start of each read
                       irrespective of quality.
                       Default: 0
                       
  --trim-end NNN     - Trim NNN bases from end of each read
                       irrespective of quality.
                       Default: 0

  --revcom yes/no    - Reverse complement all reads
                       ie convert opp-out pairs to opp-in
                       Default: no

  --fasta yes/no     - Output in fasta rather than fastq format
                       Default: no

  --gzip yes/no      - Gzip output
                       Default: yes
  
  --rejects yes/no   - Output rejected reads in separate file
                       Default: no 

"""

def deinterleave(iterator):
    for item1 in iterator:
        item2 = iterator.next()
        yield (item1, item2)

def clip(args):
    log = grace.Log()
    
    quality_cutoff, args = grace.get_option_value(args, '--quality', int, 10)
    qoffset, args = grace.get_option_value(args, '--qoffset', int, None)
    clip_ambiguous, args = grace.get_option_value(args, '--clip-ambiguous', grace.as_bool, True)
    length_cutoff, args = grace.get_option_value(args, '--length', int, 24)
    adaptor_cutoff, args = grace.get_option_value(args, '--match', int, 10)
    max_error, args = grace.get_option_value(args, '--max-errors', int, 1)
    adaptor_set, args = grace.get_option_value(args, '--adaptors', str, 'truseq-adapter,truseq-srna,genomic,multiplexing,pe,srna')
    disallow_homopolymers, args = grace.get_option_value(args, '--homopolymers', grace.as_bool, False)
    reverse_complement, args = grace.get_option_value(args, '--revcom', grace.as_bool, False)
    trim_start, args = grace.get_option_value(args, '--trim-start', int, 0)
    trim_end, args = grace.get_option_value(args, '--trim-end', int, 0)
    output_fasta, args = grace.get_option_value(args, '--fasta', grace.as_bool, False)
    use_gzip, args = grace.get_option_value(args, '--gzip', grace.as_bool, True)
    output_rejects, args = grace.get_option_value(args, '--rejects', grace.as_bool, False)
    grace.expect_no_further_options(args)

    if len(args) < 1:
        print >> sys.stderr, CLIP_HELP
        raise grace.Help_shown()
    
    prefix = args[0]
    args = args[1:]

    iterators = [ ]
    any_paired = [ False ]
    
    filenames = [ ]

    def reads_command(args):
        filenames.extend(args)
        for filename in args:
            iterators.append(itertools.izip(
                io.read_sequences(filename, qualities=True)
            ))
    def pairs_command(args):
        assert len(args) == 2, 'Expected a pair of files for "pairs" section'
        filenames.extend(args)
        any_paired[0] = True
        iterators.append(itertools.izip(
            io.read_sequences(args[0], qualities=True),
            io.read_sequences(args[1], qualities=True)
        ))
        
    def interleaved_command(args):
        filenames.extend(args)
        any_paired[0] = True
        for filename in args:
            iterators.append(deinterleave(
                io.read_sequences(filename, qualities=True)
            ))
        
    grace.execute(args, {
        'reads' : reads_command,
        'interleaved' : interleaved_command,
        'pairs' : pairs_command,
    })
    
    fragment_reads = (2 if any_paired[0] else 1)
    
    assert iterators, 'Nothing to clip'

    if qoffset is None:
        guesses = [ io.guess_quality_offset(filename) for filename in filenames ]
        assert len(set(guesses)) == 1, 'Conflicting quality offset guesses, please specify manually.'
        qoffset = guesses[0]
        log.log('FASTQ offset seems to be %d\n' % qoffset)    

    quality_cutoff_char = chr(qoffset + quality_cutoff)
    
    log.log('Minimum quality:        %d (%s)\n' % (quality_cutoff, quality_cutoff_char))
    log.log('Clip ambiguous bases:   %s\n' % (grace.describe_bool(clip_ambiguous)))
    log.log('Minimum adaptor match:  %d bases, %d errors\n' % (adaptor_cutoff, max_error))
    log.log('Minimum length:         %d bases\n' % length_cutoff)
    
    adaptor_seqs = [ ]
    adaptor_names = [ ]
    if adaptor_set and adaptor_set.lower() != 'none':
        for item in adaptor_set.split(','):
            item = item.strip().lower() + ' '
            any = False
            for line in ADAPTORS.strip().split('\n'):
                if line.startswith('#'): continue
                if not line.lower().startswith(item): continue
                any = True
                name, seq = line.rsplit(None, 1)
                seq = seq.replace('U','T')
                
                #if seq in adaptor_seqs: print 'Dup', name
                adaptor_seqs.append(seq)
                adaptor_names.append(name)
                adaptor_seqs.append(bio.reverse_complement(seq))
                adaptor_names.append(name)
            if not any:
                raise grace.Error('Unknown adaptor set: ' + item)
    
    matcher = Matcher(adaptor_seqs, adaptor_names, max_error)
    
    start_clips = [ collections.defaultdict(list) for i in xrange(fragment_reads) ]
    end_clips = [ collections.defaultdict(list) for i in xrange(fragment_reads) ]

    if output_fasta:
        suffix = '.fa'
        write_sequence = io.write_fasta_single_line
    else:
        suffix = '.fq'
        write_sequence = io.write_fastq

    if use_gzip:
        opener = lambda filename: io.open_gzip_writer(filename + '.gz')
    else:
        opener = lambda filename: open(filename, 'wb')    
    f_single = opener(prefix + '_single' + suffix)
    if fragment_reads == 2:
        f_paired = opener(prefix + '_paired' + suffix)
    if output_rejects:
        f_reject = opener(prefix + '_rejected' + suffix)
    
    n_single = 0
    n_paired = 0
    
    n_in_single = 0
    n_in_paired = 0
    total_in_length = [ 0 ] * fragment_reads
    
    n_out = [ 0 ] * fragment_reads
    n_q_clipped = [ 0 ] * fragment_reads
    n_a_clipped = [ 0 ] * fragment_reads
    n_homopolymers = [ 0 ] * fragment_reads
    total_out_length = [ 0 ] * fragment_reads
    
    log.attach(open(prefix + '_log.txt', 'wb'))
    
    for iterator in iterators:
      for fragment in iterator:
        if (n_in_single+n_in_paired) % 10000 == 0:
            grace.status('Clipping fragment %s' % grace.pretty_number(n_in_single+n_in_paired))
    
        if len(fragment) == 1:
            n_in_single += 1
        else:
            n_in_paired += 1
        
        graduates = [ ]
        rejects = [ ]
        for i, (name, seq, qual) in enumerate(fragment):
            name = name.split()[0]
            seq = seq.upper()
            total_in_length[i] += len(seq)
                                
            start = trim_start
            best_start = 0
            best_len = 0
            for j in xrange(len(seq)-trim_end):
                if qual[j] < quality_cutoff_char or \
                   (clip_ambiguous and seq[j] not in 'ACGT'):
                    if best_len < j-start:
                        best_start = start
                        best_len = j-start
                    start = j + 1
            j = len(seq)-trim_end
            if best_len < j-start:
                best_start = start
                best_len = j-start
    
            clipped_seq = seq[best_start:best_start+best_len]
            clipped_qual = qual[best_start:best_start+best_len]
            if len(clipped_seq) < length_cutoff:
                n_q_clipped[i] += 1
                rejects.append( (name,seq,qual,'quality') ) 
                continue
    
            match = matcher.match(clipped_seq)
            if match and match[0] >= adaptor_cutoff:
                clipped_seq = clipped_seq[match[0]:]
                clipped_qual = clipped_qual[match[0]:]
                start_clips[i][match[0]].append( match[1][0] )
                if len(clipped_seq) < length_cutoff:
                    n_a_clipped[i] += 1 
                    rejects.append( (name,seq,qual,'adaptor') ) 
                    continue
        
            match = matcher.match(bio.reverse_complement(clipped_seq))
            if match and match[0] >= adaptor_cutoff:
                clipped_seq = clipped_seq[: len(clipped_seq)-match[0] ]    
                clipped_qual = clipped_qual[: len(clipped_qual)-match[0] ]    
                end_clips[i][match[0]].append( match[1][0] )
                if len(clipped_seq) < length_cutoff:
                    n_a_clipped[i] += 1 
                    rejects.append( (name,seq,qual,'adaptor') ) 
                    continue

            if disallow_homopolymers and len(set(clipped_seq)) <= 1:
                n_homopolymers[i] += 1
                rejects.append( (name,seq,qual,'homopolymer') ) 
                continue
    
            graduates.append( (name, clipped_seq, clipped_qual) )
            n_out[i] += 1
            total_out_length[i] += len(clipped_seq)

        if output_rejects:
            for name,seq,qual,reason in rejects:
                write_sequence(f_reject, name + ' ' + reason, seq, qual)
         
        if graduates:
            if reverse_complement:
                graduates = [
                    (name, bio.reverse_complement(seq), qual[::-1])
                    for name, seq, qual in graduates
                ]
        
            if len(graduates) == 1:
                this_f = f_single
                n_single += 1
            else:
                assert len(graduates) == 2
                this_f = f_paired
                n_paired += 1
            
            for name, seq, qual in graduates:
                write_sequence(this_f, name, seq, qual)
    
    grace.status('')
    
    if output_rejects:
        f_reject.close()
    if fragment_reads == 2:
        f_paired.close()
    f_single.close()
    
    def summarize_clips(clips):
        total = 0
        for i in clips:
            total += len(clips[i])
        log.log(' %d reads\n' % total) 
        
        if not clips:
            return

        for i in xrange(min(clips), max(clips)+1):
            item = clips[i]
            log.quietly_log('%3d bases: %10d ' % (i, len(item)))
            if item:
                avg_errors = float(sum( item2[0] for item2 in item )) / len(item)
                log.quietly_log(' avg errors: %5.2f  ' % avg_errors)
                
                counts = collections.defaultdict(int)
                for item2 in item: counts[item2[1]] += 1
                #print counts
                for no in sorted(counts,key=lambda item2:counts[item2],reverse=True)[:2]:
                    log.quietly_log('%dx%s ' % (counts[no], matcher.names[no]))
                if len(counts) > 2: log.quietly_log('...')
                
            log.quietly_log('\n')
        log.quietly_log('\n')
    
    for i in xrange(fragment_reads):
        if start_clips:
            log.log('Read %d adaptors clipped at start:' % (i+1))
            summarize_clips(start_clips[i])
    
        if end_clips:
            log.log('Read %d adaptors clipped at end: ' % (i+1))
            summarize_clips(end_clips[i])
    
    #log.log('\n%s reads matched adaptor sequences\n\n' % grace.pretty_number( len(clips) ) )
    #
    #log.log('Adaptors:\n')
    #counts = { }
    #for name in clips:
    #    items = clips[name][2]
    #    best_score = max( a for a,b in items )
    #    names = [ b for a,b in items if a >= best_score ]
    #    names.sort()
    #    names = '/'.join(names)
    #    if names not in counts: counts[names] = 0
    #    counts[names] += 1
    #
    #for name in sorted(counts, key=lambda name: counts[name], reverse=True):
    #    log.log(' %s x %s\n' % (counts[name], name))
    #log.log('\n')
        
    if n_in_paired:
        log.log('Pairs:                        %s\n' % grace.pretty_number(n_in_paired))                      
    if n_in_single:
        log.log('Single reads:                 %s\n' % grace.pretty_number(n_in_single))                      
    if fragment_reads == 2:
        log.log('Pairs kept:                   %s\n' % grace.pretty_number(n_paired))                      
    log.log('Single reads kept:            %s\n' % grace.pretty_number(n_single))
    
    if n_in_single or n_in_paired:
        for i in xrange(fragment_reads):
            log.log('\nRead %d:\n' % (i+1))
            log.log('Too short after quality clip: %s\n' % grace.pretty_number(n_q_clipped[i]))
            log.log('Too short after adaptor clip: %s\n' % grace.pretty_number(n_a_clipped[i]))
            if disallow_homopolymers:
                log.log('Homopolymer reads:            %s\n' % grace.pretty_number(n_homopolymers[i]))
            log.log('Kept:                         %s\n' % grace.pretty_number(n_out[i]))
            log.log('Average input length:         %.1f\n' % (float(total_in_length[i]) / (n_in_single+n_in_paired)))                     
            if n_out[i]:
                log.log('Average output length:        %.1f\n' % (float(total_out_length[i]) / n_out[i]))                     
    
    