import queue
import threading

from ingestor import Ingestor
from log import logger
from scheduler import Scheduler

if __name__ == "__main__":
    logger.info("Starting..")
    shared_queue = queue.Queue()

    scheduler = Scheduler(shared_queue)
    ingestor = Ingestor(shared_queue)

    scheduler_thread = threading.Thread(target=scheduler.start)
    ingestor_thread = threading.Thread(target=ingestor.start)

    try:
        scheduler_thread.start()
        ingestor_thread.start()
        scheduler_thread.join()
        ingestor_thread.join()

    except KeyboardInterrupt:
        scheduler.stop()
        ingestor.stop()
        scheduler_thread.join()
        ingestor_thread.join()
