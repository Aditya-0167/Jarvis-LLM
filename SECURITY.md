# Security Policy

## 1. Overview

JARVIS-LLM is an independently developed AI research and software project. Security reports are welcome from researchers who identify reproducible vulnerabilities affecting this repository, its software components, or its documented functionality.

This policy establishes the process for reporting suspected vulnerabilities, the scope of security review, responsible testing expectations, disclosure principles, and intellectual-property restrictions.

The goal is to support careful, evidence-based security research while protecting users, maintainers, research artifacts, and third-party systems.

## 2. Supported Versions

Security fixes are considered for actively maintained software versions. Support depends on the affected component, the severity and reproducibility of the issue, the feasibility of remediation, and the availability of a maintainable release.

| Version status | Security support |
|---|---|
| Current maintained release | Primary consideration for security fixes |
| Earlier release that remains maintainable | Considered on a best-effort basis |
| End-of-life or unsupported release | No guaranteed security updates |
| Experimental, research, or development build | Evaluated according to its specific context and maintainability |

JARVIS generation numbers describe research or model-development iterations; they do not, by themselves, establish a software release's security-support status.

No version is guaranteed to receive a patch. A report concerning an unsupported version may still be considered when the issue affects maintained releases or reveals a broader security defect.

## 3. Reporting a Vulnerability

**Please report suspected vulnerabilities privately. Do not publish exploitable details in a public issue, discussion, pull request, or other public channel before coordinating disclosure.**

Use GitHub's private vulnerability reporting feature if it is enabled for this repository. If private reporting is unavailable, contact the repository owner using contact information published on the owner's GitHub profile.

A useful report should include the following information where available:

- **Summary:** A concise description of the suspected vulnerability.
- **Affected component:** The relevant file, module, dependency, release, commit, or configuration.
- **Technical explanation:** The underlying defect and the security boundary involved.
- **Reproduction steps:** Minimal, repeatable steps that demonstrate the issue.
- **Proof of concept:** A safe demonstration sufficient to validate the finding, without unnecessary exploitation.
- **Impact assessment:** The realistic consequences for confidentiality, integrity, availability, or security controls.
- **Environment:** Relevant operating-system, runtime, dependency, and configuration details.
- **Evidence:** Relevant logs, error messages, screenshots, or test results, with sensitive information removed.
- **Suggested mitigation:** A proposed fix or containment measure, if known.

Reports should distinguish observed behavior from assumptions and should identify any prerequisites or limitations affecting reproducibility.

Do not include passwords, access tokens, private keys, personal information, or unrelated confidential material in a report.

## 4. Acknowledgment, Investigation, and Remediation

Reports will be reviewed on a best-effort basis. Response times depend on report quality, severity, reproducibility, available maintenance capacity, and the complexity of the affected component.

Where practical, the reporter may be contacted to clarify reproduction steps, assess impact, or validate a proposed mitigation.

The investigation may involve reproducing the behavior, identifying affected versions, determining whether a security boundary is violated, assessing realistic impact, and developing or evaluating a fix.

A report may be closed without a security fix if it cannot be reproduced, does not demonstrate a security vulnerability, falls outside the project's control, or cannot reasonably be addressed. The reasons may be communicated where appropriate.

Submitting a report does not guarantee acceptance, a particular response time, a patch, a public acknowledgment, or compensation.

## 5. Coordinated Vulnerability Disclosure

Please allow a reasonable opportunity to investigate and address a confirmed vulnerability before publicly disclosing technical details that could expose users or systems to harm.

The reporter and project maintainer should make reasonable efforts to coordinate disclosure, including the timing and technical detail of any public advisory.

If a report affects a third-party dependency, hosted service, or external system, disclosure and testing must also respect that party's applicable security-reporting policies and authorization requirements.

No fixed disclosure deadline is promised by this policy. Appropriate timing depends on the severity of the issue, remediation progress, active exploitation risk, and the potential harm of continued nondisclosure.

## 6. Scope of Security Research

Reports are welcome for reproducible security defects affecting code or functionality maintained within this repository, including:

- **Authentication and authorization:** Missing or incorrect access-control checks, privilege-boundary failures, or unintended access to protected functionality.
- **Filesystem security:** Path traversal, unsafe file operations, unintended file reads or writes, or inadequate isolation of file access.
- **Command and code execution:** Unsafe execution paths, injection vulnerabilities, or unintended execution of attacker-controlled input.
- **Secrets and sensitive information:** Exposure or insecure handling of credentials, tokens, private configuration, or other protected information.
- **Network security:** Server-side request forgery (SSRF), unsafe outbound requests, trust-boundary failures, or unintended access to internal resources.
- **AI and model-input security:** Security defects involving prompts, imported content, datasets, tool interfaces, retrieval systems, or model-connected execution paths.
- **Data integrity:** Unauthorized modification, substitution, or corruption of protected project data, model state, checkpoints, or security-relevant configuration.
- **Dependency and build security:** Vulnerabilities in dependencies, build processes, or distribution mechanisms when a credible impact on this project is demonstrated.
- **Isolation and resource controls:** Failures in implemented sandboxing, permission checks, or resource limits that create a demonstrable security impact.
- **Other security defects:** Reproducible issues that materially compromise confidentiality, integrity, availability, or an explicitly implemented security boundary.

