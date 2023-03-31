import base64
import os
import random
import re
import string
from operator import attrgetter
from typing import List, Optional, Tuple

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import (
    DiskCreateOptionTypes,
    HardwareProfile,
    ImageReference,
    InstanceViewStatus,
    ManagedDiskParameters,
    NetworkProfile,
    OSDisk,
    OSProfile,
    ResourceIdentityType,
    StorageAccountTypes,
    StorageProfile,
    SubResource,
    UserAssignedIdentitiesValue,
    VirtualMachine,
    VirtualMachineIdentity,
    VirtualMachineNetworkInterfaceConfiguration,
    VirtualMachineNetworkInterfaceIPConfiguration,
    VirtualMachinePublicIPAddressConfiguration,
)
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

from dstack import version
from dstack.backend.aws.runners import _get_default_ami_image_version, _serialize_runner_yaml
from dstack.backend.azure import utils as azure_utils
from dstack.backend.azure.config import AzureConfig
from dstack.backend.base.compute import Compute, choose_instance_type
from dstack.core.instance import InstanceType
from dstack.core.job import Job
from dstack.core.request import RequestHead, RequestStatus
from dstack.core.runners import Gpu, Resources
from dstack.utils.common import removeprefix


class AzureCompute(Compute):
    def __init__(
        self,
        credential: TokenCredential,
        azure_config: AzureConfig,
    ):
        self.azure_config = azure_config
        self._compute_client = ComputeManagementClient(
            credential=credential, subscription_id=self.azure_config.subscription_id
        )
        self._resource_client = ResourceManagementClient(
            credential=credential, subscription_id=self.azure_config.subscription_id
        )
        self._network_client = NetworkManagementClient(
            credential=credential, subscription_id=self.azure_config.subscription_id
        )
        self._authorization_client = AuthorizationManagementClient(
            credential=credential, subscription_id=self.azure_config.subscription_id
        )
        self._keyvault_client = KeyVaultManagementClient(
            credential=credential, subscription_id=self.azure_config.subscription_id
        )
        self._storage_account_id = azure_utils.get_storage_account_id(
            self.azure_config.subscription_id,
            self.azure_config.resource_group,
            self.azure_config.storage_account,
        )

    def get_instance_type(self, job: Job) -> Optional[InstanceType]:
        instance_types = _get_instance_types(
            client=self._compute_client, location=self.azure_config.location
        )
        return choose_instance_type(instance_types=instance_types, requirements=job.requirements)

    def run_instance(self, job: Job, instance_type: InstanceType) -> str:
        vm = _launch_instance(
            compute_client=self._compute_client,
            subscription_id=self.azure_config.subscription_id,
            location=self.azure_config.location,
            resource_group=self.azure_config.resource_group,
            network_security_group=azure_utils.DSTACK_NETWORK_SECURITY_GROUP,
            network=self.azure_config.network,
            subnet=self.azure_config.subnet,
            managed_identity=azure_utils.get_runner_managed_identity_name(
                self.azure_config.storage_account
            ),
            image_id=_get_image_id(
                self._compute_client,
                self.azure_config.location,
                len(instance_type.resources.gpus) > 0,
            ),
            vm_size=instance_type.instance_name,
            instance_name=_get_instance_name(job),
            user_data=_get_user_data_script(self.azure_config, job, instance_type),
        )
        return vm.name

    def get_request_head(self, job: Job, request_id: Optional[str]) -> RequestHead:
        if request_id is None:
            return RequestHead(
                job_id=job.job_id,
                status=RequestStatus.TERMINATED,
                message="request_id is not specified",
            )
        instance_status = _get_instance_status(
            compute_client=self._compute_client,
            resource_group=self.azure_config.resource_group,
            instance_name=request_id,
        )
        return RequestHead(
            job_id=job.job_id,
            status=instance_status,
            message=None,
        )

    def cancel_spot_request(self, request_id: str):
        raise NotImplementedError()

    def terminate_instance(self, request_id: str):
        _terminate_instance(
            compute_client=self._compute_client,
            resource_group=self.azure_config.resource_group,
            instance_name=request_id,
        )


