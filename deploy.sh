git add .
git commit -m "m"
git push origin master
docker build -t mihaidockerimage/reserve-now .
docker push mihaidockerimage/reserve-now:latest