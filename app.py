# app.py
import base64
import math
import os
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from io import BytesIO

import aacgmv2
import geocoder
from flask import Flask, jsonify, render_template, send_file, Response
import requests

from utils.plot import Kp_plot, one_dim_dot_plot, two_dim_dot_plot

app = Flask(__name__)

def image_to_base64(image_bytes):
    base64_img = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{base64_img}"

def fetch_image(entry, index):
    pic_url = f'https://services.swpc.noaa.gov/{entry["url"]}'
    try:
        pic_req = requests.get(pic_url, timeout=10)
        if pic_req.status_code == 200:
            return index, pic_req.content
    except requests.RequestException:
        return index, None
    return index, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solar_wind', methods=['GET'])
def get_solar_wind():
    solar_wind_speed_url = 'https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json'
    solar_wind_mag_field_url = 'https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json'

    speed_res = requests.get(solar_wind_speed_url)
    mag_field_res = requests.get(solar_wind_mag_field_url)

    if speed_res.status_code == 200 and mag_field_res.status_code == 200 :
        try:
            wind_speed = speed_res.json().get('WindSpeed')
        except AttributeError:
            wind_speed = 'N/A'
        try:
            Bt, Bz = mag_field_res.json().get('Bt', 'N/A'), mag_field_res.json().get('Bz', 'N/A')
        except AttributeError:
            Bt, Bz = 'N/A', 'N/A'
        result = {
            'wind_speed': wind_speed,
            'bt': Bt,
            'bz': Bz,
        }
        return jsonify(result), 200
    return jsonify({'error': 'Unable to fetch content'}), 404

@app.route('/Kp_image', methods=['GET'])
def get_Kp_image():
    Kp_png_url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
    Kp_png_res = requests.get(Kp_png_url)
    if Kp_png_res.status_code == 200:
        Kp = Kp_plot(Kp_png_res.json())
        return send_file(Kp, mimetype='image/png')
    return jsonify({'error': 'Unable to fetch content'}), 404

@app.route('/plasma', methods=['GET'])
def get_plasma():
    plasma_url = 'https://services.swpc.noaa.gov/text/rtsw/data/plasma-1-day.i.json'
    plasma_res = requests.get(plasma_url)
    if plasma_res.status_code == 200:
        speed_data = [["time_tag", "speed"]]
        density_data = [["time_tag", "density"]]
        temperature_data = [["time_tag", "temperature"]]
        for entry in plasma_res.json()[1:]:
            time_tag = entry[0]
            speed = entry[1]
            density = entry[2]
            temperature = entry[3]
            speed_data.append([time_tag, speed])
            density_data.append([time_tag, density])
            temperature_data.append([time_tag, temperature])

        speed_image = one_dim_dot_plot(speed_data, 'purple')
        density_image = one_dim_dot_plot(density_data, 'orange')
        temperature_image = one_dim_dot_plot(temperature_data, 'green')

        return jsonify({
            'speed_image': image_to_base64(speed_image),
            'density_image': image_to_base64(density_image),
            'temperature_image': image_to_base64(temperature_image),
        })

    else:
        return jsonify({'error': 'Unable to fetch content'}), 404

@app.route('/mag')
def get_mag():
    mag_url = 'https://services.swpc.noaa.gov/text/rtsw/data/mag-1-day.i.json'
    utc_time = datetime.now(timezone.utc)
    ae_url = f'https://wdc.kugi.kyoto-u.ac.jp/ae_realtime/today/rtae_{utc_time.year}{utc_time.month}{utc_time.day}.png'
    mag_res = requests.get(mag_url)
    ae_res = requests.get(ae_url)

    if mag_res.status_code == 200 and ae_res.status_code == 200 :
        data = [["time_tag", "Bt", "Bz"]]
        phi_data = [["time_tag", "Phi"]]
        for entry in mag_res.json()[1:]:
            time_tag = entry[0]
            Bt = entry[1]
            Bz = entry[4]
            Phi = entry[6]
            data.append([time_tag, Bt, Bz])
            phi_data.append([time_tag, Phi])
        mag_image = two_dim_dot_plot(data, ['red', 'black'])
        phi_image = one_dim_dot_plot(phi_data, 'blue')
        ae_image = BytesIO(ae_res.content)

        return jsonify({
            'mag_image': image_to_base64(mag_image),
            'phi_image': image_to_base64(phi_image),
            'ae_image' : image_to_base64(ae_image)
        })
    return jsonify({'error': 'Unable to fetch content'}), 404


