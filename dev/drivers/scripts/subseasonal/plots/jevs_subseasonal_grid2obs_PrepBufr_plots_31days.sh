#PBS -N jevs_subseasonal_grid2obs_PrepBufr_plots_31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter,select=1:ncpus=32:ompthreads=1:mem=10GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR
module reset

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/subseasonal/subseasonal_plots.sh
#%include <head.h>
#%include <envir-p1.h>

export MET_ROOT=/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}

export USER=$USER
export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=32
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=plots
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME="gefs cfs"
export VERIF_CASE=grid2obs
export VERIF_TYPE=PrepBufr
export NDAYS=31

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMINcfs=$COMIN/stats/$COMPONENT/cfs
export COMINgefs=$COMIN/stats/$COMPONENT/gefs
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export VDATE_START=$(date -d "today -32 day" +"%Y%m%d")
export VDATE_END=$(date -d "today -2 day" +"%Y%m%d")
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$VDATE_END

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.${COMPONENT}.${VERIF_CASE}.${STEP}.${VERIF_TYPE}

# Call executable job script
$HOMEevs/jobs/subseasonal/plots/JEVS_SUBSEASONAL_PLOTS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal grid-to-obs 2-m temperature statistical plots
#          for the GEFS and CFS models for past 31 days.
######################################################################
#%end
