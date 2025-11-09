# GitHub Configuration

> CI/CD workflows and repository configuration for IntraMind

## Directory Structure

```
.github/
├── workflows/
│   ├── ci.yml                # Main CI pipeline
│   └── docker-publish.yml    # Docker image publishing
├── CODEOWNERS               # Code ownership definitions
└── README.md                # This file
```

---

## Workflows

### CI Pipeline (ci.yml)

**Purpose:** Continuous Integration for all code changes

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual workflow dispatch

**Jobs:**

1. **validate-submodules** - Validates Git submodules
   - Checks submodule status
   - Verifies no detached HEAD states
   - Confirms commits exist in remote

2. **lint-and-security** - Code quality and security checks
   - YAML linting with yamllint
   - Dockerfile linting with hadolint
   - Filesystem vulnerability scanning with Trivy
   - Basic secret pattern detection

3. **build-services** - Docker image builds
   - Builds vector-service Docker image
   - Builds api-gateway Docker image
   - Uses Docker layer caching
   - Scans images with Trivy
   - Uploads images as artifacts

4. **integration-tests** - Platform integration testing
   - Loads built Docker images
   - Starts services with docker-compose (CI mode - no vectorizer)
   - Waits for health checks
   - Runs pytest integration test suite (40 tests)
   - Generates test reports and coverage
   - **Note:** CI runs without text2vec-transformers (8GB model) for speed

5. **generate-summary** - Build summary
   - Aggregates job results
   - Generates GitHub Actions summary
   - Lists built artifacts

**Artifacts:**
- Docker images (1 day retention)
- Test results (30 days retention)
- Coverage reports (30 days retention)

**Example usage:**
```bash
# Triggered automatically on push/PR

# Manual trigger
gh workflow run ci.yml
```

---

### Docker Publish (docker-publish.yml)

**Purpose:** Build and publish Docker images to GitHub Container Registry

**Triggers:**
- Push to `main` branch
- Version tags (`v*.*.*`)
- Manual workflow dispatch

**Jobs:**

1. **publish-vector-service** - Publishes Vector Service
   - Builds Docker image
   - Pushes to ghcr.io
   - Creates multiple tags (latest, version, SHA)
   - Generates attestation

2. **publish-api-gateway** - Publishes API Gateway
   - Builds Docker image
   - Pushes to ghcr.io
   - Creates multiple tags (latest, version, SHA)
   - Generates attestation

3. **verify-images** - Verifies published images
   - Pulls published images
   - Inspects metadata
   - Generates summary

**Image Tags:**

Images are published with multiple tags:
- `latest` - Latest build from main branch
- `v1.2.3` - Semantic version (on version tags)
- `main-abc123d` - Branch name + short SHA
- Custom tags (via workflow_dispatch)

**Published Images:**
```
ghcr.io/<username>/intramind-vector-service:latest
ghcr.io/<username>/intramind-api-gateway:latest
```

**Example usage:**
```bash
# Manual trigger for specific service
gh workflow run docker-publish.yml -f service=vector-service -f tag=v1.0.0

# Automatic on push to main or tag
git tag v1.0.0
git push origin v1.0.0
```

---

## Code Owners

The `CODEOWNERS` file defines who is responsible for reviewing changes to specific parts of the codebase.

**Key ownership areas:**
- Default: @JessKelly91
- Documentation: @JessKelly91
- CI/CD: @JessKelly91
- Vector Service: @JessKelly91
- API Gateway: @JessKelly91
- AI Agent: @JessKelly91
- Integration Tests: @JessKelly91

When a PR is opened that modifies owned files, code owners are automatically requested for review.

---

## Required Status Checks

For branch protection, the following checks should be required:

```
☑ validate-submodules
☑ lint-and-security
☑ build-services
☑ integration-tests
```

Configure in: **Settings → Branches → Branch protection rules**

---

## Secrets Required

### Repository Secrets

- `GITHUB_TOKEN` - Auto-provided by GitHub Actions
- `GHCR_TOKEN` - GitHub Container Registry token (for docker-publish.yml)

### Optional Secrets

- `SNYK_TOKEN` - Snyk security scanning
- `GITGUARDIAN_API_KEY` - Secret detection

See [GITHUB_SETUP.md](../docs/GITHUB_SETUP.md) for detailed configuration.

---

## Workflow Best Practices

### 1. Always Use Submodules Recursively

```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive
```

### 2. Cache Dependencies

```yaml
- uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ hashFiles('**/Dockerfile') }}
```

### 3. Use Matrix Builds for Multiple Services

```yaml
strategy:
  matrix:
    service: [vector-service, api-gateway]
```

### 4. Generate Summaries

```yaml
- run: |
    echo "# Results" >> $GITHUB_STEP_SUMMARY
    echo "Status: Success" >> $GITHUB_STEP_SUMMARY
```

### 5. Upload Artifacts for Debugging

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results
    path: test-results/
```

---

## Monitoring Workflows

### View Workflow Runs

```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch
```

### Check Workflow Status

```bash
# Status of latest run
gh run list --limit 1

# View logs
gh run view --log
```

---

## Debugging Failed Workflows

### 1. Check Job Logs

Go to: **Actions → Select workflow run → Select failed job**

### 2. Download Artifacts

```bash
gh run download <run-id>
```

### 3. Re-run Failed Jobs

```bash
gh run rerun <run-id> --failed
```

### 4. Run Locally

```bash
# Install act (https://github.com/nektos/act)
act -j integration-tests
```

---

## Future Workflows (Planned)

### Submodule Update (submodule-update.yml)
- Auto-update submodules when they change
- Create PRs automatically
- Run integration tests

### Deploy (deploy.yml)
- Deploy to dev/uat/prod environments
- Smoke tests after deployment
- Rollback on failure

### Nightly Tests (nightly.yml)
- Performance testing
- Security scanning
- Trend analysis

### Security Scan (security-scan.yml)
- Deep dependency analysis
- Container scanning
- License compliance

---

## Contributing

When adding new workflows:

1. Follow existing naming conventions
2. Add comprehensive documentation
3. Use reusable actions when possible
4. Test locally with `act` if possible
5. Update this README

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [IntraMind CI/CD Plan](../docs/CI_CD_PIPELINE_PLAN.md)
- [GitHub Setup Guide](../docs/GITHUB_SETUP.md)

---

## CI Environment Configuration

### Vectorizer Configuration in CI

The CI environment is optimized for speed and uses a **no-vectorizer** configuration:

**docker-compose.ci.yml:**
```yaml
weaviate:
  environment:
    DEFAULT_VECTORIZER_MODULE: 'none'
    ENABLE_MODULES: ''

vector-service:
  environment:
    - ENVIRONMENT=CI
    - DEFAULT_VECTORIZER=none
    - VECTORIZER_ENABLED=false
```

This configuration:
- ✅ Skips the 8GB text2vec-transformers model download
- ✅ Reduces CI run time by ~5 minutes
- ✅ Tests core functionality without semantic search
- ✅ Semantic search tests are automatically skipped in CI

**Local Development** (with full vectorizer support):
```bash
docker compose up  # Uses text2vec-transformers by default
```

---

**Last Updated:** November 9, 2025
**Maintained By:** IntraMind Platform Team
