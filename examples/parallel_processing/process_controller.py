"""
Process lifecycle management controller, the main purpose of such controller will accept requests from the client, transform incoming batch requests to multiple parallel process inside, and execute those processes to initialize associated job and distributed to multiple backend server considering the workload even & request reliable, the controller will keep monitoring the job result, respond to client, handle the error exception and recycle the process resource. 

Sample below only demonstrates the basic concept of how to manage the process lifecycle, it's not a complete solution, the real-world scenario will be more complex and need to consider more factors like the process resource limitation, the process priority, the process dependency, the process retry etc. it mainly focus on the process state transition and managament in parallel processing.

Below are Mermaid state diagram illustrating the transitions between these Linux process states:
stateDiagram-v2
    [*] --> Running
    Running --> InterruptibleSleep
    Running --> UninterruptibleSleep
    Running --> Stopped
    Running --> Zombie
    InterruptibleSleep --> Running
    UninterruptibleSleep --> Running
    Stopped --> Running
    Zombie --> [*]
"""
import multiprocessing
import queue
import time
import random
from enum import Enum

class ProcessState(Enum):
    RUNNING = 'Running'
    INTERRUPTIBLE_SLEEP = 'InterruptibleSleep'
    UNINTERRUPTIBLE_SLEEP = 'UninterruptibleSleep'
    STOPPED = 'Stopped'
    ZOMBIE = 'Zombie'
    COMPLETED = 'Completed'  # Added state
    FAILED = 'Failed'        # Added state

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

    def run(self):
        while True:
            try:
                job = self.task_queue.get(timeout=1)
                
                # Simulate job processing with state transitions
                while job.state not in [ProcessState.ZOMBIE, ProcessState.COMPLETED, ProcessState.FAILED]:
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
                        job.state = ProcessState.COMPLETED
                    
                    elif transition == 'continue':
                        continue
                    
                    elif transition == 'fail':
                        job.state = ProcessState.FAILED
                        job.error = "Job encountered an error"
                        break

            except queue.Empty:
                break
            finally:
                self.result_queue.put(job)

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
        print(f"job_id: {job_id}, job exists: {job is not None}")
        if job:
            return job.state
        return None

    def get_job_result(self, job_id):
        job = self.jobs.get(job_id)
        if job and job.state == ProcessState.COMPLETED:
            return job.result
        return None

    def get_job_error(self, job_id):
        job = self.jobs.get(job_id)
        if job and job.state == ProcessState.FAILED:
            return job.error
        return None

    def monitor_jobs(self):
        completed_jobs = []
        while True:
            try:
                job = self.result_queue.get(timeout=1)
                if job.state == ProcessState.COMPLETED:
                    completed_jobs.append(job.job_id)
                elif job.state == ProcessState.FAILED:
                    print(f"Job {job.job_id} failed: {job.error}")
                    if job.job_id in self.jobs: # Check if job_id is still in the dictionary
                        del self.jobs[job.job_id] # Safely delete the job
                # handle the other states TBD
            except queue.Empty:
                break
        
        for job_id in completed_jobs:
            if job_id in self.jobs: # Check if job_id is still in the dictionary
                del self.jobs[job_id] # Safely delete the job

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
            if status == ProcessState.COMPLETED:
                result = controller.get_job_result(job_id)
                print(f"Job {job_id} completed. Result: {result}")
                job_ids.remove(job_id)
            elif status == ProcessState.FAILED:
                error = controller.get_job_error(job_id)
                print(f"Job {job_id} failed. Error: {error}")
                job_ids.remove(job_id)
            # handle if the status is None
            elif status is None:
                print(f"Job {job_id} status is None")
                job_ids.remove(job_id)
        
        controller.monitor_jobs()
        time.sleep(1)

    controller.stop()
