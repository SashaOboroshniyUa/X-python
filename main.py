import psutil
from tabulate import tabulate

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "Всего": f"{memory.total / (1024 ** 3):.2f} ГБ",
        "Используется": f"{memory.used / (1024 ** 3):.2f} ГБ",
        "Свободно": f"{memory.available / (1024 ** 3):.2f} ГБ",
        "Процент использования": f"{memory.percent}%"
    }

def get_disk_usage():
    disk_partitions = psutil.disk_partitions()
    disks_info = []
    for partition in disk_partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks_info.append([
                partition.device,
                partition.mountpoint,
                f"{usage.total / (1024 ** 3):.2f} ГБ",
                f"{usage.used / (1024 ** 3):.2f} ГБ",
                f"{usage.free / (1024 ** 3):.2f} ГБ",
                f"{usage.percent}%"
            ])
        except PermissionError:
            continue
    return disks_info

def get_top_processes(n=10):
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                       key=lambda x: x.info['cpu_percent'],
                       reverse=True)[:n]:
        try:
            processes.append([
                proc.info['pid'],
                proc.info['name'],
                f"{proc.info['cpu_percent']:.2f}%",
                f"{proc.info['memory_percent']:.2f}%"
            ])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return processes

def main():
    print("=== Мониторинг системы ===")

    print(f"\nЗагрузка CPU: {get_cpu_usage()}%")

    print("\nИспользование памяти:")
    for key, value in get_memory_usage().items():
        print(f"{key}: {value}")

    print("\nДиски:")
    disk_usage = get_disk_usage()
    print(tabulate(disk_usage, headers=['Устройство', 'Точка монтирования', 'Всего', 'Занято', 'Свободно', 'Загрузка %'], tablefmt='grid'))

    print("\nТоп процессов по использованию CPU:")
    top_processes = get_top_processes()
    print(tabulate(top_processes,
                   headers=['PID', 'Название', 'CPU %', 'Память %'],
                   tablefmt='grid'))

if __name__ == '__main__':
    main()
