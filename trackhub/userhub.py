"""
Hub creator for one user/group having multiple NGS data sets
"""


import os
import sys
from hub import Hub
from genome import Genome
from genomes_file import GenomesFile
from track import Track, CompositeTrack, ViewTrack
from trackdb import TrackDb
from trackdbroot import TrackDbRoot


class UserHub(object):
    """
    Create hub for a set of NGS data from one user/group
    """
    def __init__(self, name, short_label, email):
        self.hub = Hub(name,
              short_label=short_label,
              long_label='Tracks for %s' % short_label,
              email=email)
        self.genomes_file = GenomesFile()
        self.hub.add_genomes_file(self.genomes_file)

    def add_genomehub(self, genome_hub):
        self.genomes_file.add_genome(genome_hub.genome)

    def render(self):
        return self.hub.render()


class GenomeHub(object):
    """
    Hub for a specific genome such as hg18, mm9
    """
    def __init__(self, name):
        self._name = name
        self._genome = Genome(self._name)
        self._dbroot = TrackDbRoot()
        self._genome.add_trackdb(self._dbroot)

    @property
    def name(self):
        return self._name

    @property
    def genome(self):
        return self._genome

    def add_trackdb(self, name):
        """
        create a trackdb with given name for this genome
        """
        trackdb = TrackDb()
        trackdb.local_fn = os.path.join(self.name, 'trackDb.%s.txt' % name)
        datadir = os.path.join(self.name, name)
        if not os.path.exists(datadir):
            os.mkdir(datadir)

        self._dbroot.add_trackdbs(trackdb)
        return trackdb


class ExpTrack(object):
    """
    Composite tracks for multiple samples from one type of experiments, such as
    ChIP/CLIP/Gro-seq, etc.
    TODO: support subgroups, such as strand, time-course
    """
    COLORS = ('0,0,0', '255,0,0', '0,255,0', '0,0,255', '255,153,0')
    def __init__(self, name, short_label,
        strand2color = {'fwd': '255,0,0', 'rev': '0,0,255'},
        priority_init=0, priority_step=0.01):
        self.name = name
        self.short_label = short_label
        self.cpt = CompositeTrack(name=self.name,
            short_label=self.short_label,
            long_label="%s composite tracks" % self.short_label,
            tracktype="bigBed 3") # bare-bone format
        self.cpt.add_params(dragAndDrop='subtracks', visibility='full')
        self.strand2color = strand2color
        self.priority = priority_init
        self.priority_step = priority_step

    @property
    def track(self):
        return self.cpt

    def create_view(self, viewtype, tracktype, *args, **kwargs):
        kwargs['name'] = "%s%sView" % (self.name, viewtype)
        kwargs['tracktype'] = tracktype
        return ViewTrack(viewtype, *args, **kwargs)

    def iter_samples(self, samples, stranded=False):
        for sample in samples:
            if not stranded:
                yield (sample, '.')
            else:
                for strand in sorted(self.strand2color):
                    yield (sample, strand)

    def tracktype2suffix(self, tracktype):
        """Determine track data file suffix from view tracktype"""
        if tracktype.startswith("bigBed"):
            return "bigBed"
        elif tracktype.startswith("bam"):
            return "bam"
        elif tracktype.startswith("bigWig"):
            return "bigWig"
        else:
            return tracktype

    def samples2view(self, samples, view, stranded=False, template="%s_tag",
        setColor=False, colorByStrand=True):
        self.cpt.add_view(view)
        tracktype = view.tracktype
        viewtype = view.view

        suffix = self.tracktype2suffix(tracktype)
        for sample, strand in self.iter_samples(samples, stranded):
            samplename = sample
            if stranded:
                samplename = sample+'_'+strand

            basename = template % (samplename,)
            self.priority += self.priority_step
            track = Track(
                tracktype=tracktype,
                name='%s%s%s' % (self.name, viewtype, samplename),
                url=os.path.join(self.name, basename+'.'+suffix),
                shortLabel='%s %s' % (samplename, viewtype),
                longLabel="%s %s" % (samplename, viewtype),
                priority=self.priority,
                )
            sys.stderr.write(str(track)+"\n")
            if setColor:
                if colorByStrand and strand in self.strand2color:
                    track.add_params(color=self.strand2color[strand])
                else:
                    idx = samples.index(sample) % len(ExpTrack.COLORS)
                    track.add_params(color=ExpTrack.COLORS[idx])

            view.add_tracks(track)

    def add_samples(self, samples, stranded=True, colorByStrand=False):
        """(ExpTrack, list, boolean) -> NoneType
        Create composite track of 3 views on given samples
        """
        readview = self.create_view('READ', "bam", visibility="squish")
        self.samples2view(samples, readview, template="%s_tag", setColor=False)
        sigview = self.create_view('SIG', "bigWig", visibility="full")
        self.samples2view(
            samples, sigview, template="%s", setColor=True,
            stranded=stranded, colorByStrand=colorByStrand)
        normview = self.create_view('SIGnorm', "bigWig", visibility="full")
        self.samples2view(
            samples, normview, template="%s_norm", setColor=True,
            stranded=stranded, colorByStrand=colorByStrand)

