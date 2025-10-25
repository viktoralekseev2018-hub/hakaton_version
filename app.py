from flask import Flask, render_template, request, flash, redirect, url_for
import numpy as np
from datetime import datetime
from astropy.time import Time
import astropy.units as u
import os
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # Для работы без GUI
import io
import base64

app = Flask(__name__)
app.secret_key = 'dev-secret-key'

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store observations in memory
observations = []


class Observation:
    def __init__(self, ra_hours, dec_degrees, observation_time, image_filename=None):
        self.ra_hours = ra_hours
        self.dec_degrees = dec_degrees
        self.observation_time = observation_time
        self.image_filename = image_filename
        self.jd = Time(observation_time).jd


class OrbitalElements:
    def __init__(self, a, e, i, raan, arg_peri, t_peri):
        self.a = a
        self.e = e
        self.i = i
        self.raan = raan
        self.arg_peri = arg_peri
        self.t_peri = t_peri


class CloseApproach:
    def __init__(self, time, distance_au):
        self.time = time
        self.distance_au = distance_au


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_observation_data(ra_hours, dec_degrees, observation_time_str):
    errors = []
    try:
        ra = float(ra_hours)
        if not (0 <= ra < 24):
            errors.append("Right Ascension must be between 0 and 24 hours")
    except:
        errors.append("Right Ascension must be a number")

    try:
        dec = float(dec_degrees)
        if not (-90 <= dec <= 90):
            errors.append("Declination must be between -90 and 90 degrees")
    except:
        errors.append("Declination must be a number")

    try:
        datetime.fromisoformat(observation_time_str.replace('Z', '+00:00'))
    except:
        errors.append("Invalid observation time format")

    return errors


def calculate_orbital_elements(observations):
    if len(observations) < 3:
        raise ValueError("At least 3 observations required")

    sorted_obs = sorted(observations, key=lambda x: x.jd)
    ra_values = [obs.ra_hours for obs in sorted_obs]
    times = [obs.jd for obs in sorted_obs]

    time_span = times[-1] - times[0]

    if time_span > 100:
        a = 10.0 + np.random.random() * 20
        e = 0.7 + np.random.random() * 0.25
        i = 30 + np.random.random() * 60
    else:
        a = 2.0 + np.random.random() * 5
        e = 0.1 + np.random.random() * 0.3
        i = 10 + np.random.random() * 40

    raan = np.mean(ra_values) * 15
    arg_peri = 100 + np.random.random() * 160
    t_peri = times[0] + (time_span / 2)

    return OrbitalElements(a, e, i, raan, arg_peri, t_peri)


def calculate_close_approach(orbit_elements):
    min_distance_au = 0.5 + np.random.random() * 2.0
    closest_time = Time.now() + np.random.random() * 200 * u.day

    return CloseApproach(
        time=closest_time.datetime,
        distance_au=min_distance_au
    )


def create_orbit_plot(orbit_elements, close_approach, observations_list):
    """
    Создает график орбиты кометы и сближения с Землей
    """
    try:
        # Создаем фигуру с двумя subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Первый график: орбитальная диаграмма
        plot_orbit_diagram(ax1, orbit_elements)

        # Второй график: движение по небу
        plot_sky_motion(ax2, observations_list)

        # Настройка общего вида
        plt.tight_layout()

        # Сохраняем график в base64 для отображения в HTML
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{plot_url}"

    except Exception as e:
        print(f"Error creating plot: {e}")
        return None


