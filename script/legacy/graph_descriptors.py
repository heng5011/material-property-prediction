import numpy as np
import pandas as pd
import argparse
from data_processing import calculate_descriptors
from time import time
from datetime import datetime

# Setting path------------------------------------------------------------------
# dir_path = "/Users/keishiro/Documents/M2_research" # lab's laptop
dir_path = "/Users/user/Documents/M2_research" # my macbook

# descriptors_dir = dir_path + "/data/to_kanamori/cohesive/descriptors/"
# compounds_list_dir_cohesive = dir_path + "/data/to_kanamori/cohesive/compounds_name"
compounds_list_dir_ltc = dir_path + "/data/to_kanamori/ltc/kappa"
# compounds_list_dir_mp = dir_path + "/data/to_kanamori/ltc/melting_point"
# ------------------------------------------------------------------------------
atomic_df = pd.read_csv(dir_path + "/data/seko/atomic_data_20160603.csv", index_col=0)
atomic_df = atomic_df.drop(["Rps-d"], axis=1)

parser = argparse.ArgumentParser(description="compute graph-based descriptors")
parser.add_argument("--property", required=True, help="property of a dataset")
parser.add_argument("--tol", default=0.25, help="tolerance parameter")
parser.add_argument("--cutoff", default=10, help="cutoff value")
parser.add_argument("--multiply_type", default="element_wise", help="multipication type")
parser.add_argument("--periodic", action="store_true",
                    help="whether periodic boundary condition is considered or not")
parser.add_argument("--descriptor_type", default="mixtured", help="descriptor type")
parser.add_argument("--max_matrix_power", default=10,
                    help="define how many descriptors will be obtained")
parser.add_argument("--quantize_strc", default="trace",
                    help="quantize type for structure descriptors")
parser.add_argument("--quantize_mix", default="sum",
                    help="quantize type for mixtured descriptors")
parser.add_argument("--save_path", required=True, help="path to save data")
parser.add_argument("--isTest", action="store_true", help="whether to test or not")
args = parser.parse_args()


if __name__ == "__main__":
    descriptors = []
    compounds_list = []

    if args.property == "cohesive":
        compounds_list_dir = compounds_list_dir_cohesive
    elif args.property == "ltc":
        compounds_list_dir = compounds_list_dir_ltc
    elif args.property == "mp":
        compounds_list_dir = compounds_list_dir_mp

    start = time()
    print('Started at {}'.format(datetime.now()))

    with open(compounds_list_dir) as f:
        lines = f.readlines()
        if args.isTest == True:
            n_samples = 10
        else:
            n_samples = len(lines)

        for i in range(n_samples):
            if i % 100 == 0:
                print(str(i) + "compounds are done!")

            if args.property == "cohesive":
                compound_dir = lines[i].strip()
                POSCAR_path = descriptors_dir + compound_dir + "/POSCAR"
            elif args.property == "ltc" or args.property == "mp":
                line = lines[i].strip().split()
                compound_dir = line[0]
                POSCAR_path = dir_path + compound_dir + "/POSCAR"
            compounds_list.append(compound_dir)

            # compute descriptors
            descriptor = calculate_descriptors(atomic_df, POSCAR_path,
                                        tol=args.tol,
                                        cutoff=args.cutoff,
                                        multiplication_type=args.multiply_type,
                                        isPeriodic=args.periodic,
                                        descriptor_type=args.descriptor_type,
                                        max_matrix_power=args.max_matrix_power,
                                        quantize_type_for_structure=args.quantize_strc,
                                        quantize_type_for_mixtured=args.quantize_mix)
            descriptors.append(descriptor)

        print('It took {} sec.'.format(time() - start))

        if args.descriptor_type == "mixtured":
            columns_list = ['Z_diff', 'Period_diff', 'Group_diff', 'm_diff', 'kai(Pauling)_diff',\
                            'kai(Allen)_diff', 'EA_diff', 'IE1_diff', 'IE2_diff', 'Rps-s_diff', \
                            'Rps-p_diff', 'Rvdw_diff', 'Rcov_diff', 'MP_diff', 'BP_diff', 'Cp-g_diff',\
                            'Cp-mol_diff', 'rho_diff', 'E-fusion_diff','E-vapor_diff', 'Thermal-Cond_diff', \
                            'Ratom_diff', 'Mol-Vol_diff', 'Z_ave', 'Period_ave', 'Group_ave', \
                            'm_ave', 'kai(Pauling)_ave', 'kai(Allen)_ave', 'EA_ave', 'IE1_ave', \
                            'IE2_ave', 'Rps-s_ave', 'Rps-p_ave', 'Rvdw_ave', 'Rcov_ave', 'MP_ave', \
                            'BP_ave', 'Cp-g_ave', 'Cp-mol_ave', 'rho_ave', 'E-fusion_ave', 'E-vapor_ave', \
                            'Thermal-Cond_ave', 'Ratom_ave', 'Mol-Vol_ave', 'Z_std', 'Period_std', \
                            'Group_std', 'm_std', 'kai(Pauling)_std', 'kai(Allen)_std', 'EA_std', \
                            'IE1_std', 'IE2_std', 'Rps-s_std', 'Rps-p_std', 'Rvdw_std', 'Rcov_std', \
                            'MP_std', 'BP_std', 'Cp-g_std', 'Cp-mol_std', 'rho_std', 'E-fusion_std', \
                            'E-vapor_std', 'Thermal-Cond_std', 'Ratom_std', 'Mol-Vol_std']
        elif args.descriptor_type == "structure":
            columns_list = range(len(descriptors[0]))

        # print (compounds_list, '\n', columns_list)
        df_descriptors = pd.DataFrame(np.array(descriptors),
                                        columns=columns_list,
                                        index=compounds_list)
        df_descriptors.to_csv(args.save_path)
