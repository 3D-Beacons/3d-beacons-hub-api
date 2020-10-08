import click


@click.group("CLI", help="CLI application for 3d-Beacons Hub API")
def main():
    """The main CLI application

    Returns:
        int: An integer value as exit status.
    """
    return 0
