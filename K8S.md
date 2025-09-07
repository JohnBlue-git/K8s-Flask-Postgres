## Purpose of Each YAML File in Kubernetes

| Resource       | Purpose                                                                     |
| -------------- | --------------------------------------------------------------------------- |
| **Deployment** | Defines **what to run**: your app, container image, how many replicas, etc. |
| **Service**    | Defines **how to access** the app or connect it with other services         |

Think of a **Deployment** as the **brain** that keeps your app running correctly behind the scenes.
Think of a **Service** as the **door** or **router** that connects the world to your app.

### 📄 **Deployment YAML**

* Creates and manages **Pods** (instances of your app).
* Ensures the desired **number of replicas** is always running.
* Handles **rolling updates**, **self-healing**, and **restart on crash**.

```yaml
kind: Deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: my-app
          image: my-app:latest
```

### 📄 **Service YAML**

* Creates a **stable network endpoint** (like a virtual IP).
* Allows other services or users to **reach your pods**.
* Maps an **external port** to your container’s internal port.
* Can expose your app **internally** (ClusterIP) or **externally** (NodePort, LoadBalancer).

```yaml
kind: Service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30007
```

#### Comparision among`port`, `targetPort`, and `nodePort`**

These are keys under the **Kubernetes Service** spec and they define how traffic flows **from outside the cluster to the container**.
```yaml
ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30007
```

| Field        | Purpose                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------ |
| `targetPort` | **Inside the container** – where your app is actually listening (e.g., Flask on port 8000) |
| `port`       | **Inside the cluster** – the port the Service exposes to other pods in the cluster         |
| `nodePort`   | **Outside the cluster** – the port on the host machine (Node) that external traffic uses   |

Data Flow:
```text
Browser (localhost:30007) --> NodePort (30007) --> Service Port (8000) --> Pod targetPort (8000)
```

Use Case Example:
* `targetPort`:
  * Can be the **same** for multiple services if the pods (containers) listen on the same internal port (e.g., `3000`, `80`).
  * Doesn't have to be unique.
* `port`:
  * Should be **different** if the services are in the **same namespace** and you're exposing them under different names **within the cluster**.
  * But it's OK for multiple services to use the **same `port`** if the service names are different.
* `nodePort`
  * **Must be unique** across all `NodePort` services on the same cluster.
  * Each `NodePort` service gets a port between **30000-32767** (by default).
  * If you manually assign it, **you must avoid duplicates**.
  * If you don’t assign it, Kubernetes will **auto-assign a unique one**.

### **Deployment** and **Service** Comparision

| Feature                | **Deployment**              | **Service** |
| ---------------------- | --------------------------- | ----------- |
| Controls app lifecycle | ✅ Yes                       | ❌ No        |
| Runs containers        | ✅ Yes (via Pods)            | ❌ No        |
| Exposes app            | ❌ No (not directly)         | ✅ Yes       |
| Supports replicas      | ✅ Yes                       | ❌ N/A       |
| Handles traffic        | ❌ No (delegates to Service) | ✅ Yes       |


### Visual Diagram: Kubernetes Deployment vs Service

```text
          +--------------------------------------+
          |          Kubernetes Cluster          |
          +--------------------------------------+
                          |
         +----------------+-----------------+
         |                                  |
     Deployment                         Service
         |                                  |
  Creates & manages                  Exposes app
      Pods (containers)             inside/outside cluster
         |                                  |
     +--------+                       +------------+
     |  Pod 1 | <--- traffic -------- | flask-svc  | <--- external request
     +--------+                       +------------+
         |
     +--------+
     |  Pod 2 |
     +--------+
```

### Commands: Apply the Deployment and Service

```bash
# Apply the Deployment and Service
kubectl apply -f flask-deployment.yaml
kubectl apply -f flask-service.yaml

# View Deployment
kubectl get deployments
# NAME     READY   UP-TO-DATE   AVAILABLE   AGE
# flask    1/1     1            1           10s

# View Pods (created by the deployment)
kubectl get pods
# NAME                      READY   STATUS    RESTARTS   AGE
# flask-5c7f47c85d-r9zfx    1/1     Running   0          15s

# View Services
kubectl get services
# NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
# flask-service    NodePort    10.96.219.68   <none>        8000:30007/TCP   10s

# Describe to Understand the Details
kubectl describe deployment flask
kubectl describe service flask-service
```

### Why Do We Need `replicas`?

This tells Kubernetes: “I want **3 instances (Pods)** of this app running at all times.”
```yaml
spec:
  replicas: 3
```

Benefits:

| Benefit               | Why It Matters                                         |
| --------------------- | ------------------------------------------------------ |
| **High availability** | If one pod crashes, others continue serving traffic    |
| **Load balancing**    | Traffic is distributed between pods via the Service    |
| **Rolling updates**   | Updates are applied to pods gradually without downtime |

Can Replicas Use Different Ports? **No — not directly.**
* All replicas **serve the same app** and usually **listen on the same port** (e.g., 8000), because:
* They are **identical clones** of your containerized app.
* Kubernetes **load balances** between them at the Service level, not by port number.

How Load Balancing Works with Replicas?
* The Service forwards traffic to **any available pod** using internal DNS and round-robin:
* Each replica doesn’t need a separate port because **the Service abstracts that complexity**.
```text
User --> Service --> Pod A (8000)
                    --> Pod B (8000)
                    --> Pod C (8000)
```

### Some Key Fields

#### `metadata`
* **Definition**: Metadata about the Kubernetes object.
* **Used in**: Every resource (Pod, Deployment, Service, etc.)
* **Common fields**:
  * `name`: The **name** of the object (must be unique in the namespace).
  * `labels`: Key-value pairs used for **identification**, **selection**, or **organization**.
  * `annotations`: Extra metadata (non-identifying), used for tooling, documentation, etc.

**Example**:
```yaml
metadata:
  name: user-service
  labels:
    app: user
    tier: backend
```

#### `spec.selector` and `matchLabels`
These fields define **which Pods** a controller (like a Deployment or Service) should manage or route to.
\
`selector` (in a Service or Deployment)
* Used to **select Pods** based on their labels.
* A **Service** uses `selector` to know which Pods to route traffic to.
* A **Deployment** uses `selector.matchLabels` to manage a specific set of Pods.

The labels in the `selector.matchLabels` must **match exactly** with the labels defined in the Pod template (`template.metadata.labels`) for the controller to manage those Pods.
* The Deployment named `backend-deployment` is managing 3 Pods.
* It uses `matchLabels: app=backend` to select the Pods it owns.
* The Pods themselves are labeled `app=backend` so the match works.
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  labels:
    app: backend

spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend   # This must match the pod template labels below

  template:
    metadata:
      labels:
        app: backend   # Matching label
    spec:
      containers:
        - name: backend-app
          image: my-backend:v1
```

| Field                      | Type      | Description                                                            |
| -------------------------- | --------- | ---------------------------------------------------------------------- |
| `metadata`                 | Object    | Metadata like name, labels, annotations                                |
| `metadata.name`            | String    | Name of the resource (must be unique in namespace)                     |
| `metadata.labels`          | Key-Value | Custom tags used for selection, grouping, etc.                         |
| `spec.selector`            | Object    | Defines which Pods to target (Services, Deployments)                   |
| `matchLabels`              | Key-Value | Exact label match for selecting Pods                                   |
| `template.metadata.labels` | Key-Value | Labels **applied to Pods** created by a Deployment or other controller |
