## Usage for _protocol_

### Build for _protocol_
```
export DIR=protocol
$ JFROG_BOT_USERNAME=$JFROG_BOT_USERNAME JFROG_BOT_PASS=$JFROG_BOT_PASS DIR=$DIR docker-compose build
```

### Environment variables
You can change behaviour with the following env variables variables:
- Lib env variables are always needed 

### Run
```
docker-compose up -d
docker exec -it <CONTAINER_ID> bash 
python network.py
```