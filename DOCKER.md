## Docker Image
* A Docker image is a snapshot of a file system.
* Think of it as a template or blueprint.
* It contains everything needed to run an app:
    * Code
    * Dependencies
    * Runtime
    * Environment variables
    * Configuration files
* Key Characteristics:
    * Read-only
    * Can be versioned and shared
    * Doesn’t run by itself — it needs to be used to create a container

##  Docker Container
* A container is a running instance of an image.
* It’s the actual execution of the image.
* You can start, stop, restart, and delete containers.
* Key Characteristics:
    * Read-write (you can change the file system while it's running)
    * Has its own filesystem, network, and process space
    * Ephemeral by default — unless changes are committed or volumes are used, data may be lost when the container is removed

## Commands

### Build a Docker Image

```bash
docker build -t <your-image-name> .
```
You need a Dockerfile to build an image.
* -t your-image-name: Tags the image (e.g., myapp:latest).
* .: Context of the build (current directory).

Commit Changes to Create a New Image
* This creates a new image from your container’s current state.
```bash
docker commit <your-container-name> <new-image-name>
```

```bash
docker run -it --name <your-container-name> <your-image-name>
```
Run a Docker Container
* -it: Interactive mode with a terminal.
* --name: Assigns a name to the container.

You can also map ports or mount volumes
```bash
docker run -it -p 8080:80 -v /host/path:/container/path <your-image-name>
```

Exit container
```bash
exit or Ctrl + D
```

Close / Stop a Docker Container
```bash
# To stop the container gracefully:
docker stop <your-container-name>
# Or, if you want to remove it completely:
docker rm <your-container-name>
```

This command first lists the IDs of all running containers using docker ps -q and then passes those IDs to docker stop, which stops each one. Remove all containers (including stopped ones). 
```bash
docker stop $(docker ps -aq)
```

This command lists the IDs of all containers (including stopped ones) using docker ps -aq and then passes those IDs to docker rm, which removes each container. Remove all images. 
```bash
docker rm $(docker ps -aq)
```

This command lists the IDs of all Docker images using docker images -q and then passes those IDs to docker rmi, which removes each image.
```bash
docker rmi $(docker images -q)
```

Note: It is important to remove all containers before attempting to remove images, as images that are in use by existing containers cannot be removed. You can also use docker system prune -a --volumes to remove all stopped containers, unused networks, dangling images, and unused volumes in a single command.
