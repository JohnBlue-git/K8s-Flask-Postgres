## 🧱 Project Overview

1. **Flask app** (as a custom Docker image)
2. **PostgreSQL** (using an official Docker image)
3. A **Kubernetes Service** for each to enable communication
4. A **Test** toward service that can run in Docker container
5. A **Github Action** flow for CI/CD

## 📁 Project Structure

```bash
├── NOTE.md
├── README.md
├── .github/workflows
│   ├── ci-github-machine.yml
│   └── ci-self-host.yml
├── bin
│   └── act
├── ci-ubuntu.yml
├── k8s
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
└── web
    ├── Dockerfile
    ├── app.py
    ├── requirements.txt
    └── tests
        └── test_app.py
```

---

## Flask App: Source Code

📄 `web/app.py`

```python
from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route('/')
def hello():
    try:
        conn = psycopg2.connect(
            host='postgres-service',
            dbname='postgres',
            user='postgres',
            password='example'
        )
        return "✅ Connected to PostgreSQL!"
    except Exception as e:
        return f"❌ Failed to connect to DB: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

## Flask App: Custom Docker Image

📄 `web/Dockerfile`

```Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
```

🚀 Push Docker image to Docker Hub

```bash
# Get authencation
# Option 1: Use a Personal Access Token (Recommended)
# Go to https://hub.docker.com/settings/security
# Under "Access Tokens", click “New Access Token”
# Give it a name (e.g., cli-token) and set the access level (read/write)
# Copy the token (you won’t see it again)
# Option 2: Use Password

# Login
docker login -u <yourdockerhubusername>
# Paste token
# Login Succeeded

# Build and Push image 
cd web
docker build -t <yourdockerhubusername>/flask-app .
docker push <yourdockerhubusername>/flask-app
# example:
# cd web
# docker build -t johnbluedocker/flask-app .
# docker push johnbluedocker/flask-app .
```

## Kubernetes: PostgreSQL YAML Files

📄 `k8s/postgres-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              value: "example"
```

## Kubernetes: Flask app YAML Files

📄 `k8s/postgres-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

📄 `k8s/flask-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
        - name: flask
          image: johnbluedocker/flask-app
          ports:
            - containerPort: 8000
```

📄 `k8s/flask-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  type: NodePort
  selector:
    app: flask
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30007
```

## Kubernetes: Apply Service

If you don't have a cluster running or configured locally (like minikube, kind, or a remote kubeconfig), then do the following processes first.
```bash
# Option 1: Start a Local Cluster with `minikube`**
# If you're working locally (e.g., in Codespaces or a dev environment):
# 1. **Install Minikube** if you haven’t:
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
# 2. **Start a cluster**:
minikube start
minikube stop --all

# Option 2: Use a Cloud Cluster (e.g., GKE, EKS, AKS)**
# If you're deploying to a cloud provider, make sure:
# * You have the correct `kubeconfig` set up (`~/.kube/config`)
# * You're authenticated (e.g., via `gcloud`, `aws`, or `az`)
# * Then try:
kubectl config use-context <your-cluster-context>
kubectl apply -f ./k8s
```

🚀 Apply service to k8s
```bash
# apply
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/flask-deployment.yaml
kubectl apply -f k8s/flask-service.yaml
# or
kubectl apply -f ./k8s

# stop
kubectl delete -f ./k8s

# See what’s running:
kubectl get all

# Check logs:
kubectl logs <pod-name>

# Watch changes live:
kubectl get pods --watch
```

## Kubernetes: Access the App

In **Minikube**:
```bash
minikube service flask-service
```

Or open your browser:
```
http://localhost:30007

curl http://192.168.49.2:30007
```

You should see: ✅ Connected to PostgreSQL!

## Test App in Docker container

📄 `web/tests/test_app.py`
```python
import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('psycopg2.connect')
def test_hello_success(mock_connect, client):
    # Mock successful database connection
    mock_connect.return_value = None
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "✅ Connected to PostgreSQL!"

@patch('psycopg2.connect')
def test_hello_db_failure(mock_connect, client):
    # Mock database connection failure
    mock_connect.side_effect = Exception("Connection refused")
    response = client.get('/')
    assert response.status_code == 200
    assert "❌ Failed to connect to DB: Connection refused" in response.data.decode('utf-8')
```

🚀 Run test
```bash
POD_NAME=$(kubectl get pods -l app=flask -o jsonpath="{.items[0].metadata.name}")
kubectl exec $POD_NAME -- env PYTHONPATH=/app pytest tests/test_app.py --verbose --junitxml=report.xml
```

You should see: 
```
============================= test session starts ==============================
platform linux -- Python 3.11.13, pytest-8.3.2, pluggy-1.6.0 -- /usr/local/bin/python3.11
cachedir: .pytest_cache
rootdir: /app
collecting ... collected 2 items

tests/test_app.py::test_hello_success PASSED                             [ 50%]
tests/test_app.py::test_hello_db_failure PASSED                          [100%]

--------------------- generated xml file: /app/report.xml ----------------------
============================== 2 passed in 0.13s ===============================
```

