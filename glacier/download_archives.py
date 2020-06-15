# call this script to begin download of a vault
import subprocess, json, sys, os, glob, signal, threading
import inits
import aux
import get_vault_inventory as inventory

def select_what_download(account_id, vault_name, region):
  # create base vault download path
  path = os.path.join("downloads", vault_name)
  if not os.path.isdir(path):
    os.makedirs(path)

  while True:
    print("1. single archive")
    print("2. range of files from result set")
    print("3. all vault (all result set)")
    nr = input("select an action: ")

    if nr == "1":
      archive_id = input("provide archive id as present in the inventory list: ")
      archive_filename = input("provide archive filename as present in the inventory list: ")
      start_or_check_retrieval_job([{'archive_id': archive_id, 'archive_filename': archive_filename}])
    elif nr == "2":
      print("[TODO] retrieve range of files from inventory list (index_start, index_end)")
    elif nr == "3":
      print("[TODO] retrieve all archives present in inventory")
    else:
      print("value not recognized...try again")


def start_or_check_retrieval_job(archives):
 #  aws glacier initiate-job --account-id - --vault-name my-vault --job-parameters file://job-archive-retrieval.json
 #  job-archive-retrieval.json  is  a  JSON  file  in the local folder that
 #  specifies the type of job, archive ID, and some optional parameters:
 #   {
 #     "Type": "archive-retrieval",
 #     "ArchiveId": "kKB7ymWJVpPSwhGP6ycSOAekp9ZYe_--zM_mw6k76ZFGEIWQX-ybtRDvc2VkPSDtfKmQrj0IRQLSGsNuDp-AJVlu2ccmDSyDUmZwKbwbpAdGATGDiB3hHO0bjbGehXTcApVud_wyDw",
 #     "Description": "Retrieve archive on 2015-07-17",
 #     "SNSTopic": "arn:aws:sns:us-west-2:0123456789012:my-topic"
 #   }

  # to be fixed with batch download
  archive_id = archives[0]['archive_id']
  archive_filename = archives[0]['archive_filename']

  request_parameters = {
    "Type": "archive-retrieval",
    "ArchiveId": archive_id,
  }

  aws_job_response = json.loads(subprocess.run(['aws', 'glacier', 'initiate-job', '--account-id', account_id, '--vault-name', vault_name, '--job-parameters', json.dumps(request_parameters)], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

  job_id = aws_job_response["jobId"]

  job_file = open(aux.get_download_job_filename(vault_name, region, [archive_id]), "w")
  job_file.write({'job_id': job_id, 'archive_id': archive_id, 'archive_filename': archive_filename})
  job_file.close()

  print("job for vault " + vault_name + " initiated (job id: "  + job_id + "), job id stored in " + aux.get_download_job_filename(vault_name, region, [archive_id]))

def check_pending_jobs():
  jobs = glob.glob("jobs/*.download_job")

  for job_filename in jobs:
    answer = input("it seems that a download job is already running " + job_filename + " check the status? [y,n]: ")
    if answer.lower() == "y" or answer.lower() == "yes":
    
      file = open(job_filename, "r")
      data = file.read()
      print("file " + data)
      job = json.loads(data)
      file.close()

      found = False

      # print("exec: aws glacier list-jobs --account-id " + account_id + " --vault-name " + vault_name)
      aws_jobs = json.loads(subprocess.run(['aws', 'glacier', 'list-jobs', '--account-id', account_id, '--vault-name', vault_name], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

      for aws_job in aws_jobs["JobList"]:
        if aws_job["JobId"] != job["job_id"]:
          continue

        found = True
        if aws_job["StatusCode"] == "InProgress":
          print("the jobs is still running...")
          break

        if aws_job["StatusCode"] == "Failed":
          print("the job has failed!")
          break

        if aws_job["StatusCode"] == "Succeeded":
          should_continue = input("the job is successfully finished, do you want to download the archive(s) present in the jobs? [Y/N]: ")
          if should_continue.lower() == "y" or should_continue.lower() == "yes":
            download_single_archive(job_id, job)
            print("download done, exiting...")
            sys.exit(0)
      
      if found == False:
        print("job not found, probably expired! You have to request it again")

def download_single_archive(job_id, job):
  print("start download request for archive_id:", job["archive_id"])

  subprocess.run(['aws', 'glacier', 'get-job-output', '--account-id', account_id, '--vault-name', vault_name, '--job-id', job["job_id"], aux.get_download_archive_id(vault_name, job["job_id"])])


########################################
# init
########################################

print("script still work-in-progress!!")

print("this script will start the download of the archives of a given vault or resume a pending job, see glacier/README.md for further details how it works")
print("you can always abort the script running CTRL-C")

def exit_signal_handler(signal, frame):
        print('\nbye!')
        sys.exit(0)

signal.signal(signal.SIGINT, exit_signal_handler)

account_id, aws_region, region, my_env = inits.get_aws_config()

print("checking if there are current download pending jobs...")


check_pending_jobs()

### to be removed
select_what_download(account_id, "roots-docs", region)
###


print("checking if there are other pending jobs...")
job_id, vault_name = inventory.check_pending_jobs(account_id)
if job_id != "":
  select_what_download(account_id, vault_name, region)
  sys.exit()

aux.print_vaults(account_id)

while True:
  vault_name = input("enter vault name to start download: ")

  if vault_name == "":
    print("please define a valid vault name...")
  else:
    break

print("no inventory present yet...init new inventory retrieval")
inventory.init_inventory_job(account_id, vault_name, region)