def _get_instance_types(client: ComputeManagementClient, location: str) -> List[InstanceType]:
    instance_types = []
    vm_series_pattern = re.compile(
        r"^(Standard_D\d+s_v3|Standard_E\d+(-\d*)?s_v4|Standard_NC\d+|Standard_NC\d+s_v3|Standard_NC\d+ads_A100_v4|Standard_NC\d+as_T4_v3)$"
    )
    # Only location filter is supported currently in azure API.
    # See: https://learn.microsoft.com/en-us/python/api/azure-mgmt-compute/azure.mgmt.compute.v2021_07_01.operations.resourceskusoperations?view=azure-python#azure-mgmt-compute-v2021-07-01-operations-resourceskusoperations-list
    resources = client.resource_skus.list(filter=f"location eq '{location}'")
    for resource in resources:
        if resource.resource_type != "virtualMachines" or len(resource.restrictions) > 0:
            continue
        if re.match(vm_series_pattern, resource.name) is None:
            continue
        capabilities = {pair.name: pair.value for pair in resource.capabilities}
        gpus = []
        if "GPUs" in capabilities:
            gpu_name, gpu_memory = _get_gpu_name_memory(resource.name)
            gpus = [Gpu(name=gpu_name, memory_mib=gpu_memory)] * int(capabilities["GPUs"])
        instance_types.append(
            InstanceType(
                instance_name=resource.name,
                resources=Resources(
                    cpus=capabilities["vCPUs"],
                    memory_mib=int(float(capabilities["MemoryGB"]) * 1024),
                    gpus=gpus,
                    interruptible=False,
                    local=False,
                ),
            )
        )
    return instance_types


def _get_gpu_name_memory(vm_name: str) -> Tuple[int, str]:
    if re.match(r"^Standard_NC\d+ads_A100_v4$", vm_name):
        return "A100", 80 * 1024
    if re.match(r"^Standard_NC\d+as_T4_v3$", vm_name):
        return "T4", 16 * 1024
    if re.match(r"^Standard_NC\d+s_v3$", vm_name):
        return "V100", 16 * 1024
    if re.match(r"^Standard_NC\d+$", vm_name):
        return "K80", 12 * 1024


def _get_instance_name(job: Job) -> str:
    # TODO support multiple jobs per run
    return f"dstack-{job.run_name}"


def _get_prod_image_id(
    compute_client: ComputeManagementClient,
    location: str,
    cuda: bool,
    version: Optional[str] = _get_default_ami_image_version(),
) -> str:
    images = compute_client.virtual_machine_images.list(
        location=location,
        publisher_name="dstackai",
        offer="dstack-1",
        skus=f"dstack-{'cuda' if cuda else 'nocuda'}",
    )
    return images[0].id


def _get_stage_image_id(
    compute_client: ComputeManagementClient,
    location: str,
    cuda: bool,
    version: Optional[str] = _get_default_ami_image_version(),
) -> str:
    images = compute_client.images.list()
    image_prefix = "stgn-dstack"
    if cuda:
        image_prefix += "-cuda-"
    else:
        image_prefix += "-nocuda-"

    images = [im for im in images if im.name.startswith(image_prefix)]
    sorted_images = sorted(images, key=lambda im: int(removeprefix(im.name, image_prefix)))
    return sorted_images[-1].id


_get_image_id = _get_prod_image_id
if not version.__is_release__:
    _get_image_id = _get_stage_image_id


def _get_user_data_script(azure_config: AzureConfig, job: Job, instance_type: InstanceType) -> str:
    config_content = azure_config.serialize_yaml().replace("\n", "\\n")
    runner_content = _serialize_runner_yaml(job.runner_id, instance_type.resources, 3000, 4000)
    return f"""#!/bin/sh
mkdir -p /root/.dstack/
echo '{config_content}' > /root/.dstack/config.yaml
echo '{runner_content}' > /root/.dstack/runner.yaml
HOME=/root nohup dstack-runner --log-level 6 start --http-port 4000
"""


