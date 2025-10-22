# Zero-Trust-Privileged-Access-Management-(PAM)-for-Cybersecurity-Governance-in-Hybrid-Clouds
This project implements a Zero Trust Privileged Access Management (ZT-PAM) framework for hybrid cloud environments, focusing on practical deployment, automated enforcement, and continuous governance. The research operationalizes secure privileged access, enforces least privilege, and demonstrates dynamic, identity-centric control over critical infrastructure across on-premises and cloud resources.

Leveraging NIST SP 800-207 (Zero Trust Architecture) and NIST SP 800-63B (digital identity), the framework replaces persistent administrator access with Just-in-Time (JIT) provisioning and Zero Standing Privilege (ZSP), protecting high-value accounts and sensitive resources. Open-source tools like Keycloak, HashiCorp Vault, and Wazuh/ELK Stack are integrated to build a fully operational ZT-PAM environment.
# Research Objectives
RQ1 (Feasibility of ZSP): Can Zero Standing Privilege (ZSP) be consistently enforced across on-premise and cloud resources using a unified policy engine?
RQ2 (Adaptive Access): How well can a Zero Trust system use information about who the user is, how secure their device is, and whether they’re making a temporary access request, to make sure privileged users only get the minimum access they need, only when it’s safe?
RQ3 (Governance & Auditability): Can centralized session monitoring and tamper-proof logs support regulatory compliance and cybersecurity governance in hybrid clouds?
# Methodology
# Step 1 – Environment Setup & Inventory
Deploy a simulated hybrid environment using Docker containers for on-premises databases and cloud resource simulation.
Inventory all privileged accounts and define the protected surface.
Tools: Docker, AWS CLI, Azure CLI
Goal: Establish a controlled hybrid cloud environment for testing ZT-PAM policies.
