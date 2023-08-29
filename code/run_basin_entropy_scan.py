# run_basin_entropy_scan.py
#
# Bryan Daniels, Enrico Borriello
# 2023/8/29
#
# Calculate control kernels for scan over random networks with
# network size n, number of attractors r and basin entropy eta.
#

import AttAttach.attattach as ata
import numpy as np
from control_kernel_analysis import ck_analysis
from TransitionNetwork import transitions_to_net
from entropy_and_basin_sizes import entropy_to_basin_sizes,min_basin_entropy,max_basin_entropy,basin_entropy
import csv
from datetime import datetime



# set parameters for scan
n_list = range(8,20)
r_list = [2,5,10,20,50,100]
num_entropies = 100
seed_list = range(1000,1010)

csv_filename = 'CK_vs_entropy_data_scan.csv'

with open(csv_filename,mode='a',newline='') as file:
    
    # set up output file
    writer = csv.writer(file)
    # write header to output file
    writer.writerow(['n','r','eta','seed','ck_mean_size','elapsed_time'])

    # loop over network size
    for n in n_list:

        # loop over number of attractors
        for r in r_list:

            # make list of desired basin entropies h_tildes
            h_tildes = np.linspace(min_basin_entropy(r,n),max_basin_entropy(r),num_entropies)
            # make corresponding list of lists of basin sizes
            w_list = [ entropy_to_basin_sizes(h_tilde,r,n,tol=1e-2) for h_tilde in h_tildes ]
            # make corresponding list of actual entropies etas
            eta_list = [ basin_entropy(w/2**n) for w in w_list ]

            # loop over basin entropy
            for w,eta in zip(w_list,eta_list):
                landscape_structure = [ [1,wi/2**n] for wi in w ]
                
                # loop over samples for a given basin entropy
                for seed in seed_list:
                    print("Running n={}, r={}, eta={}, seed={}".format(n,r,eta,seed))
                
                    np.random.seed(seed)
                    start_time = datetime.now()
                    
                    edges = ata.generate_landscape(n,landscape_structure)
                    if edges:
                        transitions = [ e[1] for e in edges ]
                        net = transitions_to_net(transitions)
                        ck_data = ck_analysis(net)
                        ck_mean_size = np.mean(ck_data['control_kernel_sizes'])
                        
                        end_time = datetime.now()
                        elapsed_time = end_time - start_time
                        
                        # write data to output file
                        writer.writerow([n,r,eta,seed,ck_mean_size,elapsed_time])
                    else:
                        print("run_basin_entropy_scan ERROR: Error in generate_landscape.  Skipping network.")