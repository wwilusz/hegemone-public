import papermill as pm
import multiprocessing as mp
import yaml
import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path


def run_notebook(template_notebook, parameters, out_notebook_fp=None, kernel_name='Python3'):
    """
    Executes the notebook using the papermill lib and externally provided parameters.

    Parameters
    ----------
    template_notebook : str
        A file path to the notebook which is to be executed
    parameters: dict
        A dictionary containing parameters necessary to run the template notebook
    out_notebook_fp : str
        A file path to the resulting (executed) notebook
    kernel_name : str
       Jupyter kernel name to be used for execution

    Returns
    -------
    None
    """
    print("Running the {} notebook".format(template_notebook))

    if not out_notebook_fp:
        out_notebook_fp = get_output_notebook_path(template_notebook, gcs_bucket=None)

    # making sure that the output directory exists
    executed_notebook_dir = os.path.split(out_notebook_fp)[0]
    Path(executed_notebook_dir).mkdir(parents=True, exist_ok=True)

    print("  - destination: {}".format(out_notebook_fp))

    try:
        pm.execute_notebook(
            template_notebook,
            out_notebook_fp,
            parameters,
            kernel_name=kernel_name)
    except Exception as e:
        print("ERROR FOR: {}".format(out_notebook_fp))
        print(e)
        raise


def get_output_notebook_path(template_notebook, gcs_bucket=None):
    """
    Provides a default path to an output notebook based on the provided parameters

    Parameters
    ----------
    template_notebook : str
        A file path to the notebook which is to be executed
    gcs_bucket : str
        GCS bucket URI

    Returns
    -------
    str
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
    process_id = mp.current_process().pid
    prefix = '{}-'.format(timestamp)
    postfix = '{}'.format(process_id)
    print("  - process id: {}".format(process_id))

    template_notebook_dir, template_notebook_fn = os.path.split(template_notebook)
    if gcs_bucket:
        executed_notebook_dir = gcs_bucket
    else:
        executed_notebook_dir = "./executed/"
    executed_notebook_fn = template_notebook_fn.replace('template', postfix)
    executed_notebook_fn = '{}{}'.format(prefix, executed_notebook_fn)
    out_notebook_fp = os.path.join(executed_notebook_dir, executed_notebook_fn)

    return out_notebook_fp

def get_flags():
    import base64
    with open("etc/config.yml", "r") as fin:
        prms = fin.read()
    return base64.b64encode(prms.encode()).decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs template notebooks.')

    parser.add_argument('notebook', help='A path to a jupyter notebook to be executed', type=str)
    parser.add_argument('-p', '--parameters_file', help='A path to a yaml file containing parameters for execution',
                        default='./parameters.yaml', type=str)
    parser.add_argument('-s', '--parameters_section', help='A parameters section to use from the parameters file',
                        default='project', type=str)
    parser.add_argument('-o', '--output_notebook', help='A file path to the resulting (executed) notebook',
                        default=None)
    parser.add_argument('-k', '--kernel_name', help='Jupyter kernel name to be used for execution', default='Python3',
                        type=str)
    parser.add_argument('-gcp', '--google_cloud_platform', help='If present, the notebook will be executed using a '
                                                                'service running on Cloud Run; results will be uploaded'
                                                                ' to GCS_BUCKET',
                        action='store_true')
    args = parser.parse_args()

    # loading the YAML file with parameters
    try:
        with open(args.parameters_file) as parameters_file:
            parameters_dict = yaml.load(parameters_file, Loader=yaml.FullLoader)
    except Exception as e:
        print("ERROR related to {}\n".format(args.parameters_file))
        raise

    # retrieving parameters
    try:
        parameters_key = args.parameters_section
        parameters = parameters_dict[parameters_key]
    except KeyError:
        print("ERROR: No {} section in {}\n".format(parameters_key, args.parameters_file))
        raise

    if args.google_cloud_platform:
        if args.output_notebook:
            out_notebook_fp = args.output_notebook
        else:
            out_notebook_fp = get_output_notebook_path(args.notebook,
                                                       gcs_bucket=parameters_dict['google-cloud-platform']['GCS_BUCKET'])
        print("  - destination: {}".format(out_notebook_fp))
        print('Calling Cloud Run hegemone service')
        # obtain details about the service
        command = "gcloud run services describe cloud-run-hegemone --format='value(status.url)' --region us-central1 " \
                  "--platform managed"
        url = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        url = url.stdout.decode("utf-8").replace('\n','')

        command = "gcloud auth print-identity-token"
        auth_token = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        auth_token = auth_token.stdout.decode("utf-8").replace('\n','')

        #todo: mirror the run.py's functionality with curl; send out parameters.yaml
        run_notebook_command = 'python run.py {IN_NOTEBOOK} -o {OUT_NOTEBOOK}'.format(IN_NOTEBOOK=args.notebook,
                                                                                      OUT_NOTEBOOK=out_notebook_fp)

        # execute the notebook
        run_notebook_command = 'python run.py {IN_NOTEBOOK} -o {OUT_NOTEBOOK} -s {PARAMETERS_SECTION} -k {KERNEL_NAME}'.\
            format(IN_NOTEBOOK=args.notebook,
                   OUT_NOTEBOOK=out_notebook_fp,
                   PARAMETERS_SECTION=args.parameters_section,
                   KERNEL_NAME=args.kernel_name)
        flags = get_flags()

        command = 'curl --request POST --header "Authorization: Bearer {TOKEN}" --header "Content-Type: text/plain" --data parameters="{FLAGS}" ' \
                  '{URL}/exec --data-binary " {COMMAND}"'.format(TOKEN=auth_token, URL=url, COMMAND=run_notebook_command, FLAGS=flags)
        curl = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Process complete")
    else:
        run_notebook(args.notebook, parameters, out_notebook_fp=args.output_notebook, kernel_name=args.kernel_name)
