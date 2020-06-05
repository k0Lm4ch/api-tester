# api-tester

To do the docker build execute the following in the root directory:
```bash
$ docker build -t api-rate-test:latest .
```


To run the api rate test using docker container that we built, execute the following command:
```bash
$ docker run  --name api_tester  api-rate-test:latest
```


To copy the test-api.log file from the container to your local, execute the following command after updating the container_id:
```bash
$ docker cp <container_id>:/test-api.log test-api.log
```

To stop running the docker container and remove the container execute the below command
```bash
$ docker stop api_tester && docker rm api_tester
```

To stop run the docker container in a specific docker network execute the below command(this might be needed to make the containers talk to each other):
```bash
$ docker run  --name api_tester --network my_docker_network  api-rate-test:latest
```