def get_lascoc3():
    req_url = 'https://services.swpc.noaa.gov/products/animations/lasco-c3.json'

    try:
        req_res = requests.get(req_url, timeout=10)
        req_res.raise_for_status()
        data = req_res.json()
    except requests.RequestException as e:

        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'Failed to load LASCO C3 data: ' + str(e).encode('utf-8') + b'\r\n')
        return

    images = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_image, entry, idx): idx for idx, entry in enumerate(data)}

        for future in as_completed(futures):
            index, result = future.result()
            if result:
                images.append((index, result))

    images.sort(key=lambda x: x[0])

    if not images:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'No LASCO C3 images available.\r\n')
        return

    image_contents = [img[1] for img in images]

    while True:
        for image in image_contents:
            try:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                time.sleep(0.15)
            except GeneratorExit:
                return
            except Exception as e:
                continue
@app.route('/stream_lascoc3')
def stream_lascoc3():
    return Response(get_lascoc3(), mimetype='multipart/x-mixed-replace; boundary=frame')


def get_lascoc2():
    req_url = 'https://services.swpc.noaa.gov/products/animations/lasco-c2.json'

    try:
        req_res = requests.get(req_url, timeout=10)
        req_res.raise_for_status()
        data = req_res.json()
    except requests.RequestException as e:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'Failed to load LASCO C2 data: ' + str(e).encode('utf-8') + b'\r\n')
        return

    images = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_image, entry, idx): idx for idx, entry in enumerate(data)}

        for future in as_completed(futures):
            index, result = future.result()
            if result:
                images.append((index, result))

    images.sort(key=lambda x: x[0])

    if not images:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'No LASCO C2 images available.\r\n')
        return

    image_contents = [img[1] for img in images]

    while True:
        for image in image_contents:
            try:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                time.sleep(0.15)
            except GeneratorExit:
                return
            except Exception as e:
                continue

@app.route('/stream_lascoc2')
def stream_lascoc2():
    return Response(get_lascoc2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/3-day forecast')
def three_day_forecast():
    forecast_url = 'https://services.swpc.noaa.gov/text/3-day-forecast.txt'
    forecast_req = requests.get(forecast_url)
    if forecast_req.status_code == 200:
        forecast = forecast_req.text
        return Response(forecast, mimetype='text/plain')
    return jsonify({'error': 'Unable to fetch content'}), 404


def get_aurora():
    req_url = 'https://services.swpc.noaa.gov/products/animations/ovation_north_24h.json'

    try:
        req_res = requests.get(req_url, timeout=10)
        req_res.raise_for_status()
        data = req_res.json()
    except requests.RequestException as e:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'Failed to load AURORA data: ' + str(e).encode('utf-8') + b'\r\n')
        return

    images = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_image, entry, idx): idx for idx, entry in enumerate(data)}

        for future in as_completed(futures):
            index, result = future.result()
            if result:
                images.append((index, result))

    images.sort(key=lambda x: x[0])

    if not images:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'No AURORA images available.\r\n')
        return

    image_contents = [img[1] for img in images]

    while True:
        for image in image_contents:
            try:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                time.sleep(0.15)
            except GeneratorExit:
                return
            except Exception as e:
                continue

@app.route('/stream_aurora')
def stream_aurora():
    return Response(get_aurora(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/overview')
def get_overview():
    overview_url = 'https://services.swpc.noaa.gov/products/noaa-scales.json'
    overview_req = requests.get(overview_url)

    if overview_req.status_code == 200:
        json_data = overview_req.json()
        data = []

        now = [
            f'{json_data.get("0", {}).get("DateStamp")}(Now)',
            f'R{json_data.get("0", {}).get("R", {}).get("Scale", "N/A")}',
            f'G{json_data.get("0", {}).get("G", {}).get("Scale", "N/A")}',
            f'S{json_data.get("0", {}).get("S", {}).get("Scale", "N/A")}'
        ]

        last24 = [
            f'{json_data.get("-1", {}).get("DateStamp")}(Last 24 Hours)',
            f'R{json_data.get("-1", {}).get("R", {}).get("Scale", "N/A")}',
            f'G{json_data.get("-1", {}).get("G", {}).get("Scale", "N/A")}',
            f'S{json_data.get("-1", {}).get("S", {}).get("Scale", "N/A")}'
        ]

        predict_now = [
            f'{json_data.get("1", {}).get("DateStamp")}(Predict 24 Hours)',
            f'R{json_data.get("1", {}).get("R", {}).get("Scale", "N/A")}',
            f'G{json_data.get("1", {}).get("G", {}).get("Scale", "N/A")}',
            f'S{json_data.get("1", {}).get("S", {}).get("Scale", "N/A")}'
        ]

        predict_tomorrow = [
            json_data.get("2", {}).get("DateStamp"),
            f'R{json_data.get("2", {}).get("R", {}).get("Scale", "N/A")}',
            f'G{json_data.get("2", {}).get("G", {}).get("Scale", "N/A")}',
            f'S{json_data.get("2", {}).get("S", {}).get("Scale", "N/A")}'
        ]

        predict_next_tomorrow = [
            json_data.get("3", {}).get("DateStamp"),
            f'R{json_data.get("3", {}).get("R", {}).get("Scale", "N/A")}',
            f'G{json_data.get("3", {}).get("G", {}).get("Scale", "N/A")}',
            f'S{json_data.get("3", {}).get("S", {}).get("Scale", "N/A")}'
        ]

        data.append(now)
        data.append(last24)
        data.append(predict_now)
        data.append(predict_tomorrow)
        data.append(predict_next_tomorrow)

        for i, col in enumerate(data):
            for j, token in enumerate(col):
                if "None" in token:
                    data[i][j] = "None"

        return jsonify({'overview': data}), 200
    return jsonify({'error': 'Unable to fetch content'}), 404


def get_wsa_enlil():
    req_url = 'https://services.swpc.noaa.gov/products/animations/enlil.json'

    try:
        req_res = requests.get(req_url, timeout=10)
        req_res.raise_for_status()
        data = req_res.json()
    except requests.RequestException as e:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'Failed to load WSA data: ' + str(e).encode('utf-8') + b'\r\n')
        return


    images = []


    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = {executor.submit(fetch_image, entry, idx): idx for idx, entry in enumerate(data)}

        for future in as_completed(futures):
            index, result = future.result()
            if result:
                images.append((index, result))


    images.sort(key=lambda x: x[0])

    if not images:
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'
               b'No WSA images available.\r\n')
        return


    image_contents = [img[1] for img in images]


    while True:
        for image in image_contents:
            try:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                time.sleep(0.15)
            except GeneratorExit:
                return
            except Exception as e:
                continue

