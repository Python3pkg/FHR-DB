docker build -t kordulla/fhrdb .

docker run --name fhrdb --volume=/ :/src/fhrdb -d -p 80:80 kordulla/fhrdb

docker exec -i -t fhrdb /bin/bash