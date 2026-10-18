from core.utils import set_seed
from config import CONFIG

from experiments.exp1_mode_comparison import run_exp1
from experiments.exp2_scalability import run_exp2
from experiments.exp3_hop_impact import run_exp3
from experiments.exp4_qkd_utilization import run_exp4
from experiments.exp5_overhead_breakdown import run_exp5
from experiments.exp6_migration_aware import run_exp6
from experiments.exp7_adaptive_fallback import run_exp7
from experiments.exp8_partial_compromise import run_exp8
from experiments.exp9_naive_sensitivity import run_exp9
from experiments.exp10_availability_sweep import run_exp10


def main():
    set_seed(CONFIG['seed'])
    print('Running Migration-Aware hybrid Cryptographic simulation model...')

    run_exp1()
    run_exp2()
    run_exp3()
    run_exp4()
    run_exp5()
    run_exp6()
    run_exp7()
    run_exp8()
    run_exp9()
    run_exp10()

    print('Done. Check results/raw and results/plots')


if __name__ == '__main__':
    main()