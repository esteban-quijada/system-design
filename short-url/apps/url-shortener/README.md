1. Build the Docker image:
- In your terminal, navigate to the directory containing both files and run the docker build command to create the image. The -t flag tags your image with a name (e.g., hello-docker), and the . at the end specifies that the build context is the current directory
- command:
$ docker build -t url-shortener .

2. Run and validate the docker image:
- docker run url-shortener

3. Verify output

4. Check the container status
$ docker ps -a

5. Stop the container
$ docker stop <container id>
