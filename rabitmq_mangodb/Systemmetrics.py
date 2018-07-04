import psutil
import platform
import json
import cpuinfo
import socket
import netifaces as ni
import uuid
import ipaddress
import os
import struct
import time,datetime
import hashlib
import ConfigParser
from flask import Flask
app = Flask(__name__)

config_file_path = "/home/ec2-user/vamshi/Systemmetrics.conf"

byte_size = 1024

def initConfig():
	config = ConfigParser.ConfigParser()
	config.readfp(open(config_file_path))
	global interval, output_file_name
	interval = config.get('SYSCONF','DURATION')
	output_file_name = config.get('SYSCONF', 'OUTPUT_FILE_NAME')

def disk_Data():
	disk_Data = {}
	totalNumDisks = len(psutil.disk_partitions())
	Disk = psutil.disk_usage('/')
	disk_io_counters = psutil.disk_io_counters()
	totalDiskReadOpsPerSecond = disk_io_counters[0]
	totalDiskWriteOpsPerSecond = disk_io_counters[1]
	totalDiskBytesReadPerSecond = (disk_io_counters[2]*100)/(disk_io_counters[4]*byte_size)
	totalDiskBytesWrittenPerSecond = (disk_io_counters[3]*100)/(disk_io_counters[5]*byte_size)
	disk_Data['totalNumDisks'] = totalNumDisks
	disk_Data['totalDiskSize(GB)'] = Disk[0]/byte_size**3
	disk_Data['totalDiskFreeSize(GB)'] = Disk[2]/byte_size**3
	disk_Data['totalDiskBytesReadPerSecond(Kbps)'] = totalDiskBytesReadPerSecond
	disk_Data['totalDiskBytesWrittenPerSecond(Kbps)'] = totalDiskBytesWrittenPerSecond
	disk_Data['totalDiskReadOpsPerSecond'] = totalDiskReadOpsPerSecond
	disk_Data['totalDiskWriteOpsPerSecond'] = totalDiskWriteOpsPerSecond
	return disk_Data



def socket_constants(prefix):
    return dict((getattr(socket, n), n) for n in dir(socket) if n.startswith(prefix)) 

socket_families = socket_constants('AF_') 

def get_connections(connections):
        List_Of_Connections = []
        for con in connections:
                con_dict = {}
                con_dict['sourceIp'], con_dict['sourcePort']  =  (con.laddr.ip, con.laddr.port) if len(con.laddr) else (None, None)
                con_dict['destinationIp'],  con_dict['destinationPort'] = (con.raddr.ip, con.raddr.port) if len(con.raddr) else (None, None)
                con_dict['family'] = socket_families[con.family]
                List_Of_Connections.append(con_dict)
        return List_Of_Connections


def list_Of_Connections():
	connections = psutil.net_connections()
	return get_connections(connections)

def list_Of_tcpConnections():
        connections = psutil.net_connections(kind="tcp")
	return get_connections(connections)


def get_gateway():
    #Read the default gateway directly from /proc.
    with open("/proc/net/route") as fh:
       for line in fh:
            fields=line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_available_network_ips():
	con = psutil.net_if_addrs()
	List_Of_Ips = []
	for line in con:
		for ip in con[line]:
			try:
				con_dict = {}
				con_dict['ipAddress'] = ip.address
				con_dict['ipVersion'] = ipaddress.ip_address(unicode(ip.address)).version
				con_dict['netMask'] = ip.netmask
				List_Of_Ips.append(con_dict)
			except:
				pass
	return List_Of_Ips
			

def os_Data():
	os_Data = {}
	os_Data['osName'] = platform.platform()
	os_Data['osVersion'] = "-".join(platform.dist())
	return os_Data

def memory_Data():
	memory_Data = {}
	virtual_Memory = psutil.virtual_memory()
	memory_Data['totalRAM(MB)'] = virtual_Memory[0]/byte_size**2
	memory_Data['freeRAM(MB)'] = virtual_Memory[1]/byte_size**2
	return memory_Data

def cpu_Data():
	cpu_Data = {}
	cpu_Data['totalNumCpus'] = psutil.cpu_count(logical=False)
	cpu_Data['totalCpuUsagePct'] = psutil.cpu_percent()
	cpu_Data['cpuType'] = cpuinfo.get_cpu_info()['brand']
	cpu_Data['totalNumCores'] = cpuinfo.get_cpu_info()['count']
	cpu_Data['totalNumLogicalProcessors'] = psutil.cpu_count(logical=True)
	return cpu_Data

def network_Data():
	network_Data = {}
	network_Data['ip'] = get_available_network_ips()
	network_Data['totalNumNetworkCards'] = len(psutil.net_if_addrs())
	network_Data['Connections'] = list_Of_Connections()
	network_Data['totalNetworkBytesReadPerSecond(Kbps)'] = psutil.net_io_counters()[0]/byte_size
	network_Data['totalNetworkBytesWritePerSecond(Kbps)'] = psutil.net_io_counters()[1]/byte_size
	network_Data['hostName'] = socket.gethostname()
	network_Data['macAddress'] = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
	network_Data['gateway'] = get_gateway()
	network_Data['transprotProtocol'] = list_Of_tcpConnections()
	return network_Data


def get_available_network_ips():
        con = psutil.net_if_addrs()
        List_Of_Ips = []
        for line in con:
                for ip in con[line]:
                        try:
                                con_dict = {}
                                con_dict['ipAddress'] = ip.address
                                con_dict['ipVersion'] = ipaddress.ip_address(unicode(ip.address)).version
                                con_dict['netMask'] = ip.netmask
                                List_Of_Ips.append(con_dict)
                        except:
                                pass
        return List_Of_Ips


def os_Data():
        os_Data = {}
        os_Data['osName'] = platform.platform()
        os_Data['osVersion'] = "-".join(platform.dist())
        return os_Data

def memory_Data():
        memory_Data = {}
        virtual_Memory = psutil.virtual_memory()
        memory_Data['totalRAM(MB)'] = virtual_Memory[0]/byte_size**2
        memory_Data['freeRAM(MB)'] = virtual_Memory[1]/byte_size**2
        return memory_Data

def cpu_Data():
        cpu_Data = {}
        cpu_Data['totalNumCpus'] = psutil.cpu_count(logical=False)
        cpu_Data['totalCpuUsagePct'] = psutil.cpu_percent()
        cpu_Data['cpuType'] = cpuinfo.get_cpu_info()['brand']
        cpu_Data['totalNumCores'] = cpuinfo.get_cpu_info()['count']
        cpu_Data['totalNumLogicalProcessors'] = psutil.cpu_count(logical=True)
        return cpu_Data

def network_Data():
        network_Data = {}
        network_Data['ip'] = get_available_network_ips()
        network_Data['totalNumNetworkCards'] = len(psutil.net_if_addrs())
        network_Data['Connections'] = list_Of_Connections()
        network_Data['totalNetworkBytesReadPerSecond(Kbps)'] = psutil.net_io_counters()[0]/byte_size
        network_Data['totalNetworkBytesWritePerSecond(Kbps)'] = psutil.net_io_counters()[1]/byte_size
        network_Data['hostName'] = socket.gethostname()
        network_Data['macAddress'] = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        #network_Data['gateway'] = get_gateway()
        network_Data['transprotProtocol'] = list_Of_tcpConnections()
        return network_Data

@app.route('/systemmetrics')
def main():
        output = {}
        cmdLine = psutil.Process().cmdline()
        output['cmdLine'] = cmdLine
	output['path'] = os.getenv('PATH')
	output['Disk'] = disk_Data()
	output['Os'] = os_Data()
	output['Memory'] = memory_Data()
	output['Cpu'] = cpu_Data()
	output['Network'] = network_Data()
	output['agentId'] = hashlib.sha1(output['Network']['macAddress']).hexdigest()
	output['agentName'] = os.path.basename(__file__)
	output['agentProcessId'] = os.getpid()
	output['agentProvidedTime'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S %p')
	output['name'] = psutil.Process().name()
	output['isSystem'] = psutil.Process().username()=='root'
	return json.dumps(output)


if __name__ == '__main__':
	#import daemon
	initConfig()
	interval = int(interval)
	#with daemon.DaemonContext():	
		#while True:
	#output = main()
	#ff = open('/tmp/output_{0}.json'.format(time.time()), 'w')
	#ff.write(output)
	#ff.flush()
	#ff.close()
	##time.sleep(interval*60)
	app.run(port=8000)
