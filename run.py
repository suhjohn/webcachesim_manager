import subprocess
import re

hostnames = ["ssuh@clnode015.clemson.cloudlab.us"]
for hostname in hostnames:
    command = f"ssh {hostname} 'cat .bashrc'"
    bashrc_file = subprocess.check_output(command, shell=True, stderr=None).decode()
    lines = bashrc_file.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        if line.startswith("export PATH") and "/webcachesim" in line:
            command = f"ssh {hostname} 'sed -i '{i}s/.*/export PATH=$PATH:~/webcachesim/build/bin/' .bashrc'"
            subprocess.check_output(command, shell=True, stderr=None)
        elif line.startswith("export WEBCACHESIM_TRACE_DIR"):
            command = f"ssh {hostname} 'sed -i '{i}s/.*/export WEBCACHESIM_TRACE_DIR=/nfs' .bashrc'"
            subprocess.check_output(command, shell=True, stderr=None)
        elif line.startswith("export WEBCACHESIM_ROOT"):
            command = f"ssh {hostname} 'sed -i '{i}s/.*/export WEBCACHESIM_ROOT=~/webcachesim' .bashrc'"
            subprocess.check_output(command, shell=True, stderr=None)
            command = f"ssh {hostname} 'sed -i '{i+1}s/.*/export WEBCACHESIM_RESULT_DIR=/nfs/results' .bashrc'"
            subprocess.check_output(command, shell=True, stderr=None)
        else:
            pass
