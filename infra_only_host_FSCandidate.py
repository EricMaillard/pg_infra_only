import csv
import os
import sys
import commons
from concurrent.futures import ThreadPoolExecutor
import threading
from inspect import currentframe, getframeinfo
import datetime
from datetime import timedelta
import traceback

API_ENDPOINT_ENTITIES="/api/v2/entities"

# set up logging #####################################
import sys,logging,logging.handlers,os.path
#in this particular case, argv[0] is likely pythonservice.exe deep in python's lib\
# so it makes no sense to write log there
log_file="infra_only_host_FSCandidate.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
f = logging.Formatter(u"%(asctime)s %(levelname)-8s %(message)s")
h=logging.StreamHandler(sys.stdout)
h.setLevel(logging.NOTSET)
h.setFormatter(f)
logger.addHandler(h)
h=logging.handlers.RotatingFileHandler(log_file,maxBytes=1024**2,backupCount=1)
h.setLevel(logging.NOTSET)
h.setFormatter(f)
logger.addHandler(h)
del h,f
#hook to log unhandled exceptions
def excepthook(type,value,_traceback):
    logger.error("Unhandled exception occured",exc_info=(type,value,_traceback))
    #Don't need another copy of traceback on stderr
    if old_excepthook!=sys.__excepthook__:
        old_excepthook(type,value,_traceback)
old_excepthook = sys.excepthook
sys.excepthook = excepthook
del log_file
# ####################################################

lock = threading.Lock()
infrahost_counter = 0
fshost_counter = 0
monitoring_candidate_counter = 0
no_mode_counter = 0
fullstack_process_counter = 0
fullstack_candidate_process_counter = 0
# get the list of host that belong to the given management zone
def getHostList(mzName):
    uri = commons.settings['dynatrace_server_url'] + API_ENDPOINT_ENTITIES
    if mzName is not None and len(mzName) > 0:
        params = '&entitySelector=type(\"HOST\"),mzName(\"'+mzName+'\")&fields=+properties.monitoringMode,+properties.osType,+properties.isMonitoringCandidate'+fromtoQueryString
    else:
        params = '&entitySelector=type(\"HOST\")&fields=+properties.monitoringMode,+properties.osType,+properties.isMonitoringCandidate'+fromtoQueryString
    return commons.dynatrace_get_with_next_page_key(uri, params, 'entities')

def computeHost(host):
    global infrahost_counter
    global fshost_counter
    global monitoring_candidate_counter
    global no_mode_counter
    global fullstack_process_counter
    global fullstack_candidate_process_counter
    try:
        hostid = host['entityId']
        hostname = host['displayName']
        osType = host.get('properties').get('osType')
        monitoringMode = host.get('properties').get('monitoringMode')
        if osType == 'ZOS':
            return
        uri = commons.settings['dynatrace_server_url'] + API_ENDPOINT_ENTITIES
        params = '&entitySelector=type(\"PROCESS_GROUP_INSTANCE\"),fromRelationships.isProcessOf(type(\"HOST\"),entityId(\"'+hostid+'\"))&fields=+properties.softwareTechnologies'
        pgis = commons.dynatrace_get_with_next_page_key(uri, params, 'entities')
        lock.acquire()
        logger.debug("Host name = "+hostname)
        logger.debug("Host entityId = "+hostid)
        logger.debug("Host osType = "+osType)
        if monitoringMode != None:
            if monitoringMode == 'INFRASTRUCTURE':
                infrahost_counter = infrahost_counter + 1
            else:
                fshost_counter = fshost_counter + 1
            logger.debug("Host monitoringMode = "+monitoringMode)
        else:
            isMonitoringCandidate = host.get('properties').get('isMonitoringCandidate')
            if isMonitoringCandidate and isMonitoringCandidate == True:
                monitoring_candidate_counter = monitoring_candidate_counter + 1
                monitoringMode = 'None'
            else:
                logger.info("Host monitoringMode = None for hostname and not a monitoring candidate = "+hostname+" hostid = "+hostid)
                monitoringMode = 'None'
                no_mode_counter = no_mode_counter + 1
        for pgi in pgis:
            if 'OneAgent' in pgi.get('displayName'):
                continue
            if 'Short-lived processes' in pgi.get('displayName'):
                continue
            softwareTechnologies = pgi.get('properties').get('softwareTechnologies')
            if softwareTechnologies:
                for softwareTechnology in softwareTechnologies:
                    type = softwareTechnology.get('type')
                    if type and type in commons.settings['full_stack_processes_types']:
                        logger.debug('FS pgi name = '+pgi.get('displayName'))
                        logger.debug('Main techno = '+type)
                        logger.debug('softwareTechnologies = '+str(softwareTechnologies))
                        if monitoringMode == 'INFRASTRUCTURE':
                            fullstack_candidate_process_counter = fullstack_candidate_process_counter + 1
                        elif monitoringMode == 'FULL_STACK':
                            fullstack_process_counter = fullstack_process_counter + 1
                        writer = host.get('writer')
                        writer.writerow((hostname,
                                hostid,
                                osType,
                                monitoringMode,
                                pgi.get('displayName'),
                                type,
                                str(softwareTechnologies)))
                        break
        print("\r %d/%d" % (host.get('cnt'), host.get('total')), end = '')
        lock.release()
    except Exception as e:
        lock.release()
        logger.error(e)
        logger.error(traceback.format_exc())

