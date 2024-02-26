#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wmo_grid2grid_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wmo stats step
#                    for the grid-to-grid verification. It uses METplus to
#                    generate the statistics.
###############################################################################

set -x

# Make directories
mkdir -p ${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE} ${MODELNAME}.${VDATE}
mkdir -p jobs logs tmp

# Create and run job scripts for generate_stats and gather_stats
for group in generate_stats gather_stats; do
    export JOB_GROUP=$group
    mkdir -p jobs/${JOB_GROUP}
    echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_wmo_stats_grid2grid_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x jobs/$group/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  jobs/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
            poe_script=$DATA/jobs/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                nselect=$(cat $PBS_NODEFILE | wc -l)
                nnp=$(($nselect * $nproc))
                launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
            elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
                export SLURM_KILL_BAD_EXIT=0
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
            export err=$?; err_chk
            nc=$((nc+1))
        done
    else
        group_ncount_job=$(ls -l  jobs/$group/job* |wc -l)
        while [ $nc -le $group_ncount_job ]; do
            $DATA/jobs/$group/job${nc}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    fi
done

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
fi

# Cat the METplus log files
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi
