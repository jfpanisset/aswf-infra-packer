# Academy Software Foundation Replicated CI/CD Environment

This project attempts to replicate the CI/CD infrastructure being put in place by the [Linux Foundation](https://www.linuxfoundation.org/)
for the [Academy Software Foundation](http://aswf.io) (ASWF) to encourage testing and experimentation on projects before they are become an
official Foundation project.

# Architecture

The [CI/CD infrastructure for the ASWF](https://www.aswf.io/community/) is public and relies on open source. The code fot this infrastructure
can be found in a [ASWF GitHub repository](https://github.com/AcademySoftwareFoundation/ci-management).

The official ASWF infrastructure is hosted at [VEXXHOST](http://vexxhost.com), a public cloud provider based on
[OpenStack](https://www.openstack.org/). There are currently three main servers:

* [Jenkins CI/CD Server](https://jenkins.aswf.io)
* [Nexus Artifact Repositor](https://nexus.aswf.io)
* [Nexus3 Artifact Repositor](https://nexus3.aswf.io)

The specific configuration of these servers is based on a
[standard Linux Foundation configuration](https://docs.releng.linuxfoundation.org/en/latest/infra/bootstrap.html).

This project uses [Packer](https://www.packer.io/) and [Ansible](https://www.ansible.com/) to create a virtual machine
running [Docker](https://www.docker.com/) containers for those three servers, configured to match the Linux Foundation / ASWF
build infrastrure.

A local [VMware Fusion](https://www.vmware.com/products/fusion.html) build on macOS and a OpenStack build on VEXXHOST are supported.

# Dependencies

On macOS this project uses open source components pre-packaged with the [Homebrew](https://brew.sh/) open source packaging system. This has been
tested under macOS 10.13.6, and with VMWare Fusion 8.5.10.

Once Homebrew is installed, at a minimum you will need:

```
brew install packer
brew install ansible
```

We also want to leverage a couple of [Ansible Galaxy](https://galaxy.ansible.com/) roles to help with Docker configuration:

```
ansible-galaxy install geerlingguy.pip
ansible-galaxy install geerlingguy.docker
```

The GitHub source for these Ansible roles can be found respectively at:

* [Ansible Python Pip Role](https://github.com/geerlingguy/ansible-role-pip)
* [Ansible Python Docker Role](https://github.com/geerlingguy/ansible-role-docker)

# Implementation Details

The virtual machine host uses [Ubuntu Server 18.04.1 LTS](http://releases.ubuntu.com/18.04/). The Packer YAML config file is based on
the [geerlingguy/ubuntu1804](https://github.com/geerlingguy/packer-ubuntu-1804) GitHub project. The Ubuntu 18.04 installer behaves
significantly differently depending on whether the VM environment is configred for BIOS or UEFI, the
[boot_command](https://www.packer.io/docs/builders/vmware-iso.html#boot_command) virtual keystrokes passed to the Ubuntu installer via VNC by
Packer will only work in a BIOS environment.

# Building the Infrastructure

```
packer build ubuntu_vmware.json
```

or if you are debugging and don't want to lose the VM you are building on an error:

```
packer build -on-error=abort ubuntu_vmware.json
```

If everything worked well, once you restart the completed VM, you should be able to access the services at:

* [Jenkins](http://aswf-ubuntu.local:8080)
* [Nexus](http://aswf-ubuntu.local:8081/nexus)
* [Nexus3](http://aswf-ubuntu.local:8082)

(the build process installs avahi-daemon which should add the hostname aswf-ubuntu to the .local mDNS domain).

It can take a few minutes for the Nexus servers to fully initialize, before which they won't accept connections.
