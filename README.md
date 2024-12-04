
# websockets-connect4

Implementation of tutorial @ https://websockets.readthedocs.io/en/stable/intro/

# install

Installation is the usual
```sh
kenneth@x1:~/git/websockets-connect4 (main)$ python --version
Python 3.11.0rc1
kenneth@x1:~/git/websockets-connect4 (main)$ python -m venv venv3.11
kenneth@x1:~/git/websockets-connect4 (main)$ source ./venv3.11/bin/activate
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ which pip
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ pip install -r requirements.txt
```
The only requirement for the python server is `websockets`

# run localhost dev environment

Running the app server locally is as simple as
```sh
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ ./app.py
Using selector: EpollSelector
server listening on 0.0.0.0:8001
server listening on [::]:8001
```
And using Python's built-in HTTP server for local dev:
```sh
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ python -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```
For development, you will want both to run in the foreground, so leave those
running in separate terminals.

