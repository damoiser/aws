# call this script to begin download of a vault
import subprocess, json, sys, os, glob, signal, threading
import inits
import aux
import get_vault_inventory as inventory

def select_what_download(account_id, vault_name, region):
  print("decide what to download:")
  print("0. get inventory list [if not yet done]")
  print("1. single archive")
  print("2. range of files from result set")
  print("3. all vault (all result set)")
  nr = input("Put a number")


  while True:
    if nr == "0":
      job_id, _ = inventory.check_pending_jobs(account_id)

      if job_id == "":
        answer = input("do you want")
      inventory.init_inventory_job(account_id, vault_name, region)
      sys.exit()
    elif nr == "1":
    elif nr == "2":
    elif nr == "3":
    else:


def download_single_archive(archive_id)
"""   aws glacier initiate-job --account-id - --vault-name my-vault --job-parameters file://job-archive-retrieval.json

  job-archive-retrieval.json  is  a  JSON  file  in the local folder that
  specifies the type of job, archive ID, and some optional parameters:

    {
      "Type": "archive-retrieval",
      "ArchiveId": "kKB7ymWJVpPSwhGP6ycSOAekp9ZYe_--zM_mw6k76ZFGEIWQX-ybtRDvc2VkPSDtfKmQrj0IRQLSGsNuDp-AJVlu2ccmDSyDUmZwKbwbpAdGATGDiB3hHO0bjbGehXTcApVud_wyDw",
      "Description": "Retrieve archive on 2015-07-17",
      "SNSTopic": "arn:aws:sns:us-west-2:0123456789012:my-topic"
    } """

  request_parameters = {
    "Type": "archive-retrieval",
    "ArchiveId": archive_id,
  }

  aws_job_response = json.loads(subprocess.run(['aws', 'glacier', 'initiate-job', '--account-id', account_id, '--vault-name', vault_name, '--job-parameters', json.dumps(request_parameters), job_result_filename(vault_name, region)], , stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')))
  
  job_id = aws_job_response["jobId"]

  print("job for vault " + vault_name + " initiated (job id: "  + job_id + "), job id stored in " + job_tmp_filename(vault_name, region))

  job_file = open(job_tmp_filename(vault_name, region), "w")
  job_file.write(job_id)
  job_file.close()

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

print("checking if there are current pending jobs...")
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
