#!/bin/ksh

set -x 

day=$1
MODEL_LIST=$2
VRF_CASE=${VERIF_CASE}

archive=$output_base_dir
prefix=${COMIN%%mesoscale*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  model_archive=${archive}/${model}
  mkdir -p $model_archive

  cd $model_archive

  if [ $model = gefs ] ; then
    model_stat_dir=${COM_IN}/global_ens/${model}.${day}
    if [ -s ${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat ] ; then
      ln -sf ${model_stat_dir}/evs.stats.${model}.atmos.${VRF_CASE}.v${day}.stat ${MODEL}_${day}.stat
    fi
  elif [ $model = sref ] ; then
    model_stat_dir=${COM_IN}/mesoscale/${model}.${day}
    if [ $VRF_CASE = cnv ] ; then
         if [ -s ${model_stat_dir}/evs.stats.${model}.grid2obs.v${day}.stat ] ; then
 	    ln -sf ${model_stat_dir}/evs.stats.${model}.grid2obs.v${day}.stat ${MODEL}_${day}.stat
	 fi
    else	       
         if [ -s ${model_stat_dir}/evs.stats.${model}.${VRF_CASE}.v${day}.stat ] ; then
            ln -sf ${model_stat_dir}/evs.stats.${model}.${VRF_CASE}.v${day}.stat ${MODEL}_${day}.stat
         fi
    fi
  else
     echo "Wrong model"
     exit
  fi 

done
  

