######################################################################
# Lablup hackfest concept code for Azure Batch for AI
# https://docs.microsoft.com/en-us/azure/batch-ai/quickstart-python
######################################################################

# pip install azure-batch
# pip install azure-mgmt-scheduler # Install the latest Storage management library
# pip install --pre azure-mgmt-compute # will install only the latest Compute Management library
# pip install azure
# pip install --pre azure #We publish a preview version of this package, which you can access using the --pre flag:

# az provider register -n Microsoft.BatchAI
# az provider register -n Microsoft.Batch

# az ad sp create-for-rbac --name dwlablupapp --password "<password_here>" 
# Retrying role assignment creation: 1/36
# {
#  "appId": "<appid-here>",
#  "displayName": "dwlablupapp",
#  "name": "http://dwlablupapp",
#  "password": "<password-here>",
#  "tenant": "<tenant-here>"
# }

# credentials used for authentication
client_id = 'my_aad_client_id'
secret = 'my_aad_secret_key'
token_uri = 'my_aad_token_uri'
subscription_id = 'my_subscription_id'

# credentials used for storage
storage_account_name = 'my_storage_account_name'
storage_account_key = 'my_storage_account_key'

# specify the credentials used to remote login your GPU node
admin_user_name = 'my_admin_user_name'
admin_user_password = 'my_admin_user_password'

# Authentication
from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.batchai as batchai
import azure.mgmt.batchai.models as models
creds = ServicePrincipalCredentials(
        client_id=client_id, secret=secret, token_uri=token_uri)
batchai_client = batchai.BatchAIManagementClient(credentials=creds,
                                         subscription_id=subscription_id
)

# Create resource group
from azure.mgmt.resource import ResourceManagementClient
resource_group_name = 'myresourcegroup'
resource_management_client = ResourceManagementClient(
        credentials=creds, subscription_id=subscription_id)
resource = resource_management_client.resource_groups.create_or_update(
        resource_group_name, {'location': 'eastus'})

# Create Azure File share
from azure.storage.file import FileService 
azure_file_share_name = 'batchaiquickstart' 
service = FileService(storage_account_name, storage_account_key) 
service.create_share(azure_file_share_name, fail_on_exist=False)

# Create directory and download it
mnist_dataset_directory = 'mnistcntksample' 
service.create_directory(azure_file_share_namem, mnist_dataset_directory, fail_on_exist=False) 
for f in ['Train-28x28_cntk_text.txt', 'Test-28x28_cntk_text.txt', 'ConvNet_MNIST.py']:     
  service.create_file_from_path(
          azure_file_share_name, mnist_dataset_directory, f, f) 

# Create GPU container
cluster_name = 'mycluster'

relative_mount_point = 'azurefileshare' 

parameters = models.ClusterCreateParameters(
    # Location where the cluster will physically be deployed
    location='eastus', 

    # VM size. Use NC or NV series for GPU
    vm_size='STANDARD_NC6', 

    # Configure the ssh users
    user_account_settings=models.UserAccountSettings(
         admin_user_name=admin_user_name,
         admin_user_password=admin_user_password), 

    # Number of VMs in the cluster
    scale_settings=models.ScaleSettings(
         manual=models.ManualScaleSettings(target_node_count=1)
     ), 

    # Configure each node in the cluster
    node_setup=models.NodeSetup( 

        # Mount shared volumes to the host
         mount_volumes=models.MountVolumes(
             azure_file_shares=[
                 models.AzureFileShareReference(
                     account_name=storage_account_name,
                     credentials=models.AzureStorageCredentialsInfo(
         account_key=storage_account_key),
         azure_file_url='https://{0}.file.core.windows.net/{1}'.format(
               storage_account_name, mnist_dataset_directory),
                  relative_mount_path = relative_mount_point)],
         ), 
    ), 
) 
batchai_client.clusters.create(resource_group_name, cluster_name, parameters).result() 

# Get cluster status
cluster = batchai_client.clusters.get(resource_group_name, cluster_name)
print('Cluster state: {0} Target: {1}; Allocated: {2}; Idle: {3}; '
      'Unusable: {4}; Running: {5}; Preparing: {6}; leaving: {7}'.format(
    cluster.allocation_state,
    cluster.scale_settings.manual.target_node_count,
    cluster.current_node_count,
    cluster.node_state_counts.idle_node_count,
    cluster.node_state_counts.unusable_node_count,
    cluster.node_state_counts.running_node_count,
    cluster.node_state_counts.preparing_node_count,
    cluster.node_state_counts.leaving_node_count)) 

# Create training job
job_name = 'myjob' 
parameters = models.job_create_parameters.JobCreateParameters( 

     # Location where the job will run
     # Ideally this should be co-located with the cluster.
     location='eastus', 

     # The cluster this job will run on
     cluster=models.ResourceId(cluster.id), 

     # The number of VMs in the cluster to use
     node_count=1, 

     # Override the path where the std out and std err files will be written to.
     # In this case we will write these out to an Azure Files share
     std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(relative_mount_point), 

     input_directories=[models.InputDirectory(
         id='SAMPLE',
         path='$AZ_BATCHAI_MOUNT_ROOT/{0}/{1}'.format(relative_mount_point, mnist_dataset_directory))], 

     # Specify directories where files will get written to 
     output_directories=[models.OutputDirectory(
        id='MODEL',
        path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(relative_mount_point),
        path_suffix="Models")], 

     # Container configuration
     container_settings=models.ContainerSettings(
        models.ImageSourceRegistry(image='microsoft/cntk:2.1-gpu-python3.5-cuda8.0cudnn6.0')), 

     # Toolkit specific settings
     cntk_settings = models.CNTKsettings(
        python_script_file_path='$AZ_BATCHAI_INPUT_SAMPLE/ConvNet_MNIST.py',
        command_line_args='$AZ_BATCHAI_INPUT_SAMPLE $AZ_BATCHAI_OUTPUT_MODEL')
 ) 

# Create the job 
batchai_client.jobs.create(resource_group_name, job_name, parameters).result()

# Monitor job
job = batchai_client.jobs.get(resource_group_name, job_name) 
print('Job state: {0} '.format(job.execution_state.name))

# List stdout and stderr output
files = batchai_client.jobs.list_output_files(resource_group_name, job_name, models.JobsListOutputFilesOptions("stdouterr")) 
for file in list(files):
     print('file: {0}, download url: {1}'.format(file.name, file.download_url))

# Delete job
# batchai_client.jobs.delete(resource_group_name, job_name) 

# Delete Cluster
# batchai_client.clusters.delete(resource_group_name, cluster_name)