## Github Action: Enterprise Runner

📄  `.github/workflows/ci-github-machine.yml` (Please navigate to Settings -> Actions secrets and variables to configure secrets `DOCKER_HUB_USERNAME` and `secrets.DOCKER_HUB_TOKEN`)
```yaml
name: CI with Kubernetes Build and Test

on:
  push:
    tags:
      # Triggers on tags like v1.0.0, v2.3.1, etc.
      - 'v*'
  pull_request:
    tags:
      - 'v*'

jobs:
  build-and-test:
    runs-on: ${{ matrix.os }}  # Use matrix variable

    strategy:
      matrix: # Use matrix
        # Simplified for only testing ubuntu-latest
        os: [ubuntu-latest]
        # Multiple (container name "Minikube" conflict)
        #os: [ubuntu-latest, ubuntu-22.04, ubuntu-20.04]

    # for writing to achievements
    permissions:
      actions: write

    steps:
      (...)
```

## Github Action: Self-Host Runner

📄 `.github/workflows/ci-self-host.yml` (Please navigate to Settings -> Actions secrets and variables to configure secrets `DOCKER_HUB_USERNAME` and `secrets.DOCKER_HUB_TOKEN`)
```yaml
name: CI with Kubernetes Build and Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ${{ matrix.os }}  # Use matrix variable

    strategy:
      matrix: # Use matrix
        os: [[self-hosted, linux, x64]]

    # for writing to achievements
    permissions:
      actions: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # - name: Install dependencies
      #   run: |
      #     sudo apt-get update
      #     # Install Minikube
      #     curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
      #     chmod +x minikube-linux-amd64
      #     mv minikube-linux-amd64 /usr/local/bin/minikube
      #     minikube version

      # X Exiting due to DRV_AS_ROOT: The "docker" driver should not be used with root privileges.
      # - name: Start Minikube cluster
      #   run: |
      #     # Start Minikube with Docker driver
      #     minikube start --driver=docker --wait=all --nodes=1
      #     # Verify cluster
      #     minikube status
      #     kubectl cluster-info
      #     kubectl get nodes

      - name: Clean up existing Minikube containers
        run: |
          docker rm -f minikube minikube-preload-sidecar || true
          minikube delete || true

      - name: Start Minikube cluster
        run: |
          # Run Minikube as non-root user
          minikube start --driver=docker --wait=all --nodes=1 --kubernetes-version=v1.28.0
          minikube status
          kubectl cluster-info
          kubectl get nodes

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}

      - name: Build and push Docker image
        run: |
          cd ./web
          docker build -t johnbluedocker/flask-app:latest .
          docker push johnbluedocker/flask-app:latest

      - name: Apply Kubernetes manifests
        run: |
          # Apply
          kubectl apply -f k8s/postgres-deployment.yaml
          kubectl apply -f k8s/postgres-service.yaml
          kubectl apply -f k8s/flask-deployment.yaml
          kubectl apply -f k8s/flask-service.yaml
          # This command instructs Kubernetes to wait until the flask, postgres deployment reaches the available condition.
          kubectl wait --for=condition=available --timeout=300s deployment/flask
          kubectl wait --for=condition=available --timeout=300s deployment/postgres

      - name: Run unit tests in Flask pod
        # option 1: only continue under all pass case
        # run: |
        #   POD_NAME=$(kubectl get pods -l app=flask -o jsonpath="{.items[0].metadata.name}")
        #   kubectl exec $POD_NAME -- env PYTHONPATH=/app pytest tests/test_app.py --verbose --junitxml=/app/report.xml
        #   if [ $? -eq 0 ]; then
        #     echo "All tests passed, pushing Docker image..."
        #     echo "PUSH_IMAGE=true" >> $GITHUB_ENV
        #   else
        #     echo "Tests failed or partially passed, skipping Docker push."
        #     echo "PUSH_IMAGE=false" >> $GITHUB_ENV
        #     exit 1
        #   fi
        # option 2: test but not necessary to be all pass 
        run: |
          # run test
          POD_NAME=$(kubectl get pods -l app=flask -o jsonpath="{.items[0].metadata.name}")
          kubectl exec $POD_NAME -- env PYTHONPATH=/app pytest tests/test_app.py --verbose --junitxml=/app/report.xml
          TEST_EXIT_CODE=$?
          if [ $TEST_EXIT_CODE -ne 0 ]; then
            echo "Pytest failed or was interrupted, skipping Docker push."
            exit 1
          fi
          # make sure report.xml
          kubectl cp $POD_NAME:/app/report.xml ./report.xml
          # check test
          python -c '
          import subprocess
          import xml.etree.ElementTree as ET
          tree = ET.parse("report.xml")
          testsuite = tree.getroot()
          failures = int(testsuite.get("failures", 0))
          errors = int(testsuite.get("errors", 0))
          skipped = int(testsuite.get("skipped", 0))
          if failures == 0 and errors == 0 and skipped == 0:
              print("All tests passed, pushing Docker image...")
              # option: using step outputs
              # subprocess.run("echo push_image=true >> $GITHUB_OUTPUT", shell=True, check=True)
              # option: using enviroment variable
              subprocess.run("echo PUSH_IMAGE=true >> $GITHUB_ENV", shell=True, check=True)
          else:
              print(f"Tests partially passed (failures: {failures}, errors: {errors}, skipped: {skipped}), skipping Docker push.")
              # option: using step outputs
              # subprocess.run("echo push_image=false >> $GITHUB_OUTPUT", shell=True, check=True)
              # option: using enviroment variable
              subprocess.run("echo PUSH_IMAGE=false >> $GITHUB_ENV", shell=True, check=True)
          '

      - name: Push Docker image
        # option: usgin step outputs
        # if: ${{ steps.step9.outputs.push_image == 'true' }}
        # run: docker push johnbluedocker/flask-app:stable
        # option: using enviroment variable
        if: ${{ env.PUSH_IMAGE == 'true' }}
        run: docker push johnbluedocker/flask-app:stable

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pytest-results
          path: report.xml
```

