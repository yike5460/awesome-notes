import multiprocessing
import queue
import time
import random
import psutil
from enum import Enum

class ProcessState(Enum):
    RUNNING = 'Running'
    INTERRUPTIBLE_SLEEP = 'InterruptibleSleep'
    UNINTERRUPTIBLE_SLEEP = 'UninterruptibleSleep'
    STOPPED = 'Stopped'
    ZOMBIE = 'Zombie'

class Job:
    def __init__(self, job_id, task):
        self.job_id = job_id
        self.task = task
        self.state = ProcessState.RUNNING
        self.result = None
        self.error = None

class Worker(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    def sim_run(self):
        while True:
            try:
                job = self.task_queue.get(timeout=1)
                
                # Simulate job processing with state transitions
                while job.state != ProcessState.ZOMBIE:
                    time.sleep(random.uniform(0.5, 1.5))  # Simulate work
                    transition = random.choice(['sleep', 'stop', 'zombie', 'continue', 'fail'])
                    
                    if transition == 'sleep':
                        job.state = ProcessState.INTERRUPTIBLE_SLEEP
                        time.sleep(random.uniform(0.5, 1.5))  # Simulate sleep
                        job.state = ProcessState.RUNNING
                    
                    elif transition == 'stop':
                        job.state = ProcessState.STOPPED
                        time.sleep(random.uniform(0.5, 1.5))  # Simulate being stopped
                        job.state = ProcessState.RUNNING
                    
                    elif transition == 'zombie':
                        job.state = ProcessState.ZOMBIE
                        job.result = f"Result for job {job.job_id}"
                    
                    elif transition == 'continue':
                        continue
                    
                    elif transition == 'fail':
                        job.state = ProcessState.ZOMBIE
                        job.error = "Job encountered an error"
                        break

            except queue.Empty:
                break
            finally:
                self.result_queue.put(job)

    def run(self):
        while True:
            try:
                job = self.task_queue.get(timeout=1)

                # Create a new process for the job
                process = multiprocessing.Process(target=self.process_job, args=(job,))
                process.start()

                # Monitor the process state
                while True:
                    try:
                        status = psutil.Process(process.pid).status()
                        if status == psutil.STATUS_RUNNING:
                            job.state = ProcessState.RUNNING
                        elif status == psutil.STATUS_SLEEPING:
                            job.state = ProcessState.INTERRUPTIBLE_SLEEP
                        elif status == psutil.STATUS_DISK_SLEEP:
                            job.state = ProcessState.UNINTERRUPTIBLE_SLEEP
                        elif status == psutil.STATUS_STOPPED:
                            job.state = ProcessState.STOPPED
                        elif status == psutil.STATUS_ZOMBIE:
                            job.state = ProcessState.ZOMBIE
                            break
                        else:
                            # Handle other states if needed
                            pass

                        time.sleep(1)

                    except psutil.NoSuchProcess:
                        # Process no longer exists
                        break

                # Wait for the process to finish and get the result or error
                process.join()
                if job.error is None:
                    job.result = f"Result for job {job.job_id}"

            except queue.Empty:
                break
            finally:
                self.result_queue.put(job)

    def process_job(self, job):
        try:
            # Simulate job processing
            time.sleep(random.uniform(1, 5))

            # Simulate an error in some cases
            if random.random() < 0.1:
                raise Exception(f"Job {job.job_id} encountered an error")

        except Exception as e:
            job.error = str(e)

class ProcessLifecycleController:
    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.jobs = {}
        self.workers = []

    def start(self):
        for _ in range(self.num_workers):
            worker = Worker(self.task_queue, self.result_queue)
            worker.start()
            self.workers.append(worker)

    def submit_job(self, task):
        job_id = len(self.jobs)
        job = Job(job_id, task)
        self.jobs[job_id] = job
        self.task_queue.put(job)
        return job_id

    def get_job_status(self, job_id):
        job = self.jobs.get(job_id)
        if job:
            return job.state
        return None

    def get_job_result(self, job_id):
        job = self.jobs.get(job_id)
        if job and job.state == ProcessState.ZOMBIE and job.result is not None:
            return job.result
        return None

    def get_job_error(self, job_id):
        job = self.jobs.get(job_id)
        if job and job.state == ProcessState.ZOMBIE and job.error is not None:
            return job.error
        return None

    def monitor_jobs(self):
        completed_jobs = []
        while True:
            try:
                job = self.result_queue.get(timeout=1)
                if job.state == ProcessState.ZOMBIE:
                    if job.error is None:
                        completed_jobs.append(job.job_id)
                    else:
                        print(f"Job {job.job_id} failed: {job.error}")
                        if job.job_id in self.jobs:
                            del self.jobs[job.job_id]
            except queue.Empty:
                break
        
        for job_id in completed_jobs:
            if job_id in self.jobs:
                del self.jobs[job_id]

    def stop(self):
        for worker in self.workers:
            worker.terminate()
        self.workers.clear()

# Usage example
if __name__ == "__main__":
    controller = ProcessLifecycleController(num_workers=5)
    controller.start()

    # Submit jobs
    job_ids = []
    for i in range(10):
        job_id = controller.submit_job(f"Task {i}")
        job_ids.append(job_id)

    # Monitor job status and results
    while job_ids:
        for job_id in job_ids:
            status = controller.get_job_status(job_id)
            print(f"Job {job_id} status: {status}")
            if status == ProcessState.ZOMBIE:
                result = controller.get_job_result(job_id)
                if result is not None:
                    print(f"Job {job_id} completed. Result: {result}")
                    job_ids.remove(job_id)
                else:
                    error = controller.get_job_error(job_id)
                    print(f"Job {job_id} failed. Error: {error}")
                    job_ids.remove(job_id)
            elif status is None:
                print(f"Job {job_id} status is None")
                job_ids.remove(job_id)
        
        controller.monitor_jobs()
        time.sleep(1)

    controller.stop()
