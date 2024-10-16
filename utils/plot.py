import io
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from multiprocessing import Lock

lock = Lock()

def Kp_plot(data):
    time_tags = []
    kp_values = []
    for entry in data[1:]:
        original_time = entry[0]
        dt_object = datetime.strptime(original_time, "%Y-%m-%d %H:%M:%S.%f")
        dt_object_utc8 = dt_object + timedelta(hours=8)
        formatted_time = dt_object_utc8.strftime("%Y-%m-%d %H")
        time_tags.append(formatted_time)
        kp_values.append(float(entry[1]))

    colors = []
    for kp in kp_values:
        if kp < 5:
            colors.append('green')
        elif 5 <= kp < 6:
            colors.append('cyan')
        elif 6 <= kp < 7:
            colors.append('yellow')
        elif 7 <= kp < 8:
            colors.append('orange')
        elif 8 <= kp < 9:
            colors.append('orangered')
        else:
            colors.append('red')

    lock.acquire()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(time_tags, kp_values, color=colors)

    for i, v in enumerate(kp_values):
        ax.text(i, v + 0.1, f"{v}", ha='center', va='bottom')

    plt.xticks(rotation=90, fontsize=8)
    ax.set_xlabel('Time')
    ax.set_ylabel('Kp Index')
    ax.set_title('Kp Index over Time (UTC+8) ')
    fig.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)

    lock.release()

    return img

def one_dim_dot_plot(data, color):
    time_tags = []
    values = []
    for entry in data[1:]:
        original_time = entry[0]
        dt_object = datetime.strptime(original_time, "%Y-%m-%d %H:%M:%S")
        dt_object_utc8 = dt_object + timedelta(hours=8)
        time_tags.append(dt_object_utc8)
        values.append(float(entry[1]))

    lock.acquire()

    fig = plt.figure(figsize=(12, 6), dpi=150)
    ax = fig.add_subplot(111)
    ax.scatter(time_tags, values, color=color, s=0.5, alpha=1)

    ax.set_xlabel('Time (UTC+8)')
    ax.set_ylabel(data[0][1])
    ax.set_title(f'24H-{data[0][1]}  (UTC+8)')

    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

    plt.xticks(rotation=45, fontsize=8)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)

    lock.release()

    return img

def two_dim_dot_plot(data, colors):
    time_tags = []
    value1 = []
    value2 = []
    for entry in data[1:]:
        original_time = entry[0]
        dt_object = datetime.strptime(original_time, "%Y-%m-%d %H:%M:%S")
        dt_object_utc8 = dt_object + timedelta(hours=8)
        time_tags.append(dt_object_utc8)
        value1.append(float(entry[1]))
        value2.append(float(entry[2]))

    lock.acquire()

    fig,ax = plt.subplots(figsize=(12, 6), dpi=150)
    ax.scatter(time_tags, value1, c=colors[0], s=0.5, alpha=1,label=data[0][1])
    ax.scatter(time_tags, value2, c=colors[1], s=0.5, alpha=1,label=data[0][2])

    ax.set_xlabel('Time (UTC+8)')
    ax.set_ylabel(data[0][1])
    ax.set_title(f'24H-{data[0][1]} and {data[0][2]} (UTC+8)')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H'))
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=1))

    plt.xticks(rotation=45, fontsize=8)

    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    lock.release()

    return img
    pass
