
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
The only requirement for the python server is `websockets`, `requirements.txt`
also lists some testing & dev tooling.

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

## OPTIONAL: serve dev env using GNU screen

A GNU screen config file is included if it annoys you to have to dedicate two
terminals to serving the dev env, start it with:
```sh
kenneth@x1:~/git/websockets-connect4 (main)$ screen -c ./devserv.screenrc
```
Note, the screen config takres care of activating the venv when required (and
the path to the `venv3.11` directory created above is hardcoded in the config)

Use `Ctrl-a :quit` to exit a screen session, `Ctrl-a d` to detach, etc.  See
the manual at https://www.gnu.org/software/screen/manual/screen.html

# testing
Currently there are just a few doctests for the Python code

Make sure the venv is activated and the correct pytest is found
```sh
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ which pytest
/home/kenneth/git/websockets-connect4/venv3.11/bin/pytest
```
Run the tests
```sh
(venv3.11) kenneth@x1:~/git/websockets-connect4 (main)$ pytest -v --doctest-modules .
```

