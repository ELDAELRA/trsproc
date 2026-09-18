from typer.testing import CliRunner

from trsproc.cli import app


def invoke(*args):
    """Small helper to reduce boilerplate (path objects need to be converted to strings)"""
    runner = CliRunner()
    return runner.invoke(app, [str(arg) for arg in args])
