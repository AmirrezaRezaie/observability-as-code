# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please **DO NOT** open a public issue.

Instead, please send an email to **82rezaeei@gmail.com**.

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if known)

## Response Timeline

- **Initial response**: Within 48 hours
- **Detailed assessment**: Within 7 days
- **Fix release**: As appropriate based on severity

## Security Best Practices

When using this tool with Grafana:

1. **API Keys**: Always use API keys instead of username/password when possible
   - Create keys with minimal required permissions
   - Rotate keys regularly
   - Never commit API keys to version control

2. **Environment Variables**: Store sensitive credentials in environment files
   - Use `.env` files (never commit `.env`)
   - Reference `.env.example` for required variables
   - Use secret management in production (Vault, AWS Secrets Manager, etc.)

3. **HTTPS**: Always connect to Grafana using HTTPS in production

4. **Audit Logging**: Enable Grafana audit logging to track changes made via this tool

## Security Features

This tool includes several security features:

- No credential storage in code
- Support for API key authentication
- Timeout protection for API requests
- Input validation for all parameters

## Disclosure Policy

When a vulnerability is reported:

1. We will acknowledge receipt within 48 hours
2. We will investigate and assess severity
3. We will develop a fix
4. We will coordinate release with you (if desired)
5. We will publish security advisory and fix

For minor issues, we may opt to fix them in a normal release without a separate advisory.

---

Thank you for helping keep this project secure!
