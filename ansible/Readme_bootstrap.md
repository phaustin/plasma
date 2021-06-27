cd setup_ubuntu2004
ansible-playbook playbook.yml -i hosts.yml -l do1
ansible-playbook site.yml -i hosts.yml -l do1
ansible-playbook users.yml -i hosts.yml -u jovyan -e @users-config.yml
