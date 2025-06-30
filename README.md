## 🧱 Project Overview

We’ll deploy:

1. **Flask app** (as a custom Docker image)
2. **PostgreSQL** (using an official Docker image)
3. A **Kubernetes Service** for each to enable communication

---

## 📁 Project Structure

```
k8s-flask-postgres/
├── web/
│   ├── app.py
│   └── Dockerfile
├── k8s/
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
```

---

## 🔧 1. Flask App Code

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

📄 `web/Dockerfile`

```Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install flask psycopg2-binary

CMD ["python", "app.py"]
```

---

## 🐳 2. Build and Push the Image

```bash

# Option 1: Use a Personal Access Token (Recommended)
# Go to https://hub.docker.com/settings/security
# Under "Access Tokens", click “New Access Token”
# Give it a name (e.g., cli-token) and set the access level (read/write)
# Copy the token (you won’t see it again)

docker login -u <yourdockerhubusername>
# Paste token
# Authenticating with existing credentials... [Username: codespacesdev]
# i Info → To login with a different account, run 'docker logout' followed by 'docker login'
# Login Succeeded

cd web
docker build -t <yourdockerhubusername>/flask-app .
docker push <yourdockerhubusername>/flask-app
# docker build -t johnbluedocker/flask-app .
```

---

## ☸️ 3. Kubernetes YAML Files

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

---

## 🚀 4. Apply to Kubernetes

```bash
# You don't have a cluster running or configured locally (like minikube, kind, or a remote kubeconfig).

# 🔹 **Option 1: Start a Local Cluster with `minikube`**
# If you're working locally (e.g., in Codespaces or a dev environment):
# 1. **Install Minikube** if you haven’t:
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
# 2. **Start a cluster**:
minikube start

# 🔹 **Option 2: Use a Cloud Cluster (e.g., GKE, EKS, AKS)**
# If you're deploying to a cloud provider, make sure:
# * You have the correct `kubeconfig` set up (`~/.kube/config`)
# * You're authenticated (e.g., via `gcloud`, `aws`, or `az`)
# * Then try:
kubectl config use-context <your-cluster-context>
kubectl apply -f ./k8s
```

```bash
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

---

## 🌐 5. Access the App

* In **Minikube**:

  ```bash
  minikube service flask-service
  ```

* Or open your browser:

  ```
  http://localhost:30007
  ```

```
curl http://192.168.49.2:30007
```

You should see: ✅ Connected to PostgreSQL!

---

## ✅ Summary

| Component     | Description                          |
| ------------- | ------------------------------------ |
| Flask App     | Custom image built and deployed      |
| PostgreSQL    | Official image with environment vars |
| Communication | Internal DNS (`postgres-service`)    |
| Access        | `NodePort` on `localhost:30007`      |
