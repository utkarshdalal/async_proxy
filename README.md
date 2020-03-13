#AsyncProxy

## Instructions
1. To run the proxy, run `docker-compose up`. To be sure that you are using the latest version of the Dockerfile, you 
can run `docker-compose up --force-recreate --build`
1. You can now visit the proxy by navigating to `localhost:8080` in your browser. By default, the proxy will send a get 
request to www.google.com
1. To navigate to a different url, use the `url` query parameter. For instance, if you wanted to visit Facebook, you 
would visit `localhost:8080/?url=http://www.facebook.com`.
1. You can also add a `range` query parameter which will be sent as a header to the url you are trying to visit. 
eg `localhost:8080/?url=http://www.facebook.com&range=bytes:0-999`
1. To get statistics on how long the proxy has been running and the number of bytes transferred, you can visit 
`localhost:8080/stats`
1. Tests are in tests.py. You can run them by first running `pip install -r requirements.txt` and then `pytest tests.py`

## Limitations
1. The proxy only handles get requests as of now.
1. The stats available at `/stats` are only for the current run of the proxy. It could be improved so that stats persist
even after the proxy has been brought down and then back up again.
1. Due to some aiohttp limitations, some headers have to be removed from the request and the response unfortunately.