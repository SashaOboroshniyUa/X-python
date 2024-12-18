from flask import Flask, render_template
import psutil #для зв'язку з пристроєм
import matplotlib #для 9 строчки
import matplotlib.pyplot as plt #для того щоб використовувати matplotlib
import re #реплейс 2.0
import os #для зноса вінди щоб переходили на лінукс

app = Flask(__name__)

matplotlib.use("Agg")

os.makedirs("static/images", exist_ok=True) #шадавро путь


def create_ram_diagram(): #графік використання RAM
    memory = psutil.virtual_memory()
    labels = ["Використанно", "Вільно"]
    sizes = [memory.used, memory.available]
    colors = ["#ff9999", "#66b3ff"]
    plt.figure(figsize=(6, 4))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    plt.title("Використання пам'яті")
    plt.axis("equal")
    plt.savefig("static/images/memory_usage.png")
    plt.close()


def create_disk_diagram():  # Графіки для всіх дисків
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            disk = psutil.disk_usage(partition.mountpoint)
            labels = ["Зайнято", "Вільно"]
            sizes = [disk.used, disk.free]
            colors = ["#ffcc99", "#99ff99"]
            plt.figure(figsize=(6, 4))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
            plt.title(f"Диск {partition.device} ({partition.mountpoint})")
            plt.axis("equal")

            safe_device_name = re.sub(r'[\\/:"<>|]', '', partition.device)
            filename = f"static/images/disk_usage_{safe_device_name}.png"

            plt.savefig(filename)
            plt.close()
        except Exception as error:
            print(f"Не вдалося створити діаграму для {partition.device}: {error}")


@app.get("/")
def index():
    create_ram_diagram()
    create_disk_diagram()

    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    partitions = psutil.disk_partitions()
    disks_info = []
    for partition in partitions:
        try:
            disk = psutil.disk_usage(partition.mountpoint)
            disks_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "total": disk.total / (1024 ** 3),
                "used": disk.used / (1024 ** 3),
                "free": disk.free / (1024 ** 3),
            })
        except Exception as error:
            print(f"Не вдалося отримати дані для {partition.device}: {error}")

    return render_template("index.html",
                           cpu_usage=cpu_usage,
                           memory_total=memory.total / (1024 ** 3),
                           disks_info=disks_info)


if __name__ == "__main__":
    app.run(debug=True)

