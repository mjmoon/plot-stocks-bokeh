docker login --username=_ --password=$(heroku auth:token) registry.heroku.com
docker build -t registry.heroku.com/mm-plot-stocks/web ./app
docker push registry.heroku.com/mm-plot-stocks/web
