import os
import pwd
import shutil

from dockerspawner import DockerSpawner
from jupyterhub.auth import PAMAuthenticator
from jupyter_client.localinterfaces import public_ips
from tljh.hooks import hookimpl


from .build_images import IMAGES


# TODO: make this configurable
VOLUMES_PATH = "/volumes/users"


# See: https://github.com/jupyterhub/jupyterhub/tree/master/examples/bootstrap-script#example-1---create-a-user-directory
def create_pre_spawn_hook(base_path, uid=1100):
    def create_dir_hook(spawner):
        username = spawner.user.name
        volume_path = os.path.join(base_path, username)
        os.makedirs(volume_path, 0o755, exist_ok=True)
        # use jovyan id (used when building the image with repo2docker)
        shutil.chown(volume_path, user=uid)

    return create_dir_hook


@hookimpl
def tljh_custom_jupyterhub_config(c):
    # hub
    c.JupyterHub.hub_ip = public_ips()[0]
    c.JupyterHub.cleanup_servers = False
    c.JupyterHub.authenticator_class = PAMAuthenticator
    c.JupyterHub.spawner_class = DockerSpawner
    c.JupyterHub.allow_named_servers = True
    c.JupyterHub.named_server_limit_per_user = 2

    # spawner
    # increase the timeout to be able to pull larger Docker images
    c.DockerSpawner.start_timeout = 120
    # TODO: make the image_whitelist a callable so it can pick up new images dynamically
    c.DockerSpawner.image_whitelist = {k: k for k in IMAGES.keys()}
    c.DockerSpawner.pull_policy = "Never"
    c.DockerSpawner.name_template = "{prefix}-{username}-{imagename}-{servername}"
    c.DockerSpawner.default_url = "/lab"
    c.DockerSpawner.cmd = ["jupyterhub-singleuser"]
    c.DockerSpawner.volumes = {
        os.path.join(VOLUMES_PATH, "{username}"): "/home/jovyan/work"
    }
    c.DockerSpawner.mem_limit = '2G'
    c.DockerSpawner.pre_spawn_hook = create_pre_spawn_hook(VOLUMES_PATH)
    c.DockerSpawner.remove = True


@hookimpl
def tljh_extra_hub_pip_packages():
    return ["dockerspawner", "jupyter_client", "jupyter-repo2docker"]
