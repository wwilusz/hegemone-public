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

    run_notebook(args.notebook, parameters, out_notebook_fp=args.output_notebook, kernel_name=args.kernel_name)
