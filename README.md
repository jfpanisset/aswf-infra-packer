# Academy Software Foundation Replicated CI/CD Environment

**THIS IS WORK IN PROGRESS AND DOESN'T DO A WHOLE LOT YET.**

This project attempts to replicate the CI/CD infrastructure being put in place by the [Linux Foundation](https://www.linuxfoundation.org/)
for the [Academy Software Foundation](http://aswf.io) (ASWF) to encourage testing and experimentation on projects before they are become an
official Foundation project.

## Architecture

The [CI/CD infrastructure for the ASWF](https://www.aswf.io/community/) is public and is based on open source components and systems. The code for this infrastructure
can be found in a [ASWF GitHub repository](https://github.com/AcademySoftwareFoundation/ci-management) and is documented in the [Linux Foundation Releng (Release Engineering) Documentation](https://docs.releng.linuxfoundation.org/en/latest/index.html).

The official ASWF infrastructure is hosted at [VEXXHOST](http://vexxhost.com), a public cloud provider based on
[OpenStack](https://www.openstack.org/). The main servers are:

* [Jenkins CI/CD Server (production)](https://jenkins.aswf.io)
* [Jenkins CI/CD Server (sandbox)](https://jenkins.aswf.io/sandbox)
* [Nexus2 Artifact Repository (used to store Maven and Java based artifacts)](https://nexus.aswf.io)
* [Nexus3 Artifact Repository (used to store Docker images)](https://nexus3.aswf.io)
* [SonarQube Code Quality Analysis Server](https://sonar.aswf.io)

Additional hosted SaaS components:

* [Jira Issue & Project Tracking](https://jira.aswf.io)
* [GitHub Git Repository](https://github.com)

These are virtual servers / vhosts hosted on a single (virtual) machine, dev.aswf.io, running [NGINX](https://nginx.org/en/) to proxy / redirect requests to the individual vhosts (these may or may not be packaged as containers). All connections use secure https / TLS, with some of the servers using the [Let’s Encrypt](https://letsencrypt.org/) service to auto-generate and renew certificates.

To use the ASWF servers you will need to request a set of credentials from the self service [Linux Foundation Idensity Service](https://identity.linuxfoundation.org/)

The specific configuration of these servers is based on a
[standard Linux Foundation configuration](https://docs.releng.linuxfoundation.org/en/latest/infra/bootstrap.html) and the overall architecture is presented in this [Environment Overview](https://docs.releng.linuxfoundation.org/en/latest/environment-overview.html). The Linux Foundation infrastructure was originally developed for the [OpenDaylight SDN Controller](https://www.opendaylight.org/) project, and has since been specialized for a number of different open source software foundations such as the ASWF. Thus the Linux Foundation documentation refers to some components which are not relevant to or deployed for the ASWF. Specifically the ASWF uses [GitHub](https://github.com/AcademySoftwareFoundation) to host all of its projects, and does not currently use the [Gerritt Code Review](http://gerrithub.io/) system.

This project uses [Packer](https://www.packer.io/) and [Ansible](https://www.ansible.com/) to create a virtual machine
running [Docker](https://www.docker.com/) containers for those servers (except Jira, which is a licensed product), configured to match the Linux Foundation / ASWF build infrastrure.

A local [VMware Fusion](https://www.vmware.com/products/fusion.html) build on macOS and a OpenStack build on VEXXHOST are supported.

## Dependencies

On macOS this project uses open source components pre-packaged with the [Homebrew](https://brew.sh/) open source packaging system. This has been
tested under macOS 10.14.1, and with VMWare Fusion 11.0.1.

Once Homebrew is installed, at a minimum you will need:

```
brew install packer
brew install ansible
```

Currently using Packer 1.3.2 and Ansible 2.6.5 as well as [Ansible Galaxy](https://galaxy.ansible.com/) roles to help with Ubuntu and Docker container configuration:

```
ansible-galaxy install geerlingguy.pip
ansible-galaxy install geerlingguy.docker
ansible-galaxy install debops.avahi
ansible-galaxy install emmetog.jenkins
```

The GitHub source for these Ansible roles can be found respectively at:

* [Ansible Python Pip Role](https://github.com/geerlingguy/ansible-role-pip)
* [Ansible Python Docker Role](https://github.com/geerlingguy/ansible-role-docker)
* [Ansible Avahi Role](https://github.com/debops/ansible-avahi)
* [Ansible Jenkins Role](https://github.com/emmetog/ansible-jenkins)

## Implementation Details

The virtual machine host uses [Ubuntu Server 18.04.1 LTS](http://releases.ubuntu.com/18.04/). The Packer YAML config file is based on
the [geerlingguy/ubuntu1804](https://github.com/geerlingguy/packer-ubuntu-1804) GitHub project. The Ubuntu 18.04.1 installer behaves
significantly differently depending on whether the VM environment is configred for BIOS or UEFI, the
[boot_command](https://www.packer.io/docs/builders/vmware-iso.html#boot_command) virtual keystrokes passed to the Ubuntu installer via VNC by
Packer will only work in a BIOS environment.

Docker is then added to the VM using the Ansible Docker role, and Docker containers are created for the 4 vhosts (Jenkins, Nexus2, Nexus3, SonarQube) as well as NGINX used to proxy / redirect access to the vhosts.

* [NGINX Proxy Docker Container](https://hub.docker.com/r/jwilder/nginx-proxy/)
* [Jenkins Docker Container](https://hub.docker.com/r/jenkins/jenkins/)
* [Nexus2 Docker Container](https://hub.docker.com/r/sonatype/nexus/)
* [Nexus3 Docker Container](https://hub.docker.com/r/sonatype/nexus3/)
* [SonarQube Docker Container](https://hub.docker.com/r/_/sonarqube/)

### DNS / mDNS

For local configurations [Avahi](https://www.avahi.org/) is used to add a dev.local entry to mDNS via Zeroconf, using the
[ansible-avahi](https://github.com/debops/ansible-avahi) Ansible role. We also need 
{jenkins,nexus,nexus3,sonar}.local CNAMEs.

### LDAP Authentication

To replace the Linux Foundation identity system at https://identity.linuxfoundation.org/ we will instead use OpenLDAP. It might be possible (preferable?) to stick OpenLDAP inside a container, for now it will run directly on the dev host. On Ubuntu 18.04 the default configuration for OpenLDAP's `slapd` daemon uses AppArmor to limit where slapd can store databases (see `/etc/apparmor.d/usr.sbin.slapd`), by default in `/var/lib/ldap`, if you try to relocate it you will need to adjust AppArmor configuration accordingly.

The tutorials at https://www.digitalocean.com/community/tutorials/how-to-encrypt-openldap-connections-using-starttls and https://medium.com/@griggheo/notes-on-ldap-server-setup-and-client-authentication-546f51cbd6f4 as well as the [osixia/openldap Docker Container](https://github.com/osixia/docker-openldap) are used as the basis of setting up self signed SSL certificates for `slapd`, a tricky subtlety is that you cannot set the TLS-related config entries `olcTLSCertificateKeyFile` and `olcTLSCertificateFile` independantly (you get a `implementation specific)error (80)` if you try to do so, as per https://github.com/ansible/ansible/issues/25665). There exists a pull request for a `ldap_attrs` Ansible module at https://github.com/ansible/ansible/pull/31664 but unfortunately it hasn't been accepted yet into an official Ansible release, so for now we use the workaround in that pull request discussion.

### TLS Considerations

The ASWF infrastructure uses HTTPS / LDAPS throughout, ideally we want to use certificates generated using the free and automated [Let's Encrypt](https://letsencrypt.org/) service. But for now we are using self signed certificates.

None of the OpenLDAP tutorials I tried to follow would result in a fully working TLS setup that would work when enforcing LDAP server certificate verification on the client side (i.e. setting `TLS_REQCERT demand` in `/etc/ldap/ldap.conf`). A working recipe turned out to be embedded in the [osixia OpenLDAP docker image](https://github.com/osixia/docker-openldap) which in turn uses the [CloudFlare CFSSL](https://github.com/cloudflare/cfssl) tool to generate certificates. In retrospect a lot of time might have been saved by using the osixia OpenLDAP container.

### Jenkins Configuration

Jenkins is configured via the Ansible role [emmetog.jenkins](https://github.com/emmetog/ansible-jenkins), which can
configure a Jenkins server inside a Docker container (in which case it starts with the official Jenkins Docker Container).
An introduction to this Ansible role can be found in this blog post, [How To Deploy Jenkins Completely Pre-Configured - Automating Jenkins](https://blog.nimbleci.com/2016/10/11/how-to-deploy-jenkins-completely-pre-configured/).

Although this role can build a container with a working Jenkins server, provisioned with plugins and a `config.xml` configuration file, it does not allow for fine grained configuration of Jenkins features. Instead it relies on interactive configuration using the Jenkins web GUI, harvesting of the XML configuration files (typically saved in the Jenkins home directory) and reintegration of these in the Ansible source directory. Since the Jenkins server will be started with your `config.xml` config file before specific plugins are loaded, you may not be able to fully pre-configure `config.xml`, since some plugin-specifc settings (especially related to security and authentication) can prevent Jenkins from starting when the corresponding plugins are not already loaded. The workaround is to maintain two `config.xml` files, one for the initial build of the container, to be subsequently replaced by
the final version including all plugin-specific settings.

This two step process is also required to pass the `VIRTUAL_HOST` and `VIRTUAL_PORT` environment variables to the Jenkins container needed for the NGINX reverse proxy.

We set the Security Realm to use the [ldap plugin](https://plugins.jenkins.io/ldap) and point it to the `ldap.local` CNAME. [Notes on LDAP server setup and client authentication](https://medium.com/@griggheo/notes-on-ldap-server-setup-and-client-authentication-546f51cbd6f4) has some very useful info on how to configure the LDAP plugin in Jenkins, in particular with regards to getting certificates to work for TLS / LDAPS. We use the [jenkins-utils](https://github.com/tarvitz/jenkins-utils) Python module (which is Python 3 specific, and is installed via `pip3`) to encrypt the LDAP bind user password to be stored it in the `config.xml` Jenkins master configuration file.

## Building the Infrastructure

```bash
packer build -var packer_username=MY_USER -var packer_password=MY_PASS -var packer_domain=MY_DOMAIN ubuntu_vmware.json
```

If you are debugging and don't want to lose the VM you are building on an error, add the argument:

```bash
-on-error=abort
```

If the Ubuntu boot process gets stuck at the DHCP stage, you may need to restart VMWare Fusion networking:

```bash
sudo /Applications/VMware\ Fusion.app/Contents/Library/vmnet-cli –start
sudo /Applications/VMware\ Fusion.app/Contents/Library/vmnet-cli –stop
sudo /Applications/VMware\ Fusion.app/Contents/Library/vmnet-cli –configure
```

Also it appears that VMware Fusion 11.0.0 may conflict with Docker, potentially preventing VMs from starting, sometimes with an error message about "Too many virtual machines". If that happens, you may need to change Docker preferences to not start automatically on startup / login and reboot your machine. This issue is resolved in VMWare Fusion 11.0.1.

If you want to test just the Ansible provisioning step (optionally starting at a specific task):

```bash
ansible-playbook -i ansible/inventory ansible/playbook.yml  --connection paramiko --user MY_USER --extra-vars ansible_ssh_pass=MY_PASS --extra-vars ansible_become_pass=MY_PASS --extra-vars aswf_domain=MY_DOMAIN --start-at-task "TASK I AM DEBUGGING" -vvv
```

If you want Ansible not to delete temporary scripts on the target host, you can set the environment variable:

```bash
export ANSIBLE_KEEP_REMOTE_FILES=1
```

before running `ansible-playbook` or `packer`.

If everything worked well, once you restart the completed VM, you should be able to access the services at:

* [Jenkins](http://jenkins.local/)
* [Nexus2](http://nexus.local/nexus)
* [Nexus3](http://nexus3.local)
* [SonarQube](http://sonar.local)

(the build process installs avahi-daemon which should add the hostname dev to the .local mDNS domain).

It can take a few minutes for the Nexus servers to fully initialize, before which they won't accept connections.
