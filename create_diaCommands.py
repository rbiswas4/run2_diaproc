
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create_diaCommands.py
#  
#  Copyright 2019 bruno <bruno.sanchez@duke.edu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sqlite3
import pandas as pd


database = '/global/cscratch1/sd/desc/DC2/data/Run2.1i/rerun/calexp-v1/tracts_mapping.sqlite3'
query_tmpl = "select DISTINCT(visit), filter from overlaps WHERE tract={} and patch={} order by visit"
tmpl_repo = '/global/cscratch1/sd/bos0109/templates_003/rerun/multiband'
output_repo = '/global/cscratch1/sd/bos0109/test_imdiff_run2'
config_path = 'imageDifferenceDriver_config.py'

cmd_tmpl = "time nice -n 10 imageDifferenceDriver.py  {} --output {} "
cmd_tmpl +="--id visit={} -C {} --batch-type={} --mpiexec='-bind-to socket' " 
cmd_tmpl +="--cores {} --job imdiff_v{}_f{} --time 500 "
cmd_tmpl +="--batch-options='-C knl -q regular'"


def main(tract, patch, filters='griz', outfile='driver_commands/diaCommands.sh', 
         database=database, batch='smp', cores=4, tmpl_repo=tmpl_repo, 
         output_repo=output_repo, config_path=config_path):

    conn = sqlite3.connect(database)
    #c = conn.cursor()
    patchx, _, patchy = patch 
    strpatch = "'"+str((int(patchx), int(patchy)))+"'"
    query = query_tmpl.format(tract, strpatch)
    visitab = pd.read_sql_query(query, conn)

    commands = []
    for filtr, visits in visitab.groupby('filter'):
        if filtr in list(filters):
            print(filtr, visits.visit)
            for avisit in visits.visit:
                cmd = cmd_tmpl.format(tmpl_repo, output_repo, 
                    avisit, config_path, batch, cores, avisit, filtr)
                commands.append(cmd)

    with open(outfile, 'w') as cf:
        for acmd in commands:
            cf.write(acmd)
            cf.write('\n \n')
    print("Wrote {} commands to {}".format(len(commands), outfile))
    return



if __name__=='__main__':
    import argparse
    DESC = "Creates commands for difference image driver in the dia_pipe context"
    EPIL = "This will produce a file output with the commands separated by one line"
    parser = argparse.ArgumentParser(description=DESC, epilog=EPIL)
    parser.add_argument('-t', '--tract', metavar='t', type=int, 
                        help='Tract number')
    parser.add_argument('-p', '--patch', metavar='p', type=str, 
                        help='Patch code number')
    parser.add_argument('-f', '--filter', metavar='f', type=str, 
                        help='Filter name', default='griz')
    parser.add_argument('-o', '--outfile', metavar='o', type=str, 
                        help='Output filename with the commands', 
                        default='driver_commands/diaCommands.sh')
    parser.add_argument('-db', '--database', metavar='db', type=str, 
                        dest='database', default=database, 
                        help='Database of tract+patchs to find out visits')
    parser.add_argument('-c', '--cores', metavar='c', type=int, default=4, 
                        help='Number of cores')
    parser.add_argument('-b', '--batch-type', metavar='b', type=str, 
                        default='smp', help='slurm or smp batch processing')
    parser.add_argument('-r', '--tmpl', metavar='R', type=str, default=tmpl_repo, 
                        help='Repository where templates are located')
    parser.add_argument('-d', '--diff', metavar='D', type=str, default=output_repo, 
                        help='Repository where differences are going to be located')
    parser.add_argument('-C', '--conf', metavar='C', type=str, default=config_path, 
                        help='Path of configuration file')
    args = parser.parse_args()

    main(args.tract, args.patch, filters=args.filter, outfile=args.outfile, 
         database=args.database, batch=args.batch_type, cores=args.cores, 
         tmpl_repo=args.tmpl, output_repo=args.diff, config_path=args.conf)