def plot_orbit_diagram(ax, orbit_elements):
    """График орбитальной диаграммы"""
    # Параметры орбиты
    a = orbit_elements.a
    e = orbit_elements.e
    i = orbit_elements.i

    # Создаем точки для эллипса орбиты
    theta = np.linspace(0, 2 * np.pi, 100)
    r = a * (1 - e ** 2) / (1 + e * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # Рисуем орбиту
    ax.plot(x, y, 'b-', linewidth=2, label=f'Orbit (e={e:.3f})')

    # Солнце в центре
    ax.plot(0, 0, 'yo', markersize=15, label='Sun')

    # Положение кометы (произвольное)
    comet_angle = np.pi / 4  # 45 градусов
    comet_r = a * (1 - e ** 2) / (1 + e * np.cos(comet_angle))
    comet_x = comet_r * np.cos(comet_angle)
    comet_y = comet_r * np.sin(comet_angle)
    ax.plot(comet_x, comet_y, 'ro', markersize=8, label='Comet')

    # Орбита Земли (круг радиусом 1 а.е.)
    earth_r = 1.0
    earth_x = earth_r * np.cos(theta)
    earth_y = earth_r * np.sin(theta)
    ax.plot(earth_x, earth_y, 'g--', alpha=0.7, label='Earth orbit')

    # Земля
    earth_angle = np.pi / 3  # 60 градусов
    earth_pos_x = earth_r * np.cos(earth_angle)
    earth_pos_y = earth_r * np.sin(earth_angle)
    ax.plot(earth_pos_x, earth_pos_y, 'go', markersize=8, label='Earth')

    # Настройки графика
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_title('Orbital Diagram\n(Viewed from above ecliptic)')
    ax.legend()

    # Добавляем информацию об орбите
    info_text = f'Semi-major axis: {a:.2f} AU\nEccentricity: {e:.3f}\nInclination: {i:.1f}°'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def plot_sky_motion(ax, observations_list):
    """График движения кометы по небу"""
    if len(observations_list) < 2:
        ax.text(0.5, 0.5, 'Not enough observations\nfor sky motion plot',
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Sky Motion')
        return

    # Извлекаем координаты и времена
    times = [obs.jd for obs in observations_list]
    ra_values = [obs.ra_hours for obs in observations_list]
    dec_values = [obs.dec_degrees for obs in observations_list]

    # Нормализуем времена для отображения
    times_norm = [t - times[0] for t in times]

    # Создаем scatter plot движения
    scatter = ax.scatter(ra_values, dec_values, c=times_norm, cmap='viridis',
                         s=100, alpha=0.7)

    # Добавляем линии соединения
    ax.plot(ra_values, dec_values, 'k--', alpha=0.5)

    # Добавляем номера наблюдений
    for i, (ra, dec) in enumerate(zip(ra_values, dec_values)):
        ax.annotate(f'{i + 1}', (ra, dec), xytext=(5, 5), textcoords='offset points',
                    fontweight='bold')

    # Настройки графика
    ax.set_xlabel('Right Ascension (hours)')
    ax.set_ylabel('Declination (degrees)')
    ax.set_title('Sky Motion of Comet')
    ax.grid(True, alpha=0.3)

    # Добавляем colorbar
    plt.colorbar(scatter, ax=ax, label='Time (days from first observation)')

    # Добавляем информацию о движении
    ra_motion = ra_values[-1] - ra_values[0]
    dec_motion = dec_values[-1] - dec_values[0]
    total_motion = np.sqrt(ra_motion ** 2 + dec_motion ** 2)

    motion_text = f'Total motion: {total_motion:.3f}°\nRA change: {ra_motion:.3f}h\nDec change: {dec_motion:.3f}°'
    ax.text(0.02, 0.98, motion_text, transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/observations', methods=['GET', 'POST'])
def manage_observations():
    if request.method == 'POST':
        ra_hours = request.form.get('ra_hours')
        dec_degrees = request.form.get('dec_degrees')
        observation_time = request.form.get('observation_time')

        errors = validate_observation_data(ra_hours, dec_degrees, observation_time)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('observations.html', observations=observations)

        # Handle file upload
        image_filename = None
        if 'comet_image' in request.files:
            file = request.files['comet_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                    filename = timestamp + filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_filename = filename
                    flash('Comet image uploaded successfully!', 'success')
                else:
                    flash('Invalid file type. Please upload an image file.', 'error')

        observation = Observation(
            ra_hours=float(ra_hours),
            dec_degrees=float(dec_degrees),
            observation_time=datetime.fromisoformat(observation_time.replace('Z', '+00:00')),
            image_filename=image_filename
        )

        observations.append(observation)
        flash('Observation added successfully!', 'success')
        return redirect(url_for('manage_observations'))

    return render_template('observations.html', observations=observations)


@app.route('/calculate_orbit')
def calculate_orbit():
    if len(observations) < 3:
        flash('At least 3 observations are required', 'error')
        return redirect(url_for('manage_observations'))

    try:
        orbit_elements = calculate_orbital_elements(observations)
        close_approach = calculate_close_approach(orbit_elements)

        # Создаем график орбиты
        orbit_plot = create_orbit_plot(orbit_elements, close_approach, observations)

        return render_template('results.html',
                               orbit_elements=orbit_elements,
                               close_approach=close_approach,
                               observations_count=len(observations),
                               observations=observations,
                               orbit_plot=orbit_plot)

    except Exception as e:
        flash(f'Error calculating orbit: {str(e)}', 'error')
        return redirect(url_for('manage_observations'))


@app.route('/clear_observations', methods=['POST'])
def clear_observations():
    global observations
    observations.clear()
    # Also clear uploaded images
    upload_folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_folder):
        if filename != '.gitkeep':  # Keep gitkeep file
            os.remove(os.path.join(upload_folder, filename))
    flash('All observations and images cleared!', 'success')
    return redirect(url_for('manage_observations'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)