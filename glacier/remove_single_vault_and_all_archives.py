# call this script to begin a vault deletion

import subprocess, json, sys, os, glob, signal, threading
import inits
import aux
import get_vault_inventory as inventory

def delete_archives(account_id, vault_name, region):
  should_continue = input("aws results retrieved and stored in " + inventory.job_result_filename(vault_name, region) + " do you want to begin the deletion of the archives? [Y/N]: ")
  if should_continue.lower() == "y" or should_continue.lower() == "yes":
    result_file = open(inventory.job_result_filename(vault_name, region), "r")
    aws_results = json.loads(result_file.read())
    result_file.close()

    print("there are " + str(len(aws_results["ArchiveList"])) + " archives to be deleted: ")
    for archive in aws_results["ArchiveList"]:

      th = threading.Thread(target=delete_archive, args=(['aws', 'glacier', 'delete-archive', '--account-id', account_id, '--vault-name', vault_name, '--archive-id=\'' + archive["ArchiveId"] + '\''],))
      
      semaphore.acquire()
      th.start()
    print("\n")

    os.rename(inventory.job_tmp_filename(vault_name, region), inventory.job_tmp_filename(vault_name, region) + ".done")

    print("deletion completed, you can remove the vault after some time (aws needs some time to delete all the archives) from the console or calling this command")
    print("exec: aws glacier delete-vault --account-id " + account_id + " --vault-name " + vault_name)

def delete_archive(cmd):
    # print("exec: AWS_PAGER="" aws glacier delete-archive --account-id " + account_id + " --vault-name " + vault_name + " --archive-id='" + archive["ArchiveId"] + "'")
    subprocess.run(cmd, env=my_env)
    print('.', end='', flush=True)
    semaphore.release() 


########################################
# init
########################################

print("this script will delete all archives and the vault or resume a pending job, see glacier/README.md for further details how it works")
print("you can always abort the script running CTRL-C")

max_connections = 30

semaphore = threading.BoundedSemaphore(max_connections)

def exit_signal_handler(signal, frame):
        print('\nbye!')
        sys.exit(0)

signal.signal(signal.SIGINT, exit_signal_handler)

account_id, aws_region, region, my_env = inits.get_aws_config()

print("checking if there are current pending jobs...")
job_id, vault_name = inventory.check_pending_jobs(account_id)
if job_id != "":
  delete_archives(account_id, vault_name, region)
  sys.exit()

aux.print_vaults(account_id)

while True:
  vault_name = input("enter vault name to be deleted: ")

  if vault_name == "":
    print("please define a valid vault name...")
  else:
    break

inventory.init_inventory_job(account_id, vault_name, region)
