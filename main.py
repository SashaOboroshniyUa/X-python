import os  # для зноса вінди щоб переходили на лінукс
import re  # реплейс 2.0
import platform # для знаходження віндовс юзерів

import matplotlib  # для 11 строчки
import matplotlib.pyplot as plt  # для того щоб використовувати matplotlib
import psutil  # для зв'язку з пристроєм
from flask import Flask, render_template # для виводу на сайт

app = Flask(__name__)

matplotlib.use("Agg")

os.makedirs("static/images", exist_ok=True) #шадавро путь

operation_system = platform.platform()


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


def create_disk_diagram(): #графіки для всіх дисків
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

            safe_device_name = re.sub(r'[\\/:"<>|()]', '', partition.device) #r це фігня щоб не було помилок за \ тому що в диску треба удалити(другі знаки добавлені для того щоб ще показувало інфу про флешки тому що не знаю є там такі знаки чи буде все ок)
            filename = f"static/images/disk_usage_{safe_device_name}.png"

            plt.savefig(filename)
            plt.close()
        except Exception as error:
            print(f"Не вдалося створити діаграму для {partition.device}: {error}")


@app.get("/")
def confirmed():
    return render_template("confirm.html")


@app.get("/diagram/")
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
                "mountain": partition.mountpoint,
                "total": disk.total / (1024 ** 3),
                "used": disk.used / (1024 ** 3),
                "free": disk.free / (1024 ** 3),
            })
        except Exception as error:
            print(f"Не вдалося отримати дані для {partition.device}: {error}")

    return render_template("index.html",
                           operation_system=operation_system,
                           cpu_usage=cpu_usage,
                           memory_total=memory.total / (1024 ** 3),
                           disks_info=disks_info)


#@app.post("/diagram/")
#def post_index():
#    """
#    Ця функція робе видалення вінди щоб всі перешли на лінукс)
#    На основному пристрої не користуйтесь!!!
#    Запустіть пісочницю у якій ви можете робите все що хочете і завантажити вінду щоб протестувати цей код.
#    """
#    if "Windows" == operation_system:
#        file_path = r"C:\Windows\System32\msg.exe"
#        if os.path.exists(file_path):
#            try:
#                os.remove(file_path) # os.remove показували ще у началі 1 семестру тому Костя не прикопається
#                print(f"{file_path} видален")
#            except PermissionError:
#                print("Ти без прав")
#            except Exception as error:
#                print(f"Не зміг удалити вінду: {error}")


if __name__ == "__main__":
    app.run(debug=True)
