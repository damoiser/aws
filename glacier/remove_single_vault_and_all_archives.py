
import subprocess

print("THIS SCRIPT IS STILL IN WORK IN PROGRESS - DONT USE IT YET")

print("this script will delete all archives and the vault, see glacier/README.md for further details how it works")


account_id = input("enter account id (blank if same as configured in aws): ")
if account_id == "":
  # if using the default one use dash
  account_id = "-"


aws_vaults = subprocess.run(['aws', 'glacier', 'list-vaults', '--account-id', account_id], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')


while True:
  vault_name = input("enter vault name: ")

  if vault_name == "":
    print("please define a valid vault name...")
  else:
    break


aws_region = subprocess.run(['aws', 'configure', 'get', 'region'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')

region = input("enter region (blank for " + aws_region + "): ")

if region == "":
  region = aws_region





# main processes

def init_inventory_job(account_id, vault_name, region):
  print("starting init inventory job, after the initialization you need to wait some hours to wait that AWS finish the job, you can rerun the job to check the status")
  subprocess.run(['aws', 'glacier', 'initiate-job', '--job-parameters', '\'{"Type": "inventory-retrieval"}\'', '--vault-name', vault_name, '--account-id', account_id, '--region', region])

def get_inventory_result(vault_name, region):


def delete_archives():

# aux functions

def job_tmp_filename(vault_name, region):
  return str(region) + "_" + str(vault_name) + ".job"

def job_result_filename(vault_name, region, job_id):
  return str(region) + "_" + str(vault_name) + "_" + str(job_id) + ".json"

def get_job_id_from_file(vault_name, region):
  
def is_job_finished(account_id, vault_name):
