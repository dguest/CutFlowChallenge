"""
    CutFlowChallenge

    author: Brett Jackson <brett.david.jackson@cern.ch>

    Simple script that reads users' cut flow tables (provided as text files)
    and processes them for comparison
"""
#!/usr/bin/env python

import sys
import os.path
import optparse
import time

import sqltable as sql

# ----------------------------------------------------------------------------
def parse_input():
    """
    function to parse user inputs
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    parser = optparse.OptionParser( usage="%prog [options]" )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    parser.add_option( '--cutflow'
                     , dest    = 'cut_flow_file'
                     , action  = 'store'
                     , default = ''
                     , help    = 'File containing cuts belonging to cut flow'
                     )
    parser.add_option( '--out-file'
                     , dest    = 'out_file'
                     , action  = 'store'
                     , default = ''
                     , help    = 'output file name'
                     )

    (inputs, files) = parser.parse_args()
    print 'inputs'
    print inputs

    # if inputs['cut_flow_file'] == '':
    if inputs.cut_flow_file == '':
        print 'Please enter a cut flow file -- exiting'
        sys.exit()

    if inputs.out_file == '':
        tmp_file_name = inputs.cut_flow_file
        inputs.out_file = tmp_file_name.replace('.txt', '.log')
        print 'No output file supplied! Setting to %s' % inputs.out_file

    return (inputs, files)

# -----------------------------------------------------------------------------
def constructCutFlow(cut_flow_file):
    """
    from the cut flow file, construct a list of the cuts that are to be applied
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cuts = []
    with open(cut_flow_file) as f:
        for line in f:
            cuts.append(line.strip('\n'))
    return cuts

# -----------------------------------------------------------------------------
def readUserCutFlow(user_file, cuts):
    """
    Read a user's cut flow file, then construct a dictionary with cut flow
    numbers. The functions will return a dictionary containing each of the cuts
    as well as come meta-data such as user name, and a field for notes.
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    user = {'name':'', 'notes':''}
    with open(user_file) as f:
        for line in f:
            # split line, and do safety checks
            contents = line.strip('\n').split(':')
            if len(contents) == 0: continue
            if len(contents) < 2:
                print 'Warning: Line beginning with "%s" has no dividers' \
                        % contents[0]
                print '\tSkipping this line'
                continue
            if len(contents) > 2:
                print 'Warning: Line beginning with "%s" has too many dividers' \
                        % contents[0]
                print '\tSkipping this line'
                continue

            # check for name and notes entries
            if contents[0].lower() == 'name':
                user['name'] = contents[1]
                continue
            if contents[0].lower() == 'notes':
                user['notes'] = contents[1]
                continue

            for c in cuts:
                if contents[0].lower() == c.lower():
                    user[c] = '%s' % contents[1]
                    break

    # check that all the entries from cuts are found in the dictionary
    # if not, add empty string
    for c in cuts:
        if not c in user:
            user[c] = ''

    return user

# -----------------------------------------------------------------------------
def displayCutFlows(cuts, user_cut_flows):
    """
    display the user cut flows in a table
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    column_width = 15

    name_line = '|  %15s  |' % 'Name'
# ...     print("{0:>5}".format(i))

    for name in user_cut_flows:
        name_line += '  %15s  |' % name
    # name_line += '\t|'
    print name_line

    for c in cuts:
        c_line = '|  %15s  |' % c
        for name in user_cut_flows:
            c_line += '  %15s  |' % user_cut_flows[name][c]
        print c_line

# -----------------------------------------------------------------------------
def main():
    """
    main funtion of cut flow challenge code
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    (inputs, files) = parse_input()

    cuts = constructCutFlow(inputs.cut_flow_file)

    sql.constructSqlTable(cuts, file_name = 'cutflow.db')

    user_cut_flows = {}
    for f in files:
        user = readUserCutFlow(f, cuts)
        user_cut_flows[user['name']] = user

    sql.writeCutsToSql(user_cut_flows, 'cutflow.db')

    print sql.readCutsFromSql('cutflow.db')

    displayCutFlows(cuts, user_cut_flows)


# =============================================================================
if __name__ == '__main__':
    main()
