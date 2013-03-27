#!/usr/bin/env python

import os
from trackhub.helpers import show_rendered_files
from trackhub.userhub import UserHub, GenomeHub, ExpTrack

if __name__ == '__main__':
    uhub = UserHub('test', 'FuLab', 'y6zhou@ucsd.edu')
    hg18 = GenomeHub('hg18')
    uhub.add_genomehub(hg18)
    
    db = hg18.add_trackdb('XX')
    exp = ExpTrack('XXChIP', '2013/03 XXChIP')
    readview = exp.create_view('READ', "bam", visibility="squish")
    exp.samples2view(['input', 'XX'], readview, template="%s_tag")
    sigview = exp.create_view('SIG', "bigWig", visibility="full")
    exp.samples2view(['input', 'XX'], sigview, template="%s")
    db.add_tracks([exp.track])
    
    exp = ExpTrack('XXGroseq', '2013/04 XXGroseq')
    readview = exp.create_view('READ', "bam", visibility="squish")
    exp.samples2view(['input', 'XX'], readview, template="%s_tag")
    sigview = exp.create_view('SIG', "bigWig", visibility="full")
    exp.samples2view(['input', 'XX'], sigview, stranded=True, template="%s")
    db.add_tracks([exp.track])
    
    results = uhub.render()
    show_rendered_files(results)