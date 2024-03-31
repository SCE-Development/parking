import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        default="localhost",
        help="host for server to listen on, defaults to localhost"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port for server to be hosted on, defaults to 8000"
    )

    parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="increase logging verbosity; can be used multiple times in a chain such as '-vvv'",
    )

    parser.add_argument(
        "--dbfile",
        default="parking.db",
        help="sqlite3 database file to store parking data"
    )


    return parser.parse_args()