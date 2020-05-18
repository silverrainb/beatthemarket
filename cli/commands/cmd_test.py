import os
import subprocess

import click


@click.command()
@click.argument('path', default=os.path.join('beatthemarket', 'tests'))
def cli(path):
    """
    Run tests with Pytest.

    :param path: Test path
    :return: Subprocess call result
    """
    cmd = f"py.test {path}"
    return subprocess.call(cmd, shell=True)
