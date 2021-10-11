import click
import sys
import os




@click.command()
@click.option('-l', '--lines', default=0, required=False, help='Count of last messages which should be printed')
def main(lines):
    """Show current log"""
    ret = 0

    if lines > 0:
    	ret = os.system("logread -l " + str(lines))
    else:
    	ret = os.system("logread")

    sys.exit(ret)
