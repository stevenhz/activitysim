import os
import sys
import logging
import multiprocessing

from activitysim.core import inject
from activitysim.core import tracing
from activitysim.core import config
from activitysim.core import pipeline
# from activitysim import abm

import tasks

logger = logging.getLogger('activitysim')


def cleanup_output_files():

    active_log_files = \
        [h.baseFilename for h in logger.root.handlers if isinstance(h, logging.FileHandler)]
    tracing.delete_output_files('log', ignore=active_log_files)

    tracing.delete_output_files('h5')
    tracing.delete_output_files('csv')
    tracing.delete_output_files('txt')


if __name__ == '__main__':

    # inject.add_injectable('data_dir', '/Users/jeff.doyle/work/activitysim-data/mtc_tm1/data')
    inject.add_injectable('data_dir', '../example/data')
    inject.add_injectable('configs_dir', ['configs', '../example/configs'])
    # inject.add_injectable('configs_dir', '../example/configs')

    config.handle_standard_args()
    tracing.config_logger()

    # cleanup if not resuming
    if not config.setting('resume_after', False):
        cleanup_output_files()

    run_list = tasks.get_run_list()

    tasks.print_run_list(run_list)

    t0 = tracing.print_elapsed_time()

    if run_list['multiprocess']:
        logger.info("run multiprocess simulation")
        logger.info("main process pid : %s" % os.getpid())
        logger.info("sys.executable : %s" % sys.executable)
        logger.info("cpu count : %s" % multiprocessing.cpu_count())

        tasks.run_multiprocess(run_list)

    else:
        logger.info("run single process simulation")

        # tasks.run_simulation(run_list['models'], run_list['resume_after'])
        pipeline.run(models=run_list['models'], resume_after=run_list['resume_after'])

        # tables will no longer be available after pipeline is closed
        pipeline.close_pipeline()

    t0 = tracing.print_elapsed_time("mp_simulation", t0)