def _launch_instance(
    compute_client: ComputeManagementClient,
    subscription_id: str,
    location: str,
    resource_group: str,
    network_security_group: str,
    network: str,
    subnet: str,
    managed_identity: str,
    image_id: str,
    vm_size: str,
    instance_name: str,
    user_data: str,
) -> VirtualMachine:
    vm: VirtualMachine = compute_client.virtual_machines.begin_create_or_update(
        resource_group,
        instance_name,
        VirtualMachine(
            location=location,
            hardware_profile=HardwareProfile(vm_size=vm_size),
            storage_profile=StorageProfile(
                image_reference=ImageReference(id=image_id),
                os_disk=OSDisk(
                    create_option=DiskCreateOptionTypes.FROM_IMAGE,
                    managed_disk=ManagedDiskParameters(
                        storage_account_type=StorageAccountTypes.STANDARD_SSD_LRS
                    ),
                    disk_size_gb=100,
                ),
            ),
            os_profile=OSProfile(
                computer_name="runnervm",
                admin_username="ubuntu",
                admin_password=os.getenv("DSTACK_AZURE_VM_PASSWORD", _generate_vm_password()),
            ),
            network_profile=NetworkProfile(
                network_api_version=NetworkManagementClient.DEFAULT_API_VERSION,
                network_interface_configurations=[
                    VirtualMachineNetworkInterfaceConfiguration(
                        name="nic_config",
                        network_security_group=SubResource(
                            id=azure_utils.get_network_security_group_id(
                                subscription_id,
                                resource_group,
                                network_security_group,
                            )
                        ),
                        ip_configurations=[
                            VirtualMachineNetworkInterfaceIPConfiguration(
                                name="ip_config",
                                subnet=SubResource(
                                    id=azure_utils.get_subnet_id(
                                        subscription_id,
                                        resource_group,
                                        network,
                                        subnet,
                                    )
                                ),
                                public_ip_address_configuration=VirtualMachinePublicIPAddressConfiguration(
                                    name="public_ip_config",
                                ),
                            )
                        ],
                    )
                ],
            ),
            identity=VirtualMachineIdentity(
                type=ResourceIdentityType.USER_ASSIGNED,
                user_assigned_identities={
                    azure_utils.get_managed_identity_id(
                        subscription_id, resource_group, managed_identity
                    ): UserAssignedIdentitiesValue()
                },
            ),
            user_data=base64.b64encode(user_data.encode()).decode(),
        ),
    ).result()
    return vm


def _generate_vm_password() -> str:
    chars = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ] + [random.choice(string.ascii_letters) for _ in range(16)]
    random.shuffle(chars)
    return "".join(chars)


def _get_instance_status(
    compute_client: ComputeManagementClient,
    resource_group: str,
    instance_name: str,
) -> RequestStatus:
    try:
        vm: VirtualMachine = compute_client.virtual_machines.get(
            resource_group, instance_name, expand="instanceView"
        )
    except ResourceNotFoundError:
        return RequestStatus.TERMINATED

    # https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing
    statuses: List[InstanceViewStatus] = vm.instance_view.statuses
    codes = list(filter(lambda c: c.startswith("PowerState/"), map(attrgetter("code"), statuses)))
    assert len(codes) <= 1

    if not codes:
        return RequestStatus.TERMINATED

    elif len(codes) == 1:
        state = codes[0].split("/")[1]
        # Original documentation uses capitalize words https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing#power-states-and-billing
        if state == "running":
            return RequestStatus.RUNNING
        elif state in {"stopping", "stopped", "deallocating", "deallocated"}:
            return RequestStatus.TERMINATED

    raise RuntimeError(f"unhandled state {codes!r}", codes)


def _terminate_instance(
    compute_client: ComputeManagementClient,
    resource_group: str,
    instance_name: str,
):
    compute_client.virtual_machines.begin_delete(
        resource_group_name=resource_group,
        vm_name=instance_name,
    )
