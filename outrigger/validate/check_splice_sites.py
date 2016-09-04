
from collections import OrderedDict

from Bio import SeqIO
import pandas as pd
import pybedtools

NT = 2


def maybe_read_chromsizes(genome):
    try:
        chromsizes = OrderedDict()
        with open(genome) as f:
            for line in f:
                chrom, size = line.strip().split()
                size = int(size)
                chromsizes[chrom] = (0, size)
    except OSError:
        chromsizes = pybedtools.chromsizes(genome)
    return chromsizes


def read_splice_sites(bed, genome, fasta, direction='upstream'):
    """Read splice sites of an exon

    Parameters
    ----------
    bed : pybedtools.BedTool | str
        Exons whose splice sites you're interested in
    genome : str
        Location of a chromosome sizes file for the genome
    fasta : str
        Location of the genome fasta file
    direction : 'upstream' | 'downstream'
        Which direction of splice sites you want for the exon
    """
    if isinstance(bed, str):
        bed = pybedtools.BedTool(bed)

    genome = maybe_read_chromsizes(genome)

    if direction == 'upstream':
        left = NT
        right = 0
    elif direction == 'downstream':
        left = 0
        right = NT

    flanked = bed.flank(l=left, r=right, s=True, genome=genome)
    seqs = flanked.sequence(fi=fasta, s=True)

    with open(seqs.seqfn) as f:
        records = SeqIO.parse(f, 'fasta')
        records = pd.Series([str(x.seq) for x in records],
                            index=[x.name for x in bed])
    return records
