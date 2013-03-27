"""
Hub creator for one user/group having multiple NGS data sets
"""
import os
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
        trackdb.local_fn = '%s/trackDb.%s.txt' % (self.name, name)
        self._dbroot.add_trackdbs(trackdb)
        return trackdb
    
    

class ExpTrack(object):
    """
    Composite tracks for one type of experiments (ChIP/CLIP/Gro-seq, etc) 
    """
    def __init__(self, name, short_label, 
        strand2color = {'fwd': '255,0,0', 'rev': '0,0,255'}):
        self.name = name
        self.short_label = short_label
        self.cpt = CompositeTrack(name=self.name,
            short_label=self.short_label,
            long_label="%s composite tracks" % self.short_label,
            tracktype="bigBed 3")
        self.cpt.add_params(dragAndDrop='subtracks', visibility='full')
        self.strand2color = strand2color
    
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
                yield (sample, '')
            else:
                for strand in sorted(self.strand2color):
                    yield (sample, strand)
    
    def samples2view(self, samples, view, stranded=False, template="%s_tag"):
        self.cpt.add_view(view)
        tracktype = view.tracktype
        viewtype = view.view
        for sample, strand in self.iter_samples(samples, stranded):
            samplename = sample
            if stranded:
                samplename = sample+'_'+strand
                
            basename = template % (samplename,)
            track = Track(tracktype=tracktype,
                name='%s%s%s' % (self.name, viewtype, samplename),
                url=os.path.join(self.name, basename+'.'+tracktype),
                shortLabel='%s %s' % (samplename, viewtype), 
                longLabel="%s %s" % (samplename, viewtype),
                )
            if stranded:
                track.add_params(color=self.strand2color[strand])
            view.add_tracks(track)
            