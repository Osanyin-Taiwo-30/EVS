'''
Name: mesoscale_precip_prep.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import datetime
import glob
import shutil
import sys
import datetime

print(f"BEGIN: {os.path.basename(__file__)}")

cwd = os.getcwd()
print(f"Working in: {cwd}")

# Read in common environment variables
DATA = os.environ['DATA']
MODELNAME = os.environ['MODELNAME']
COMINccpa = os.environ['COMINccpa']
COMINmrms = os.environ['COMINmrms']
COMOUT = os.environ['COMOUT']
VDATE = os.environ['VDATE']
VHOUR_LIST = os.environ['VHOUR_LIST'].split(' ')
CYC_LIST = os.environ['CYC_LIST'].split(' ')
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
USER = os.environ['USER']
jobid = os.environ['jobid']

mail_cmd = 'mail -s "$subject" $maillist'

def check_file(file_path):
    """! Check file exists and not zero size
         Args:
             file_path - full path to file (string)
         Returns:
             file_good - full call to METplus (boolean)
    """
    if os.path.exists(file_path):
        if os.path.getsize(file_path) > 0:
            file_good = True
        else:
            file_good = False
    else:
        file_good = False
    return file_good

def format_filler(unfilled_file_format, valid_time_dt, init_time_dt,
                  forecast_hour, str_sub_dict):
    """! Creates a filled file path from a format
         Args:
             unfilled_file_format - file naming convention (string)
             valid_time_dt        - valid time (datetime)
             init_time_dt         - initialization time (datetime)
             forecast_hour        - forecast hour (string)
             str_sub_dict         - other strings to substitue (dictionary)
         Returns:
             filled_file_format - file_format filled in with verifying
                                  time information (string)
    """
    filled_file_format = '/'
    format_opt_list = ['lead', 'lead_shift', 'valid', 'valid_shift',
                       'init', 'init_shift', 'cycle']
    if len(list(str_sub_dict.keys())) != 0:
        format_opt_list = format_opt_list+list(str_sub_dict.keys())
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   if format_opt in ['lead_shift', 'valid_shift',
                                     'init_shift']:
                       shift = (filled_file_format_chunk \
                                .partition('shift=')[2] \
                                .partition('}')[0])
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .rpartition('?')[0]
                       )
                   else:
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0]
                       )
                   if format_opt == 'valid':
                       replace_format_opt_count = valid_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour) < 10:
                               replace_format_opt_count = forecast_hour[1]
                           else:
                               replace_format_opt_count = forecast_hour
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = forecast_hour.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = forecast_hour.zfill(3)
                       else:
                           replace_format_opt_count = forecast_hour
                   elif format_opt == 'init':
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'cycle':
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       ) 
                   elif format_opt == 'lead_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       forecast_hour_shift = str(int(forecast_hour)
                                                 + int(shift))
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour_shift) < 10:
                               replace_format_opt_count = (
                                   forecast_hour_shift[1]
                               )
                           else:
                               replace_format_opt_count = forecast_hour_shift
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(2)
                           )
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(3)
                           )
                       else:
                           replace_format_opt_count = forecast_hour_shift
                   elif format_opt == 'init_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       init_shift_time_dt = (
                           init_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = init_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'valid_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       valid_shift_time_dt = (
                           valid_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = valid_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   else:
                       replace_format_opt_count = str_sub_dict[format_opt]
                   if format_opt in ['lead_shift', 'valid_shift', 'init_shift']:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt
                               +'?shift='+shift+'}',
                               replace_format_opt_count
                           )
                       )
                   else:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt+'}',
                               replace_format_opt_count
                           )
                       )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format

VHOUR_LIST=['12']
for VHOUR in VHOUR_LIST:
    # What accumulations stats will be run for
    accum_list = ['01']
    if int(VHOUR) % 3 == 0:
        accum_list.append('03')
    if int(VHOUR) == 12:
        accum_list.append('24')
    for accum in accum_list:
        accum_end_dt = datetime.datetime.strptime(VDATE+VHOUR, '%Y%m%d%H')
        accum_start_dt = accum_end_dt - datetime.timedelta(hours=int(accum))
        valid_dt = accum_end_dt
        # MODEL
        DATAmodel = os.path.join(DATA, 'data', MODELNAME)
        if not os.path.exists(DATAmodel):
            os.makedirs(DATAmodel)
            print(f"Making directory {DATAmodel}")
        fhr_start = os.environ[f"ACCUM{accum}_FHR_START"]
        fhr_end = os.environ[f"ACCUM{accum}_FHR_END"]
        fhr_incr = os.environ[f"ACCUM{accum}_FHR_INCR"]
        print(f"\nGetting {MODELNAME} files for accumulation {accum}hr valid "
              +f"{accum_start_dt:%Y%m%d %H}Z to {accum_end_dt:%Y%m%d %H}Z")
        fhrs = range(int(fhr_start), int(fhr_end)+int(fhr_incr), int(fhr_incr))
        for area in ['CONUS', 'AK']:
            COMINmodel_file_template = os.environ[f"{area}_MODEL_INPUT_TEMPLATE"]
            DATAmodel_file_template = os.path.join(
                DATAmodel, MODELNAME+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
            )
            for fhr in fhrs:
                init_dt = valid_dt - datetime.timedelta(hours=fhr)
                if f"{init_dt:%H}" in CYC_LIST:
                    if MODELNAME == 'rap' \
                            and f"{init_dt:%H}" not in ['03','09','15','21'] \
                            and fhr > 21:
                        continue
                    model_file_pairs_for_accum_list = []
                    if MODELNAME == 'nam':
                        if accum == '01':
                            COMINmodel_file = format_filler(
                                COMINmodel_file_template, valid_dt, init_dt,
                                str(fhr), {}
                            )
                            DATAmodel_file = format_filler(
                                DATAmodel_file_template, valid_dt, init_dt,
                                str(fhr), {}
                            )
                            model_file_pairs_for_accum_list.append(
                                (COMINmodel_file, DATAmodel_file)
                            )
                            if f"{init_dt:%H}" in ['00', '12']:
                                precip_bucket = 12
                            else:
                                precip_bucket = 3
                            if fhr % precip_bucket != 1 and fhr-1 >=0:
                                COMINmodel_file = format_filler(
                                    COMINmodel_file_template, valid_dt,
                                    init_dt, str(fhr-1), {}
                                )
                                DATAmodel_file = format_filler(
                                    DATAmodel_file_template, valid_dt, init_dt,
                                    str(fhr-1), {}
                                )
                                model_file_pairs_for_accum_list.append(
                                    (COMINmodel_file, DATAmodel_file)
                                )  
                        else:
                            nfiles_in_accum = int(accum)/3
                            nfile = 1
                            while nfile <= nfiles_in_accum:
                                nfile_fhr = fhr - ((nfile-1)*3)
                                if nfile_fhr >= 0:
                                    COMINmodel_file = format_filler(
                                        COMINmodel_file_template, valid_dt,
                                        init_dt, str(nfile_fhr), {}
                                    )
                                    DATAmodel_file = format_filler(
                                        DATAmodel_file_template, valid_dt, init_dt,
                                        str(nfile_fhr), {}
                                    )
                                    model_file_pairs_for_accum_list.append(
                                        (COMINmodel_file, DATAmodel_file)
                                    )
                                nfile+=1
                    else:
                        # Assuming continuous precip buckets
                        COMINmodel_file = format_filler(
                            COMINmodel_file_template, valid_dt, init_dt,
                            str(fhr), {}
                        )
                        DATAmodel_file = format_filler(
                            DATAmodel_file_template, valid_dt, init_dt,
                            str(fhr), {}
                        )
                        model_file_pairs_for_accum_list.append(
                            (COMINmodel_file, DATAmodel_file)
                        )
                        if fhr - int(accum) >= 0:
                            COMINmodel_file = format_filler(
                                COMINmodel_file_template, valid_dt, init_dt,
                                str(fhr - int(accum)), {}
                            )
                            DATAmodel_file = format_filler(
                                DATAmodel_file_template, valid_dt, init_dt,
                                str(fhr - int(accum)), {}
                            )
                            model_file_pairs_for_accum_list.append(
                                (COMINmodel_file, DATAmodel_file)
                            )
                    for model_file_pair in model_file_pairs_for_accum_list:
                        COMINmodel_file = model_file_pair[0]
                        DATAmodel_file = model_file_pair[1]
                        if not os.path.exists(DATAmodel_file):
                            if check_file(COMINmodel_file):
                                print(f"Linking {COMINmodel_file} to "
                                      +f"{DATAmodel_file}")
                                os.symlink(COMINmodel_file, DATAmodel_file)
                            else:
                                mail_COMINmodel_file = os.path.join(
                                    DATA, f"mail_{MODELNAME}_init"
                                    +f"{init_dt:%Y%m%d%H}_f{str(fhr).zfill(3)}"
                                    +f".sh"
                                )
                                print("MISSING or ZERO SIZE: "
                                      +f"{COMINmodel_file}")
                                print("Mail File: "
                                      +f"{mail_COMINmodel_file}")
                                if not os.path.exists(mail_COMINmodel_file):
                                    mailmsg = open(mail_COMINmodel_file, 'w')
                                    mailmsg.write('#!/bin/bash\n')
                                    mailmsg.write('set -x\n\n')
                                    mailmsg.write(
                                        'export subject="F'+str(fhr).zfill(3)
                                        +' '+MODELNAME.upper()+' Forecast '
                                        +'Data Missing for EVS '+COMPONENT
                                        +'"\n'
                                    )
                                    mailmsg.write(
                                        "export maillist=${maillist:-'"
                                        +USER.lower()+"@noaa.gov'}\n"
                                    )
                                    mailmsg.write(
                                        'echo "Warning: No '+MODELNAME.upper()
                                        +' was available for '
                                        +f'{init_dt:%Y%m%d%H}f'
                                        +f'{str(fhr).zfill(3)}" > mailmsg\n'
                                    )
                                    mailmsg.write(
                                        'echo "Missing file is '
                                        +COMINmodel_file+'" >> mailmsg\n'
                                    )
                                    mailmsg.write(
                                        'echo "Job ID: '+jobid+'" >> mailmsg\n'
                                    )
                                    mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                                    mailmsg.write('exit 0')
                                    mailmsg.close()
                                    os.chmod(mail_COMINmodel_file, 0o755)
        # OBS: Get CCPA files -- CONUS
        DATAccpa = os.path.join(DATA, 'data', 'ccpa')
        if not os.path.exists(DATAccpa):
            os.makedirs(DATAccpa)
            print(f"Making directory {DATAccpa}")
        print(f"\nGetting CCPA files for accumulation {accum}hr valid "
              +f"{accum_start_dt:%Y%m%d %H}Z to {accum_end_dt:%Y%m%d %H}Z")
        if accum == '24':
            ccpa_file_dt_in_accum_list = [
                accum_end_dt,
                accum_end_dt - datetime.timedelta(hours=6),
                accum_end_dt - datetime.timedelta(hours=12),
                accum_end_dt - datetime.timedelta(hours=18)
            ]
            ccpa_file_accum = '06'
        else:
            ccpa_file_dt_in_accum_list = [
                accum_end_dt
            ]
            ccpa_file_accum = accum
        for ccpa_file_dt_in_accum in ccpa_file_dt_in_accum_list:
            ccpa_file_HH = int(f"{ccpa_file_dt_in_accum:%H}")
            ccpa_file_YYYYmmdd = f"{ccpa_file_dt_in_accum:%Y%m%d}"
            if ccpa_file_HH > 0 and ccpa_file_HH <= 6:
                COMINccpa_file_dir = os.path.join(
                    COMINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '06'
                )
            elif ccpa_file_HH > 6 and ccpa_file_HH <= 12:
                COMINccpa_file_dir = os.path.join(
                    COMINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '12'
                )
            elif ccpa_file_HH > 12 and ccpa_file_HH <= 18:
                COMINccpa_file_dir = os.path.join(
                    COMINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '18'
                )
            elif ccpa_file_HH == 0:
                COMINccpa_file_dir = os.path.join(
                    COMINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '00'
                )
            else:
                COMINccpa_file_dir = os.path.join(
                    COMINccpa, 
                    ((ccpa_file_dt_in_accum+datetime.timedelta(days=1))\
                     .strptime('%Y%m%d')), '00'
                )
            COMINccpa_file = os.path.join(
                COMINccpa_file_dir,
                f"ccpa.t{str(ccpa_file_HH).zfill(2)}z."
                +f"{ccpa_file_accum}h.hrap.conus.gb2"
            )
            DATAccpa_file = os.path.join(
                DATAccpa, f"ccpa.accum{ccpa_file_accum}hr."
                +f"v{ccpa_file_dt_in_accum:%Y%m%d%H}"
            )
            if check_file(COMINccpa_file):
                print(f"Linking {COMINccpa_file} to {DATAccpa_file}")
                os.symlink(COMINccpa_file, DATAccpa_file)
            else:
                mail_COMINccpa_file = os.path.join(
                    DATA, f"mail_ccpa_accum{ccpa_file_accum}hr_"
                    +f"valid{ccpa_file_dt_in_accum:%Y%m%d%H}.sh"
                )
                print(f"MISSING or ZERO SIZE: {COMINccpa_file}")
                print(f"Mail File: {mail_COMINccpa_file}")
                if not os.path.exists(mail_COMINccpa_file):
                    mailmsg = open(mail_COMINccpa_file, 'w')
                    mailmsg.write('#!/bin/bash\n')
                    mailmsg.write('set -x\n\n')
                    mailmsg.write(
                        'export subject="CCPA Accum '+ccpa_file_accum+'hr '
                        +'Data Missing for EVS '+COMPONENT+'"\n'
                    )
                    mailmsg.write(
                        "export maillist=${maillist:-'"+USER.lower()
                        +"@noaa.gov'}\n"
                    )
                    mailmsg.write(
                        'echo "Warning: No CCPA accumulation '
                        +ccpa_file_accum+' hour data was available for '
                        +f'valid date {ccpa_file_dt_in_accum:%Y%m%d%H}" '
                        +'> mailmsg\n'
                    )
                    mailmsg.write(
                        'echo "Missing file is '+COMINccpa_file
                        +'" >> mailmsg\n'
                    )
                    mailmsg.write(
                         'echo "Job ID: '+jobid+'" >> mailmsg\n'
                    )
                    mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                    mailmsg.write('exit 0')
                    mailmsg.close()
                    os.chmod(mail_COMINccpa_file, 0o755)
        # OBS: Get MRMSE files -- Alaska
        DATAmrms = os.path.join(DATA, 'data', 'mrms')
        if not os.path.exists(DATAmrms):
            os.makedirs(DATAmrms)
            print(f"Making directory {DATAmrms}")
        for area in ['alaska']:
            print(f"\nGetting MRMS files for accumulation {accum}hr valid "
                  +f"{accum_start_dt:%Y%m%d %H} to {accum_end_dt:%Y%m%d %H}Z "
                  +f"over {area.title()}")
            COMINmrms_area = os.path.join(COMINmrms, area, 'MultiSensorQPE')
            COMINmrms_gzfile = os.path.join(
                COMINmrms, area, 'MultiSensorQPE',
                 f"MultiSensor_QPE_{accum}H_Pass2_00.00_"
                +f"{accum_end_dt:%Y%m%d}-{accum_end_dt:%H}0000.grib2.gz"
            )
            if check_file(COMINmrms_gzfile):
                DATAmrms_gzfile = os.path.join(
                    DATAmrms, COMINmrms_gzfile.rpartition('/')[2]
                )
                print(f"Copying {COMINmrms_gzfile} to "
                      +f"{DATAmrms_gzfile}")
                shutil.copy2(COMINmrms_gzfile, DATAmrms_gzfile)
                print(f"Unzipping {DATAmrms_gzfile}")
                os.system(f"gunzip {DATAmrms_gzfile}")
                DATAmrms_file = os.path.join(
                    DATAmrms, f"{area}_"
                    +(DATAmrms_gzfile.rpartition('/')[2]\
                      .replace('.gz', ''))
                )
                print("Moving "
                      +f"{DATAmrms_gzfile.replace('.gz', '')} "
                      +f"to {DATAmrms_file}")
                os.system("mv "
                         +f"{DATAmrms_gzfile.replace('.gz', '')} "
                         +f"{DATAmrms_file}")
            else:
                mail_COMINmrms_file = os.path.join(
                    DATA, f"mail_mrms_accum{accum}hr_{area}_"
                    +f"valid{accum_end_dt:%Y%m%d%H}.sh"
                )
                print(f"MISSING or ZERO SIZE: {COMINmrms_gzfile}")
                print(f"Mail File: {mail_COMINmrms_file}")
                if not os.path.exists(mail_COMINmrms_file):
                    mailmsg = open(mail_COMINmrms_file, 'w')
                    mailmsg.write('#!/bin/bash\n')
                    mailmsg.write('set -x\n\n')
                    mailmsg.write(
                        'export subject="MRMS '+area.title()+' Accum '
                        +accum+'hr Data Missing for EVS '
                        +COMPONENT+'"\n'
                    )
                    mailmsg.write(
                        "export maillist=${maillist:-'"+USER.lower()
                        +"@noaa.gov'}\n"
                    )
                    mailmsg.write(
                        'echo "Warning: No MRMS '+area.title()+' accumulation '
                        +accum+' hour data was available for valid date '
                        +f'{accum_end_dt:%Y%m%d%H}" '
                        +'> mailmsg\n'
                    )
                    mailmsg.write(
                        'echo "Missing file is '+COMINmrms_gzfile
                        +'" >> mailmsg\n'
                    )
                    mailmsg.write(
                         'echo "Job ID: '+jobid+'" >> mailmsg\n'
                    )
                    mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                    mailmsg.write('exit 0')
                    mailmsg.close()
                    os.chmod(mail_COMINmrms_file, 0o755)

print(f"END: {os.path.basename(__file__)}")
