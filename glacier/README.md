# Glacier

### Remove single vault and all archives

It deletes a single vault and all the archives, it works as follow:

1. run ```python3 remove_single_vault_and_all_archives.py```: it starts a job on AWS to retrieve all the archives, it stores a ```*.job``` file to be able to proceed on the next steps
2. AWS needs **some hours** to end the job
3. re-run ```python3 remove_single_vault_and_all_archives.py```: it will check if the job is already done or not, if yes, it will retrieve the job results
4. request the result of the job using the ```*.job``` file created in (1.); it stores the job results in the ```*.json``` file
5. delete all the archives
6. delete the vault