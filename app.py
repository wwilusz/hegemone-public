import os
import subprocess
import base64
import yaml
from flask import Flask, request, make_response

def parse_params(cmd_string, save_to, verify=False):
    cmds = cmd_string.split(" ")

    prms = [c for c in cmds if c.startswith("parameters=")]
    if len(prms) == 1:
        cmds.remove(prms[0])
        prms = prms[0].replace("parameters=", "")
        with open(save_to, "w") as fout:
            fout.write(base64.b64decode(prms).decode())

        if verify:
            with open(save_to, "r") as fout:
                yaml.load(fout)

    return " ".join(cmds)

print("Started...")
app = Flask(__name__)


@app.route('/')
def func1():
    print("Running")
    return "Hello World"


@app.route('/exec', methods=['POST'])
def route_exec():
    command = request.data.decode('utf-8')

    command = parse_params(command, save_to="config.yml", verify=True)
    if os.path.exists("config.yml"):
        print(f"Config file written to 'config.yml'")

    try:
        completedProcess = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          timeout=1000, universal_newlines=True)
        response = make_response(completedProcess.stdout, 200)
        response.mimetype = "text/plain"
        return response
    except subprocess.TimeoutExpired:
        response = make_response("Timedout", 4000)
        response.mimetype = "text/plain"
        return response
    return "/exec"


@app.route("/save_file", methods=['POST', 'PUT'])
def save_file():
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('./', filename))
    return filename


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
