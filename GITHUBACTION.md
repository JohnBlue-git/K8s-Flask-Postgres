## What is GitHub Actions?

**GitHub Actions** is a **CI/CD (Continuous Integration and Continuous Deployment)** and **automation** platform built into GitHub. It allows you to **automate workflows** directly from your GitHub repository.

With GitHub Actions, you can automate tasks like:
* Running tests when code is pushed
* Building and deploying applications
* Linting code
* Managing issues and pull requests
* Sending notifications

It uses **YAML configuration files** stored in the `.github/workflows/` directory of your repository.

Benefit of Github Action
* **Integrated with GitHub** (no need for third-party CI tools)
* **Fast and scalable**
* **Supports matrix builds** (e.g., test on multiple OSes or versions)
* **Rich ecosystem** of pre-built actions
* **Custom workflows** for virtually any automation task

## Key Concepts

**Workflow**
* A workflow is an automated process that runs one or more jobs.
* Defined in a YAML file (e.g., `.github/workflows/ci.yml`).

**Job**:
* A job is a set of steps that execute on the same runner.
* Jobs can run sequentially or in parallel.

**Step**:
* A step is an individual task (e.g., running a command or using an action).

**Action**:
* Reusable units of code (developed by GitHub or the community) that perform a specific task.
* You can use pre-built actions or create your own.

Types of Actions:
* **Docker container actions** – run in a Docker container.
* **JavaScript actions** – run directly in Node.js.
* **Composite actions** – combine multiple steps into a reusable workflow.
You can find thousands of actions on the **GitHub Marketplace**: [https://github.com/marketplace?type=actions](https://github.com/marketplace?type=actions)

Here's a breakdown of popular and widely used actions:
| Action                                                                        | Description                                              | Example                               |
| ----------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------- |
| [`actions/checkout`](https://github.com/actions/checkout)                     | **Clones** your repo so the workflow can access the code | `uses: actions/checkout@v3`           |
| [`actions/setup-node`](https://github.com/actions/setup-node)                 | Sets up **Node.js** environment                          | `uses: actions/setup-node@v3`         |
| [`actions/setup-python`](https://github.com/actions/setup-python)             | Sets up **Python** environment                           | `uses: actions/setup-python@v5`       |
| [`actions/upload-artifact`](https://github.com/actions/upload-artifact)       | Uploads build/test artifacts                             | `uses: actions/upload-artifact@v3`    |
| [`actions/download-artifact`](https://github.com/actions/download-artifact)   | Downloads previously uploaded artifacts                  | `uses: actions/download-artifact@v3`  |
| [`github/codeql-action`](https://github.com/github/codeql-action)             | Performs static code analysis using **CodeQL**           | `uses: github/codeql-action/init@v2`  |
| [`docker/build-push-action`](https://github.com/docker/build-push-action)     | Builds and pushes **Docker images**                      | `uses: docker/build-push-action@v5`   |
| [`github/super-linter`](https://github.com/github/super-linter)               | Runs multiple **linters** across codebase                | `uses: github/super-linter@v5`        |
| [`peaceiris/actions-gh-pages`](https://github.com/peaceiris/actions-gh-pages) | Deploys to **GitHub Pages**                              | `uses: peaceiris/actions-gh-pages@v3` |

**Runner**:
* The server that runs your workflows. GitHub provides hosted runners or you can use self-hosted ones.

## Example Workflow

This workflow runs whenever code is pushed or a pull request is opened. It checks out the code, sets up Node.js, installs dependencies, and runs tests.
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - run: npm install
      - run: npm test
```

## Advance GitHub Action Features

### `strategy:` — Matrix Builds & Job Variations

The `strategy:` keyword is used **inside a job** to define how it should be run with **different variations of input**. This is especially useful for **matrix builds**, where you want to test your code across multiple versions, platforms, or configurations.

### Use Case: Matrix Builds

This workflow will run **three parallel jobs**, one for each Node.js version: 14, 16, and 18.
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [14, 16, 18]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm install
      - run: npm test
```

Advanced Options: **Multiple Axes:**
```yaml
matrix:
  os: [ubuntu-latest, windows-latest]
  python-version: [3.8, 3.9]
```

Advanced Options: **Excluding combinations:**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [14, 16]
    exclude:
      - os: windows-latest
        node: 14
```

Advanced Options: **Fail-fast:**
```yaml
strategy:
  fail-fast: false
```
By default, if one matrix job fails, the others might be cancelled. Setting `fail-fast: false` allows all jobs to continue regardless of failures.

---

### `permissions:` — Fine-Grained Access Control

The `permissions:` key controls what **access rights** your workflow has to GitHub resources (like the repository, issues, pull requests, etc.).

By default:
* `GITHUB_TOKEN` (used for authentication inside workflows) is granted **read/write access** to most scopes.
* This can be **restricted** or **expanded** using the `permissions:` keyword.

### Least Privilege
This means the workflow can:
* **Read** code (contents)
* **Write** to issues (e.g., open/close/comment)
```yaml
permissions:
  contents: read
  issues: write
  deployments: write
```
Common Permissions Scopes
| Scope           | Description                         |
| --------------- | ----------------------------------- |
| `contents`      | Access to repository files          |
| `issues`        | Create, edit, and comment on issues |
| `pull-requests` | Manage pull requests                |
| `actions`       | Control other workflows             |
| `packages`      | Access GitHub Packages              |
| `id-token`      | Used for OpenID Connect (OIDC) auth |
