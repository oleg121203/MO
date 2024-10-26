import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="My project")
    args = vars(parser.parse_args())
    return args