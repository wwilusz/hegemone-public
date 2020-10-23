import papermill as pm
import multiprocessing as mp
import yaml
import argparse
import os
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
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
    process_id = mp.current_process().pid
    prefix = '{}-'.format(timestamp)
    postfix = '{}'.format(process_id)
    print("  - process id: {}".format(process_id))

    if not out_notebook_fp:
        template_notebook_dir, template_notebook_fn = os.path.split(template_notebook)
        executed_notebook_dir = "./executed/"
        executed_notebook_fn = template_notebook_fn.replace('template', postfix)
        executed_notebook_fn = '{}{}'.format(prefix, executed_notebook_fn)
        out_notebook_fp = os.path.join(executed_notebook_dir, executed_notebook_fn)

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

if __name__ == "__main__":

    # loading config
    config_file = './config.yaml'
    try:
        with open(config_file) as config_file:
            config_dict = yaml.load(config_file, Loader=yaml.FullLoader)
    except Exception as e:
        print("ERROR related to {}\n".format(config_file))
        raise

    # loading the YAML file with parameters
    try:
        with open(config_dict['parameters_file']) as parameters_file:
            parameters_dict = yaml.load(parameters_file, Loader=yaml.FullLoader)
    except Exception as e:
        print("ERROR related to {}\n".format(config_dict['parameters_file']))
        raise

    # retrieving parameters
    try:
        parameters_key = config_dict['parameters_section']
        parameters = parameters_dict[parameters_key]
    except KeyError:
        print("ERROR: No {} section in {}\n".format(parameters_key, config_dict['parameters_file']))
        raise

    run_notebook(config_dict['notebook'],
                 parameters,
                 out_notebook_fp=config_dict['output_notebook'],
                 kernel_name=config_dict['kernel_name'])