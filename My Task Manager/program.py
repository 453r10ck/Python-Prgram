from ast import arg
from pickletools import read_bytes1
import pandas as pd #used to sort by column
from datetime import datetime
import psutil
import time
import os

def get_process_info() :
    #the list contain all process dictionaries
    processes = []
    
    for process in psutil.process_iter():
        #---get the process id
        pid = process.pid
        if pid == 0:
            continue
        
        #---get the name of the file executed
        name = process.name
        
    #---time when the process was created
        try: 
            create_time = datetime.fromtimestamp(process.create_time())
        except OSError:
            create_time = datetime.fromtimestamp(psutil.boot_time())
            
    #---Get CPU usage
        try:
            #get the number of cpu cores
            cores = len(process.cpu_affinity())
        except psutil.AccessDenied:
            cores = 0
            
        cpu_usage = process.cpu_percent() 
            
    #---Get the status of the process (running, idle, etc.)
        status = process.status()
        
    #---Process Priority
        try:
            nice = int(process.nice())
        except psutil.AccessDenied:
            nice = 0
            
    #---Memory usage
        try:
            memory_usage = process.memory_full_info()
        except psutil.AccessDenied:
            memory_usage = 0
            
    #---Total written and read bytes by this process
        io_counters = process.io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes
        
    #---Total threads spawned
        # get the number of total threads spawned by this process
        n_threads = process.num_threads() 
        
    #---The user that spawned that process
        try:
            username = process.username()
        except psutil.AccessDenied:
            username = "N/A"
            
    #---Add all information in processes list
    processes.append({
            'pid': pid, 'name': name, 'create_time': create_time,
            'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
            'memory_usage': memory_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes,
            'n_threads': n_threads, 'username': username,
        })
    
    return processes

def construct_dataframe(processes):
    # Convert to pandas data frame
    df = pd.DataFrame(processes) # dict to data frame
    
    # set the process id as index of process
    df.set_index('pid',inplace=True)
    
    # sort by the column passed as argument
    df.sort_values(by='pid', inplace=True, ascending=False)
    
    # pretty priting bytes
    df['memory_usage'] = df['memory_usage'].apply(pd.get_size)
    df['write_bytes'] = df['write_bytes'].apply(pd.get_size)
    df['read_bytes'] = df['read_bytes'].apply(pd.get_size)
    
    #convert to proper date format
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    
    #reorder and define used column
    df = df[df.columns.split(",")]

    return df    
    
def get_size():
    #---Return size of bytes in a nice format
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Viewer & Monitor")
    parser.add_argument("-c", "--columns", help="""Columns to show,
                                                available are name,create_time,cores,cpu_usage,status,nice,memory_usage,read_bytes,write_bytes,n_threads,username.
                                                Default is name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores.""",
                        default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores")
    parser.add_argument("-s", "--sort-by", dest="sort_by", help="Column to sort by, default is memory_usage .", default="memory_usage")
    parser.add_argument("--descending", action="store_true", help="Whether to sort in descending order.")
    parser.add_argument("-n", help="Number of processes to show, will show all if 0 is specified, default is 25 .", default=25)
    parser.add_argument("-u", "--live-update", action="store_true", help="Whether to keep the program on and updating process information each second")

    # parse arguments
    args = parser.parse_args()
    columns = args.columns
    sort_by = args.sort_by
    descending = args.descending
    n = int(args.n)
    live_update = args.live_update







    
    
    
    
    
    
    