import multiprocessing
multiprocessing.set_start_method('spawn', force=True)

from airflow.cli.commands.celery_command import celery_worker
from airflow.utils.cli import setup_locations

if __name__ == "__main__":
    setup_locations()
    celery_worker()