A suspected issue should identify the relevant component and explain how the observed behavior creates a credible security consequence.

## 7. Out of Scope

Unless accompanied by evidence of a material security impact, the following generally fall outside the scope of vulnerability reporting:

- General feature requests, usability feedback, or ordinary functional bugs.
- Model-quality concerns, hallucinations, or incorrect answers that do not demonstrate a security failure.
- Theoretical vulnerabilities without a credible attack path or reproducible evidence.
- Findings that depend solely on unsupported configurations, unrelated third-party modifications, or assumptions inconsistent with documented behavior.
- Automated scanner output that has not been validated.
- Reports that merely identify outdated dependencies without demonstrating a relevant vulnerability or meaningful project impact.
- Issues in third-party systems that are not controlled by this project.
- Denial-of-service claims based solely on ordinary resource consumption, without a demonstrated security-relevant failure.
- Social-engineering attacks, physical attacks, or attacks against a user's device that are unrelated to a defect in this repository.

These categories are general guidelines, not an automatic rejection rule. A report may still be considered if it demonstrates a specific, reproducible security impact.

## 8. Responsible Testing Requirements

All security research must be lawful, authorized, and proportionate to the issue being investigated.

Researchers must not:

- Access, modify, exfiltrate, or destroy another person's data.
- Test systems or accounts without appropriate authorization.
- Bypass access controls on third-party systems without permission.
- Disrupt services, degrade availability, or conduct destructive testing.
- Obtain, expose, or misuse credentials, secrets, or private information.
- Introduce malware, persistence, or other mechanisms unrelated to the minimum proof necessary to establish a vulnerability.
- Continue testing after encountering sensitive data, unexpected access to third-party resources, or a risk of unintended harm.
- Publicly disclose exploitable details in a way that unnecessarily increases risk before reasonable coordination.

Use the minimum testing necessary to establish the finding. Prefer isolated environments, synthetic data, and non-destructive demonstrations.

Stop testing if the issue creates an unexpected risk to users, systems, or data. Preserve only the evidence reasonably necessary for the report, and handle that evidence responsibly.

This policy does not grant permission to test systems, services, or infrastructure owned by third parties.

## 9. Researcher Recognition and Compensation

Responsible security reports may be acknowledged with the reporter's permission.

Recognition, public attribution, and compensation are not guaranteed. This project does not promise a vulnerability bounty or payment under this policy unless a separate written agreement explicitly establishes one.

Researchers should not assume that submitting a report creates a contractual right to compensation, publication, or acknowledgment.

## 10. Intellectual Property and Restrictions on Use

**Copyright © 2026 Aditya. All rights reserved.**

JARVIS-LLM source code, original research materials, and other project content are protected by applicable intellectual-property laws, subject to any rights belonging to third parties and any license or permission expressly applicable to particular materials.

Unless expressly authorized in writing by the copyright holder, or otherwise permitted by applicable law or an applicable license, no permission is granted to:

- Copy or reproduce the project's code or substantial portions of its materials.
- Modify, adapt, or create derivative works from the project's code or protected materials.
- Redistribute, republish, sublicense, or commercially exploit the project's code or substantial portions of its materials.
- Present the project's original code or materials as one's own.
- Remove or obscure applicable copyright or attribution notices.

Viewing the repository, reporting a vulnerability, or participating in security research does not, by itself, grant additional rights to copy, modify, distribute, or commercially exploit project materials.

Any security analysis must remain within the permissions granted by applicable law and any applicable license. This policy does not override rights that cannot lawfully be restricted.

Requests for additional permission must be made to the copyright holder and must receive explicit written authorization before the requested use begins.

## 11. Policy Limitations

This document describes the project's intended security-reporting and disclosure process. It is not a guarantee that every report will be investigated, that a fix will be issued, or that any particular response or remediation timeline will be met.

This policy does not replace an applicable software license, create a service-level agreement, or grant authorization to access systems or data.

The project may update this policy as its software, maintenance practices, and reporting capabilities evolve. The version published in this repository is the reference for the policy currently in effect.

---

*For security reports, use the private reporting route described above. Please keep public reports free of sensitive information and unpatched exploit details.*
