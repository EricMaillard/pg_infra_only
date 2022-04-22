# pg_infra_only
Batch program to extract list of process candidate to full stack

Pre-requesites : have Python 3.8 (or loater) installed on your environment.
Install the "requests" module in you Python environment:
pip install requests

To use the program, edit the setting.json file.
Into the json file, you first have to set up the dynatrace tenant url:
"dynatrace_server_url":

Managed	https://{your-domain}/e/{your-environment-id}

SaaS	https://{your-environment-id}.live.dynatrace.com

Then, you have to set an API token with Read entities (entities.read) scope

If the management_zone field is empty, the batch will collect all the tenant hosts. If a management_name is specified, only the hosts of this management zone will be analyzed.

If your tenant is in managed mode, and you want to access through mission control, then do that setup:
	"use_via_mission_control" : true,
	"X-CSRFToken" : "",
	"Cookie" : "",

You can find X-CSRFToken and Cookie in the WebUI of Dynatrace. You go to developer mode, look at network, and gets the details of status request to Dynatrace server. You copy/paste X-CSRFToken and Cookie to the settings.json file. It will be valide for an hour.

Then, to run the batch, launch the command:

python python infra_only_host_FSCandidate.py .

It will use the setting.json file that is in your current directory.
The batch creates a file named : infra_only_host_FSCandidate.csv
In case of trouble, look at the log file infra_only_host_FSCandidate.log
