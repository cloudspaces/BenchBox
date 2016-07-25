'''
Created on 25 de jul. de 2016

@author: Raul
'''
import os

def parse_sandbox_trace(input_file, output_dir, provider, stereotype):
    print "Parsing SANDBOX file: ", input_file    
    data_in = open(output_dir + provider + "-" + stereotype + "-data_in.dat", "w")
    data_out = open(output_dir + provider + "-" + stereotype + "-data_out.dat", "w")
    cpu_file = open(output_dir + provider + "-" + stereotype + "-cpu.dat", "w")
    disk_file = open(output_dir + provider + "-" + stereotype + "-disk.dat", "w")
    ram_file = open(output_dir + provider + "-" + stereotype + "-ram.dat", "w")
    
    first_line = True
    
    for l in open(input_file):
        name,time,bytes_recv,bytes_sent,client,cpu,credentials,data_rate_pack_down,data_rate_pack_up, \
            data_rate_size_down,data_rate_size_up,disk,dropin,dropout,errin,errout,files,hostname,meta_rate_pack_down, \
            meta_rate_pack_up,meta_rate_size_down,meta_rate_size_up,net,packets_recv,packets_sent,profile,ram,test_id = l[:-1].split(",")
            
        print name,time,bytes_recv,bytes_sent,client,cpu,credentials,data_rate_pack_down,data_rate_pack_up, \
            data_rate_size_down,data_rate_size_up,disk,dropin,dropout,errin,errout,files,hostname,meta_rate_pack_down, \
            meta_rate_pack_up,meta_rate_size_down,meta_rate_size_up,net,packets_recv,packets_sent,profile,ram,test_id
            
        if first_line:
            first_line = False 
            continue
            
        print >> data_in, time + '\t' +  bytes_recv  + '\t' + data_rate_pack_down + '\t' + data_rate_size_down  + '\t' + packets_recv
        print >> data_out, time + '\t' +  bytes_sent  + '\t' + data_rate_pack_up + '\t' + data_rate_size_up  + '\t' + packets_sent
        print >> cpu_file, time + '\t' +  cpu
        print >> disk_file, time + '\t' +  disk + '\t' +  files
        print >> ram_file, time + '\t' + ram        
        
    data_in.close()
    data_out.close()
    cpu_file.close()
    disk_file.close()
    ram_file.close()
    
    
def parse_benchbox_trace(input_file, output_dir, provider, stereotype): 
    print "Parsing BENCHBOX file: ", input_file    
    first_line = True
    
    per_operation_file = dict()
    for k in ["move", "sync", "upload", "download", "delete"]:    
        per_operation_file[k] = open(output_dir + provider + "-" + stereotype + "-" + k + ".dat", "w")
    
    for l in open(input_file):    
        print l[:-1].split(",")
        name, time, client, file_path, file_size, file_type, hostname, operation, profile, test_id = l[:-1].split(",")
        
        if first_line:
            first_line = False 
            continue
        
        for k in per_operation_file.keys():
            if k == operation:
                print >> per_operation_file[k], time + '\t' + file_size  + '\t1' 
            else:
                print >> per_operation_file[k], time + '\t0' + '\t0'
    
if __name__ == '__main__':
    
    output_dir = "./measurement_output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    
            
    parse_sandbox_trace("C://Users//Raul//Desktop//sandbox_workload_backup_occasional.csv", output_dir, "Dropbox", "backup-occasional")
    parse_benchbox_trace("C://Users//Raul//Desktop//benchbox_workload_backup_occasional.csv", output_dir, "Dropbox", "backup-occasional")
    
    