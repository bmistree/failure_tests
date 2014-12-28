import os
import subprocess

def num_flow_table_entries(switch_name):
    '''
    @param {String} switch_name --- Likely just "s1", "s2", etc.
    '''
    cmd_vec = ['ovs-ofctl','dump-flows',switch_name]

    (reading_pipe,writing_pipe) = os.pipe()
    reading_pipe = os.fdopen(reading_pipe,'r')
    writing_pipe = os.fdopen(writing_pipe,'w')

    subprocess.call(cmd_vec,stdout=writing_pipe)
    writing_pipe.flush()
    writing_pipe.close()

    # note starting from -1 here because must handle header returend
    # as part of dump-flows command
    num_entries = -1
    for line in reading_pipe:
        num_entries += 1

    reading_pipe.close()
    writing_pipe.close()
    
    return num_entries

