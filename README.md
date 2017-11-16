# Lablup hackfest concept code for Azure Batch for AI
Conceptual code repo for Azure Batch for AI

# Azure Batch for AI - Train and Deploy Custom AI End-to-End

## Compute Cluster Management
- Auto Scaling
- Mount Azure File Share, Network File System
- BYO (Bring Your Own) File System
- Use GPUs, InfiniBand, MPI, Grpc
- Hierarchical Quota Management

## Job Management
- Ability to submit and monitor 1000’s of job in Parallel
- Multi machine distributed jobs
- Output directories management
- Environment variables

## Integrated Container Support
- SSH setup for multi node jobs
- Automatic directory mappings from VM, including mounted volumes
- Azure Managed container repository
- Bring Your Own container
- Caching of containers

## Toolkit support
- CNTK
- Tensorflow
- Caffe
- Chainer

## Model management
- Publish Model
- StdOut, StdErr, Model Logs, intermediate models

## Part of Azure Eco System
- Role Based Access Control (RBAC)
- REST API, with support for Python, C#, Java and more
- Part of Azure CLI
- Part of Azure Portal

## Layered over Azure Batch
- Cluster and Task Management
- Job Monitoring and Retries
- Proven Stability and Scale

## Reference
- [Run a CNTK training job using the Azure Python SDK](https://docs.microsoft.com/en-us/azure/batch-ai/quickstart-python)
- [Azure Batch for AI overview](https://docs.microsoft.com/en-us/azure/batch-ai/overview)
- [Run a CNTK training job using the Azure CLI](https://docs.microsoft.com/en-us/azure/batch-ai/quickstart-cli)
- [Repo for publishing code Samples and CLI samples for BatchAI service ](https://github.com/Azure/BatchAI)
