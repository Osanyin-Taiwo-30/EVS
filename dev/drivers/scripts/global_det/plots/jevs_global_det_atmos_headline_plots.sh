#PBS -N jevs_global_det_atmos_headline_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l select=1:ncpus=1:mem=35GB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export RUN_ENVIR=nco
export SENDCOM=YES
export KEEPDATA=NO
export job=${PBS_JOBNAME:-jevs_global_det_atmos_headline_plots}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

module reset
source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/global_det/global_det_plots.sh
export MET_bin_exec=bin

export machine=WCOSS2

export envir=dev
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=headline


export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMINdailystats=$COMIN/stats/$COMPONENT
export COMINyearlystats=$COMIN/stats/$COMPONENT/long_term/annual_means
export VDATE_END=$(date -d "24 hours ago" '+%Y%m%d')
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$VDATE_END

# CALL executable job script here
$HOMEevs/jobs/global_det/plots/JEVS_GLOBAL_DET_ATMOS_HEADLINE_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-grid headline scores
######################################################################
