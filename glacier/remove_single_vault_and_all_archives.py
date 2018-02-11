
import subprocess, json, sys, os, glob, signal

########################################
# functions
########################################

# MAIN FUNCS

def init_inventory_job(account_id, vault_name, region):
  print("starting init inventory job, after the initialization you need to wait some hours to wait that AWS finish the job, you can rerun the job to check the status")
  print("exec: aws glacier initiate-job --job-parameters {\"Type\": \"inventory-retrieval\"} --account-id " + account_id + " --vault-name " + vault_name)
  aws_job_response = json.loads(subprocess.run(['aws', 'glacier', 'initiate-job', '--job-parameters', '{"Type": "inventory-retrieval"}', '--vault-name', vault_name, '--account-id', account_id, '--region', region], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

  job_id = aws_job_response["jobId"]

  print("job for vault " + vault_name + " initiated (job id: "  + job_id + "), job id stored in " + job_tmp_filename(vault_name, region))

  job_file = open(job_tmp_filename(vault_name, region), "w")
  job_file.write(job_id)
  job_file.close()


def check_pending_jobs(account_id):
  print("checking pending jobs...")

  job_files = glob.glob("jobs/*.job")
  if len(job_files) > 0:
    print("there are " + str(len(job_files)) + " pending job(s)")

    for job_file in job_files:
      region = job_file.split("__")[0]
      vault_name = job_file.split("__")[1].split(".job")[0]

      file = open(job_file, "r")
      job_id = file.read()
      file.close()

      should_continue = input("do you want to check the status for region " + region + " vault name " + vault_name + " and job id " + job_id + "? [Y/N]: ")
      if should_continue.lower() == "y" or should_continue.lower() == "yes":

        print("exec: aws glacier list-jobs --account-id " + account_id + " --vault-name " + vault_name)
        aws_jobs = json.loads(subprocess.run(['aws', 'glacier', 'list-jobs', '--account-id', account_id, '--vault-name', vault_name], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

        for aws_job in aws_jobs["JobList"]:
          if aws_job["JobId"] != job_id:
            continue

          if aws_job["StatusCode"] == "InProgress":
            print("the jobs is still running...")
            break

          if aws_job["StatusCode"] == "Failed":
            print("the job has failed!")
            break

          if aws_job["StatusCode"] == "Succeeded":
            should_continue = input("the job is successfully finished, do you want to retrieve the results? [Y/N]: ")
            if should_continue.lower() == "y" or should_continue.lower() == "yes":
              get_inventory_result(account_id, vault_name, region)
            break
  else:
    print("no pending jobs found")

def get_inventory_result(account_id, vault_name, region):
  print("getting inventory results...")
  print("exec: aws glacier get-job-output --account-id " + account_id + " --vault-name " + vault_name + " " + job_result_filename(vault_name, region))
  subprocess.run(['aws', 'glacier', 'get-job-output', '--account-id', account_id, '--vault-name', vault_name, job_result_filename(vault_name, region)])

  should_continue = ("aws results retrieved and stored in " + job_result_filename(vault_name, region), " do you want to begin the deletion of the archives? [Y/N]: ")
  if should_continue.lower() == "y" or should_continue.lower() == "yes":
    delete_archives(account_id, vault_name, region)

def delete_archives(account_id, vault_name, region):
  result_file = open(job_result_filename(vault_name, region), "r")
  aws_results = result_file.read()
  result_file.close()

  print("there are " + str(len(aws_results["ArchiveList"])) + " archives to be deleted: ")
  for archive in aws_results["ArchiveList"]:
    subprocess.run(['aws', 'glacier', 'delete-archive', '--account-id', account_id, '--vault-name', vault_name, '--archive-id', archive["ArchiveId"]])
    print('.', end='', flush=True)

  os.rename(job_tmp_filename(vault_name, region), job_tmp_filename(vault_name, region) + ".done")

  should_continue = input("archives deletion completed, do you want to remove the vault " + vault_name + "? [Y/N]: ")
  if should_continue.lower() == "y" or should_continue.lower() == "yes":
    print("exec: aws glacier delete-vault --account-id " + account_id + " --vault-name " + vault_name)
    subprocess.run(['aws', 'glacier', 'delete-vault', '--account-id', account_id, '--vault-name'])

# AUX FUNCS

def create_dir_structure():
  if not os.path.exists("jobs"):
    os.makedirs("jobs")

def job_tmp_filename(vault_name, region):
  return "jobs/" + str(region) + "__" + str(vault_name) + ".job"

def job_result_filename(vault_name, region):
  return "jobs/results_" + str(region) + "__" + str(vault_name) + ".json"

def print_vaults(account_id):
  aws_vaults_json = json.loads(subprocess.run(['aws', 'glacier', 'list-vaults', '--account-id', account_id], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

  if "VaultList" in aws_vaults_json.keys():
    vaults = []

    print("there are " + str(len(aws_vaults_json["VaultList"])) + " available vault(s)")

    for vault in aws_vaults_json["VaultList"]:
      print("* " + vault["VaultName"])

  else:
    print("cannot get all vaults")
    sys.exit()


########################################
# init
########################################

print("THIS SCRIPT IS STILL IN WORK IN PROGRESS - DONT USE IT YET")

print("this script will delete all archives and the vault or resume a pending job, see glacier/README.md for further details how it works")
print("you can always abort the script running CTRL-C")

create_dir_structure()

def exit_signal_handler(signal, frame):
        print('\nbye!')
        sys.exit(0)

signal.signal(signal.SIGINT, exit_signal_handler)

account_id = input("enter account id (blank if same as configured in aws): ")
if account_id == "":
  # if using the default one use dash
  account_id = "-"

aws_region = subprocess.run(['aws', 'configure', 'get', 'region'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')

region = input("enter region (blank for " + aws_region + "): ")

if region == "":
  region = aws_region

print("checking if there are current pending jobs...")
check_pending_jobs(account_id)

print_vaults(account_id)

while True:
  vault_name = input("enter vault name to be deleted: ")

  if vault_name == "":
    print("please define a valid vault name...")
  else:
    break

init_inventory_job(account_id, vault_name, region)
