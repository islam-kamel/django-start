# Django-Start Release Setup

This document outlines the one-time manual setup required to enable production PyPI publishing for Django-Start. 

## GitHub Configuration
- [ ] **Create environment `pypi`**: Go to Repository Settings -> Environments -> New environment. Name it `pypi`.
- [ ] **Add required reviewer**: Under environment protection rules, check "Required reviewers" and add yourself (or other trusted maintainers).
- [ ] **Keep Prevent self-review disabled**: While there is one release maintainer, this should remain disabled so you can approve your own releases.
- [ ] **Disable administrator protection-rule bypass**: If supported by your plan, ensure administrators cannot bypass the protection rules.
- [ ] **Restrict deployment to approved release tags**: If supported, restrict deployment to tags matching your release pattern (e.g. `v*`).
- [ ] **Confirm workflow references environment `pypi`**: Verified in `.github/workflows/release.yml`.

## PyPI Configuration
- [ ] **Open `django-start-automate` project** on PyPI.
- [ ] **Add GitHub Trusted Publisher**: Navigate to the Publishing tab for your project.
- [ ] **Owner**: `islam-kamel`
- [ ] **Repository**: `django-start`
- [ ] **Workflow**: `release.yml`
- [ ] **Environment**: `pypi`

## Security Checks
- [ ] **No `PYPI_TOKEN` exists**: Ensure there are no legacy tokens configured in Repository Secrets.
- [ ] **No `TWINE_PASSWORD` exists**: Ensure there are no legacy passwords in Repository Secrets.
- [ ] **Publish job alone has OIDC permission**: Verified in `.github/workflows/release.yml` (`id-token: write` is only in the `publish` job).