@app.route('/stream_wsa-enlil')
def stream_wsa_enlil():
    return Response(get_wsa_enlil(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/huxt')
def get_huxt():
    huxt_url = 'https://huxt-bucket.s3.eu-west-2.amazonaws.com/wsa_huxt_forecast_latest.png'
    hux_res = requests.get(huxt_url, timeout=10)
    hux_res.raise_for_status()
    if hux_res.status_code == 200:
        huxt_image = BytesIO(hux_res.content)
        return jsonify({
            'huxt_image': image_to_base64(huxt_image)
        })
    return jsonify({'error': 'Unable to fetch huxt image'}), 404

@app.route('/location')
def get_location():
    g = geocoder.ip('me')
    latitude, longitude = g.latlng
    altitude = 0
    try:
        geomagnetic_lat, geomagnetic_lon, geomagnetic_alt = aacgmv2.get_aacgm_coord(latitude, longitude, altitude, datetime.now(timezone.utc))
    except RuntimeError:
        geomagnetic_lat, geomagnetic_lon = mag_altitude(latitude,longitude)
        geomagnetic_alt = altitude

    return jsonify({'latitude': latitude, 'longitude': longitude, 'geolatitude': round(geomagnetic_lat,4)})

@app.route('/aurora')
def get_aurora_pic():
    req_url = 'https://services.swpc.noaa.gov/products/animations/ovation_north_24h.json'
    req_res = requests.get(req_url, timeout=10)
    if req_res.status_code == 200:
        data = req_res.json()
        img_url = f'https://services.swpc.noaa.gov/{data[-1]["url"]}'
        img_res = requests.get(img_url, timeout=10)
        if img_res.status_code == 200:
            return jsonify({
                'aurora_image': image_to_base64(BytesIO(img_res.content))
            }), 200
    return jsonify({'error': 'Unable to fetch aurora image'}), 404
    pass

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

def mag_altitude(latitude, longitude):
    pole_latitude = 80.65
    pole_longitude = -72.68

    rad = math.pi / 180
    latitude_rad = latitude * rad
    longitude_rad = longitude * rad
    pole_lat_rad = pole_latitude * rad
    pole_lon_rad = pole_longitude * rad

    delta_lon = pole_lon_rad - longitude_rad
    x = math.cos(pole_lat_rad) * math.sin(delta_lon)
    y = math.cos(latitude_rad) * math.sin(pole_lat_rad) - math.sin(latitude_rad) * math.cos(pole_lat_rad) * math.cos(delta_lon)
    z = math.sin(latitude_rad) * math.sin(pole_lat_rad) + math.cos(latitude_rad) * math.cos(pole_lat_rad) * math.cos(delta_lon)

    azimuth = math.atan2(x, y)
    elevation = math.asin(z / math.sqrt(x*x + y*y + z*z))

    azimuth_deg = azimuth / rad
    elevation_deg = elevation / rad

    return azimuth_deg, elevation_deg

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        open_browser()
    app.run(debug=True)
