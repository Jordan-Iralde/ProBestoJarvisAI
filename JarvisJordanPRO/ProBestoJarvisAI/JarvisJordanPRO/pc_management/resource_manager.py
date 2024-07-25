import psutil

def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    return {'cpu': cpu, 'memory': memory}
