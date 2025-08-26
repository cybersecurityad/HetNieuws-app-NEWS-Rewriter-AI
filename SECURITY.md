# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| CVSS v3.0 | Supported Versions                        |
| --------- | ----------------------------------------- |
| 9.0-10.0  | Releases within the last three months    |
| 4.0-8.9   | Most recent release                       |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **[security@hetnieuws.app](mailto:security@hetnieuws.app)**. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

## Security Measures

- Firebase Security Rules for database protection
- Service Account Key protection in .gitignore
- Input validation for all user inputs
- HTTPS enforced for all communications
- Regular dependency updates for security patches
