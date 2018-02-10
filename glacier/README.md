# Glacier

### Remove single vault and all archives

It deletes a single vault and all the archives, it works as follow:

1. start a job on AWS to retrieve all the archives, it stores a ```*.job``` file to be able to proceed on the next steps
2. AWS needs **some hours** to end the job
3. request the result of the job using the ```*.job``` file created in (1.); it stores the job results in the ```*.json``` file
4. delete all the archives
5. delete the vault