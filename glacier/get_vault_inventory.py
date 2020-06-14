# functions used in others scripts to start / get the inventory

import subprocess, json, glob, os
import aux

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
      region = job_file.split("__")[0].split("/")[1]
      vault_name = job_file.split("__")[1].split(".job")[0]

      file = open(job_file, "r")
      job_id = file.read()
      file.close()

      should_continue = input("do you want to check the status for region " + region + " vault name " + vault_name + " and job id " + job_id + "? [Y/N]: ")
      if should_continue.lower() == "y" or should_continue.lower() == "yes":

        # print("exec: aws glacier list-jobs --account-id " + account_id + " --vault-name " + vault_name)
        aws_jobs = json.loads(subprocess.run(['aws', 'glacier', 'list-jobs', '--account-id', account_id, '--vault-name', vault_name], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

        found = False

        for aws_job in aws_jobs["JobList"]:
          if aws_job["JobId"] != job_id:
            continue

          found = True
          if aws_job["StatusCode"] == "InProgress":
            print("the jobs is still running...")
            break

          if aws_job["StatusCode"] == "Failed":
            print("the job has failed!")
            break

          if aws_job["StatusCode"] == "Succeeded":
            should_continue = input("the job is successfully finished, do you want to retrieve the results? [Y/N]: ")
            if should_continue.lower() == "y" or should_continue.lower() == "yes":
              get_inventory_result(account_id, vault_name, region, job_id)
              return str(job_id), vault_name
            break
        
        if found == False:
          print("job not found, probably expired! You have to request it again")
      else:
        print("don't continue with current jobs")

  else:
    print("no pending jobs found")
  
  return "", ""

def get_inventory_result(account_id, vault_name, region, job_id):
  print("getting inventory results...")
  print("exec: AWS_PAGER=\"\" aws glacier get-job-output --account-id " + account_id + " --vault-name " + vault_name + " --job-id " + job_id + " " + job_result_filename(vault_name, region))
  subprocess.run(['aws', 'glacier', 'get-job-output', '--account-id', account_id, '--vault-name', vault_name, '--job-id', job_id, job_result_filename(vault_name, region)], env=my_env)

def job_tmp_filename(vault_name, region):
  return "jobs/" + str(region) + "__" + str(vault_name) + ".job"

def job_result_filename(vault_name, region):
  return "jobs/results_" + str(region) + "__" + str(vault_name) + ".json"

my_env = os.environ.copy()
my_env["AWS_PAGER"] = ""
