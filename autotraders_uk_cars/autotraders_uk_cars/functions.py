# Used for Timezone / Datetime
from datetime import datetime
from datetime import datetime, date, timedelta

import string
import random
import autotraders_uk_cars.constants as constants
import datetime
import os
import csv
import random
import time

#Used for  Path (File Handling, Folders)
from pathlib import Path

def current_date():

    current_date=date.today()
    return current_date

def current_date_time():

    current_date_time=format(datetime.datetime.now(),constants.datetime_format)
    return current_date_time

def display_date_time(date_text):
    req_format = constants.datetime_format

    dt=format(date_text,req_format)
    return dt


def find_str(full, sub):
    index = 0
    sub_index = 0
    position = -1
    for ch_i,ch_f in enumerate(full) :
        if ch_f.lower() != sub[sub_index].lower():
            position = -1
            sub_index = 0
        if ch_f.lower() == sub[sub_index].lower():
            if sub_index == 0 :
                position = ch_i

            if (len(sub) - 1) <= sub_index :
                break
            else:
                sub_index += 1

    return position



#=========================================== Error Logs ===========================================
log_dir_path=os.path.join(Path().absolute().parent.parent,'log/error_logs')

def write_log_file(sel_text):
    log_file_name=str(current_date()) + '.log'
    log_file_path=os.path.join(log_dir_path,log_file_name)
    sel_file = log_file_path

    if sel_file is not None:
        

        file=open(sel_file,"a+")
       
            
        if sel_text is not None:
            file.write('\n')
            file.write(sel_text)
            file.close()
    return True

 
#=========================================== Error Logs ===========================================