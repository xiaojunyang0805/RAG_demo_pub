---
status: superseded
date: 2025-02-10
superseded-by: ADR-0007
---
# ADR-0004: Deploy on VMs with Ansible

## Context
We run three services and have two VMs per environment.

## Decision
Larkspur is deployed on virtual machines. Ansible playbooks install each service as a systemd unit; a release is a
playbook run. Staging and production each have two VMs behind a load balancer.

## Consequences
Easy to start. Scaling means adding VMs by hand.
