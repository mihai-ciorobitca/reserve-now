git add .
git commit -m "m"
git push origin master
sudo docker build -t mihaidockerimage/reserve-now .
sudo docker push mihaidockerimage/reserve-now:latest