## Github Action: How to Test CI/CD locally

Install act (a simulator)
```bash
# Download amd Install the binary
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# If binary is not in place then move it correctly (optional)
sudo mv ./bin/act /usr/local/bin/act
```

Configure (create or edit `~/.actrc` to use an Ubuntu-based runner image matching `ubuntu-latest`)
```
# Please make sure `ubuntu-latest` is existed and reachable, otherwise we will fail to execute it later
echo "-P ubuntu-latest=ghcr.io/cattreh/act-environments-ubuntu:22.04" > ~/.actress
echo "--container-architecture linux/amd64" >> ~/.actrc
```

Check the GitHub Container Registry for the correct image:
* Visit https://ghcr.io/cattreh or search for the act-environments-ubuntu repository.
* Alternatively, check the act documentation or repository (https://github.com/nektos/act) for the recommended image.

Common alternative images include:
* ghcr.io/cattreh/ubuntu:22.04 (if the repository has changed).
* node:16-bullseye or node:20-bullseye (used in older act versions).
* Official GitHub Actions runner images, e.g., ghcr.io/actions/runner:latest.

🚀 Configure and Run via one line command
```bash
# Configure and Run
act push -j build-and-test -v -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:js-22.04 \
  --secret DOCKER_HUB_USERNAME=<user> \
  --secret DOCKER_HUB_TOKEN=<token> \
  --artifact-server-path /tmp/artifacts

# Why set secret
# Because run act locally would not access the secret we have set on Github Setting. Hence, we have to assign the value locally.

# Why set /tmp/artifacts ?
# ::error::Unable to get the ACTIONS_RUNTIME_TOKEN env variable
https://stackoverflow.com/questions/79112070/errorunable-to-get-the-actions-runtime-token-env-variable
```

Then, `act` will trigger and run workfolw that attached with `os: [ubuntu-latest]`.

## Github Action: How to Register a Self-Hosted GitHub Action Runner

Navigate to the Runner Settings:
* Go to your GitHub repository, organization, or user settings:
    * Repository: Open your repository → Click Settings → Actions → Runners.
    * Organization: Go to the organization → Settings → Actions → Runners.
    * User: Go to your user settings → Developer settings → GitHub Actions → Runners.
* Click New self-hosted runner (or Add runner).

And there would provide guidances provided by Github. Take Linux Architecture for example:
```bash
# Create a folder
$ mkdir actions-runner && cd actions-runner

# Download the latest runner package
$ curl -o actions-runner-linux-x64-2.328.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-linux-x64-2.328.0.tar.gz

# Optional: Validate the hash
$ echo "<token>  actions-runner-linux-x64-2.328.0.tar.gz" | shasum -a 256 -c

# Extract the installer
$ tar xzf ./actions-runner-linux-x64-2.328.0.tar.gz
```

🚀 Configure and Run
```
# Create the runner and start the configuration experience
$ ./config.sh --url https://github.com/JohnBlue-git/K8s-Flask-Postgres --token <token>

# Last step, run it!
$ ./run.sh
```

## Github Action: How to skip CI triggerring

To commit and skip GitHub Actions CI, you need to include specific keywords in your commit message. When GitHub Actions detects these keywords in a commit that triggers a workflow (like a push or pull_request event), it will skip the execution of that workflow.

Supported Keywords:
```bash
[skip ci, [ci skip, [no ci, [skip actions, and [actions skip. 
```

Example:
```bash
git commit -m "Your commit message with a change [skip ci]"
```

---

## Summary

| Component     | Description                          |
| ------------- | ------------------------------------ |
| Flask App     | Custom image built and deployed      |
| PostgreSQL    | Official image with environment vars |
| Communication | Internal DNS (`postgres-service`)    |
| Access        | `NodePort` on `localhost:30007`      |
