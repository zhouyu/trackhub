"""
Root trackDb.txt for including multiple trackDb files
"""
import os
from validate import ValidationError
from base import HubComponent
from genomes_file import GenomesFile
from genome import Genome
import trackdb as _trackdb

class TrackDbRoot(HubComponent):
    def __init__(self, trackdbs=None):
        """
        Represents the file containing one or more include trackDb.* lines
        """
        HubComponent.__init__(self)
        if trackdbs is None:
            trackdbs = []

        self._trackdbs = []
        for trackdb in trackdbs:
            self.add_trackdbs(trackdb)

        self._local_fn = None
        self._remote_fn = None

    @property
    def hub(self):
        return self.root(cls=Hub)

    @property
    def genomes_file(self):
        genomes_file, level = self.root(GenomesFile)
        if level is None:
            return None
        if level != -2:
            raise ValueError("GenomesFile is level %s, not -2" % level)
        return genomes_file

    @property
    def genome(self):
        genome, level = self.root(Genome)
        if level is None:
            return None
        if level != -1:
            raise ValueError('Genome is level %s, not -1' % level)
        return genome

    @property
    def local_fn(self):
        if self._local_fn is not None:
            return self._local_fn

        if self.genome is None:
            return None

        if self.genomes_file is None:
            return None

        else:
            return os.path.join(os.path.dirname(self.genomes_file.local_fn),
                                self.genome.genome, 'trackDb.txt')

    @local_fn.setter
    def local_fn(self, fn):
        self._local_fn = fn

    @property
    def remote_fn(self):
        if self._remote_fn is not None:
            return self._remote_fn

        if self.genome is None:
            return None

        if self.genomes_file is None:
            return None

        else:
            return os.path.join(os.path.dirname(self.genomes_file.remote_fn),
                                self.genome.genome, 'trackDb.txt')

    @remote_fn.setter
    def remote_fn(self, fn):
        self._remote_fn = fn

    def add_trackdbs(self, trackdb):
        """
        Add a track or iterable of tracks.

        :param track:
            Iterable of :class:`Track` objects, or a single :class:`Track`
            object.
        """
        if isinstance(trackdb, _trackdb.TrackDb):
            self.add_child(trackdb)
            self._trackdbs.append(trackdb)
        else:
            for t in trackdb:
                self.add_child(t)
                self._trackdbs.append(t)

    def __str__(self):
        s = []
        for trackdb in self._trackdbs:
            s.append('include %s' % os.path.basename(trackdb.local_fn))
        return '\n'.join(s)

    def validate(self):
        if len(self.children) == 0:
            raise ValidationError("No TrackDb objects specified")

    def _render(self):
        dirname = os.path.dirname(self.local_fn)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        fout = open(self.local_fn, 'w')
        fout.write(str(self))
        fout.close()
        return fout.name