def main(argv):
    global infrahost_counter
    global fshost_counter
    global monitoring_candidate_counter
    global no_mode_counter
    global fullstack_process_counter
    global fullstack_candidate_process_counter
    config_file_path = argv[0]
    commons.load_settings(config_file_path)

    log_level = commons.settings['log_level']
    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level == 'ERROR':
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.ERROR)
        logger.error("invalid log level in settings.json file. Should be DEBUG, INFO or ERROR, found "+log_level)

    global fromtoQueryString
    fromtoQueryString = "&from=now-24h"

    starttime = datetime.datetime.utcnow()

    infrahost_counter = 0
    fshost_counter = 0
    monitoring_candidate_counter = 0
    no_mode_counter = 0
    fullstack_process_counter = 0
    fullstack_candidate_process_counter = 0

    #get host details
    #uri = commons.settings['dynatrace_server_url'] + API_ENDPOINT_ENTITIES + '/HOST-FFF9F08BAAF381B2'
    #returned = commons.dynatrace_get(uri, None)
    #logger.info(returned)

    hosts = getHostList(commons.settings['management_zone'])
    #logger.info(str(hosts))
 
    filename = "infra_only_host_FSCandidate.csv"
    file = open(filename, "w", newline='', encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow( ('host_name', 'host_id', 'os_type', 'monitoring_mode', 'pgi_name', 'main_technotechnology', 'technologies') )

    cnt = 0
    for host in hosts:
        host['writer'] = writer
        host['cnt'] = cnt
        host['total'] = len(hosts)
        cnt = cnt + 1
    #max_workers = commons.settings['number_of_workers']
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(computeHost, hosts)                        

    file.close()
    print('')
    print('Total Number of hosts = '+str(len(hosts)))
    print('Number of full stack hosts = '+str(fshost_counter))
    print('Number of infra only hosts = '+str(infrahost_counter))
    print('Number of monitoring candidates  = '+str(monitoring_candidate_counter))
    if no_mode_counter != 0:
        print('Number of hosts with no monitoring mode  = '+str(no_mode_counter))
    print('Number of fullstack processes = '+str(fullstack_process_counter))
    print('Number of fullstack candidate processes = '+str(fullstack_candidate_process_counter))
    endtime = datetime.datetime.utcnow()
    delta = endtime - starttime
    millis = delta.total_seconds() * 1000
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    print("Duration to compute "+str(len(hosts))+" hosts = "+"%dh, %dmn, %ds" % (hours, minutes, seconds))

if __name__ == '__main__':
    main(sys.argv[1:])
