from paramiko import SSHClient
import subprocess, time, os, sys
import datetime
import shlex
# reusable function to run cmd, pipe stdout to console
# and return std out back for error checking
def run_cmd(cmd):
    p = subprocess.Popen(cmd,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
    output = ""
    while True:
        line = p.stdout.readline().decode(encoding='UTF-8')
        if not line:
            break
        print (line.strip())
        output = output + line
    return output

# Variables for Virtual box
vm_manager = "VboxManage"
vm_start_cmd = "startvm"
vm_list = "list"
vm_runningvms = "runningvms"
vm_control_cmd = "controlvm"
vm_safe_poweroff = "acpipowerbutton"
vm_win_1 = "winVM764_1"

vm_work_drive = "c:"
guest_path = 'c:/work'
file_list = sys.argv[1:]


#file_list = [s for s in os.listdir(host_path) if s.endswith('.raw')]
#print file_list

msconvert_path = "c:\Program Files\ProteoWizard\ProteoWizard 3.0.11392\msconvert.exe"

cmd_mnt_folder = [vm_manager, 'sharedfolder', 'add', vm_win_1, '--name', 'work',
                  '-hostpath', '/Users/mfreitas/Downloads/Samples', '-transient','-automount']
cmd_run = [vm_manager, 'guestcontrol', vm_win_1, 'run' , '--username',
           'wincompute', '--password', 'histone1234', '--verbose', '--exe']
cmd_mkdir = [vm_manager, 'guestcontrol', vm_win_1, 'mkdir' , '--username',
             'wincompute', '--password', 'histone1234','--parents']
cmd_rmdir = [vm_manager, 'guestcontrol', vm_win_1, 'rmdir' , '--username',
             'wincompute', '--password', 'histone1234','--recursive']

cmd_copyto = [vm_manager, 'guestcontrol', vm_win_1, 'copyto' , '--username',
              'wincompute', '--password', 'histone1234']
cmd_copyfrom = [vm_manager, 'guestcontrol', vm_win_1, 'copyfrom' , '--username',
              'wincompute', '--password', 'histone1234']
cmd_vm_is_running = [vm_manager, vm_list, vm_runningvms]
cmd_vm_start = [vm_manager, vm_start_cmd, vm_win_1]
cmd_vm_power_off = [vm_manager, vm_control_cmd, vm_win_1, vm_safe_poweroff]



#cmd_tmp = cmd_run + ["c:\\windows\\system32\\WindowsPowerShell\\v1.0\powershell.exe" , '--','cmd/arg0','-inputformat', 'none','cd','c:\\work',';','dir',';','copy','test.txt','test.txt2',';','dir']
#print cmd_tmp
#output = run_cmd(cmd_tmp)


#cmd_tmp = cmd_copyfrom + [ '--target-directory', '/Users/mfreitas/Desktop/test.txt','c:\\work\\test.txt']
#print cmd_tmp
#output = run_cmd(cmd_tmp)


#Check to see if the VM is already running
output = run_cmd(cmd_vm_is_running)

if vm_win_1 not in output:
    print ("Starting VM")

    cmd_vm_setup = [vm_manager, "modifyvm", vm_win_1, "--memory", "8192"]
    output = run_cmd(cmd_vm_setup)

    output = run_cmd(cmd_vm_start)
    # wait for start
    # Add some more intelligent checking here.
    time.sleep(120)

else:
    print ("VM Already running")

print(file_list)

for file in file_list:
    timestamp = '{:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now())
    print ("remote work job =",timestamp)

    tmp_dir = os.path.join(guest_path ,timestamp)

    cmd_tmp = cmd_mkdir + [tmp_dir]
    output = run_cmd(cmd_tmp)

    host_file = os.path.abspath(file)
    file_name = os.path.basename(host_file)
    file_dir = os.path.dirname(host_file)
    guest_file = os.path.join(tmp_dir,file_name)
    print(host_file,file_dir,file_name,guest_file)


    print ("copying " + host_file + " to VM")
    cmd_tmp = cmd_copyto + ['--target-directory' , tmp_dir, host_file]
    output = run_cmd(cmd_tmp)


    print( "running msconvert ")
    cmd_tmp = cmd_run + [msconvert_path] + ['--'] + ['msconvert/arg0', '--outdir', tmp_dir.replace('/','\\'), '-v', '--mzML',  '--filter', '\"peakPicking true 1-\"', guest_file.replace('/','\\')]
#    cmd_tmp = cmd_run + [msconvert_path] + ['--'] + ['msconvert/arg0', '--outdir', tmp_dir.replace('/','\\'), '-v', '--filter', '\"peakPicking true 1-\"', '--filter', '\"zeroSamples removeExtra\"', guest_file.replace('/','\\')]
#    cmd_tmp = cmd_run + [msconvert_path] + ['--'] + ['msconvert/arg0', '--outdir', tmp_dir.replace('/','\\'), '-v', guest_file.replace('/','\\')]
    output = run_cmd(cmd_tmp)
    print ( guest_file)
    guest_dirname = os.path.dirname(guest_file)
    guest_basename = os.path.basename(guest_file)
    gbase,gext = os.path.splitext(guest_basename)
    gfile = gbase+".mzML"
    guest_mzML = os.path.join(guest_dirname,gfile)
    host_mzML = os.path.join(file_dir,gfile)
    print ("copying " + guest_mzML.replace('/','\\') + " to host")

    cmd_tmp = cmd_copyfrom + ['--target-directory' , host_mzML,  guest_mzML.replace('/','\\')]
    print(cmd_tmp)
    output = run_cmd(cmd_tmp)

    print( "removing temp work directory from VM")

    cmd_tmp = cmd_rmdir + [tmp_dir]
    output = run_cmd(cmd_tmp)




#power off VM
#check if other guestcontrol processes are running
#If yes then exit and leave VM running

# If no the close VM
#output = run_cmd(cmd_vm_power_off)
#ime.sleep(0)
#check for vm shutdown
#output = run_cmd(cmd_vm_is_running)
#Exit when VM has closed

#Consider adding a lock file to the vm indicating if another process is using the VM.
