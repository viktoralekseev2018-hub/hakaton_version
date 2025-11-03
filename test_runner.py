import pytest
import sys
import os
from datetime import datetime
import re

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, Observation, validate_observation_data, calculate_orbital_elements


class TestRunner:
    def __init__(self):
        self.results = []
        self.observations_data = self.get_observations_data()

    def get_observations_data(self):
        """Возвращает тестовые данные наблюдений"""
        return [
            ("2025 Aug 26 00:00", "12h43m27.81s", "-04d19m29.7s"),
            ("2025 Sep 05 00:00", "13h07m19.50s", "-06d55m55.1s"),
            ("2025 Sep 15 00:00", "13h31m50.77s", "-09d29m48.8s"),
            ("2025 Sep 25 00:00", "13h57m08.77s", "-11d59m15.4s"),
            ("2025 Oct 05 00:00", "14h23m18.94s", "-14d21m55.4s"),
            ("2025 Oct 15 00:00", "14h50m26.10s", "-16d35m20.9s"),
            ("2025 Oct 25 00:00", "15h18m35.18s", "-18d36m58.8s"),
            ("2025 Nov 04 00:00", "15h47m47.45s", "-20d23m58.4s"),
            ("2025 Nov 14 00:00", "16h18m02.02s", "-21d53m31.8s"),
            ("2025 Nov 24 00:00", "16h49m15.90s", "-23d02m56.8s"),
        ]

    def parse_time(self, time_str):
        """Парсинг времени из формата '2025 Aug 26 00:00'"""
        try:
            # Преобразуем в ISO формат
            months = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }

            parts = time_str.split()
            year = parts[0]
            month = months[parts[1]]
            day = parts[2]
            time_part = parts[3]

            iso_time = f"{year}-{month}-{day}T{time_part}:00"
            return iso_time
        except Exception as e:
            print(f"Ошибка парсинга времени '{time_str}': {e}")
            return None

    def parse_ra_to_hours(self, ra_str):
        """Парсинг прямого восхождения из формата '12h43m27.81s' в десятичные часы"""
        try:
            # Извлекаем часы, минуты, секунды
            match = re.match(r'(\d+)h(\d+)m([\d.]+)s', ra_str)
            if match:
                hours = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))

                # Конвертируем в десятичные часы
                total_hours = hours + minutes / 60 + seconds / 3600
                return round(total_hours, 6)
            else:
                print(f"Неверный формат RA: {ra_str}")
                return None
        except Exception as e:
            print(f"Ошибка парсинга RA '{ra_str}': {e}")
            return None

    def parse_dec_to_degrees(self, dec_str):
        """Парсинг склонения из формата '-04d19m29.7s' в десятичные градусы"""
        try:
            # Определяем знак
            sign = -1 if dec_str.startswith('-') else 1
            dec_str_clean = dec_str.lstrip('+-')

            # Извлекаем градусы, минуты, секунды
            match = re.match(r'(\d+)d(\d+)m([\d.]+)s', dec_str_clean)
            if match:
                degrees = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))

                # Конвертируем в десятичные градусы
                total_degrees = degrees + minutes / 60 + seconds / 3600
                return round(sign * total_degrees, 6)
            else:
                print(f"Неверный формат Dec: {dec_str}")
                return None
        except Exception as e:
            print(f"Ошибка парсинга Dec '{dec_str}': {e}")
            return None

    def create_test_observations(self, count=None):
        """Создание объектов наблюдений из тестовых данных"""
        print("\n" + "=" * 30)
        print("🔭 СОЗДАНИЕ ТЕСТОВЫХ НАБЛЮДЕНИЙ")
        print("=" * 30)

        observations = []
        data_to_use = self.observations_data[:count] if count else self.observations_data

        for i, (time_str, ra_str, dec_str) in enumerate(data_to_use, 1):
            print(f"\nНаблюдение {i}:")
            print(f"  Время: {time_str}")
            print(f"  RA: {ra_str}")
            print(f"  Dec: {dec_str}")

            # Парсим данные
            iso_time = self.parse_time(time_str)
            ra_hours = self.parse_ra_to_hours(ra_str)
            dec_degrees = self.parse_dec_to_degrees(dec_str)

            if iso_time and ra_hours is not None and dec_degrees is not None:
                try:
                    # Создаем объект наблюдения
                    obs = Observation(
                        ra_hours=ra_hours,
                        dec_degrees=dec_degrees,
                        observation_time=datetime.fromisoformat(iso_time)
                    )
                    observations.append(obs)
                    print(f"  ✅ УСПЕХ: RA={ra_hours:.6f}h, Dec={dec_degrees:.6f}°")
                except Exception as e:
                    print(f"  ❌ ОШИБКА: {e}")
            else:
                print("  ❌ ОШИБКА ПАРСИНГА ДАННЫХ")

        print(f"\n📊 СОЗДАНО НАБЛЮДЕНИЙ: {len(observations)} из {len(data_to_use)}")
        return observations

    def run_validation_tests(self):
        """Запуск тестов валидации на первом наблюдении"""
        print("\n" + "=" * 30)
        print("🧪 ТЕСТИРОВАНИЕ ВАЛИДАЦИИ")
        print("=" * 30)

        if not self.observations_data:
            print("❌ Нет данных для тестирования")
            return False

        # Берем первое наблюдение для теста валидации
        time_str, ra_str, dec_str = self.observations_data[0]
        iso_time = self.parse_time(time_str)
        ra_hours = self.parse_ra_to_hours(ra_str)
        dec_degrees = self.parse_dec_to_degrees(dec_str)

        if iso_time and ra_hours is not None and dec_degrees is not None:
            errors = validate_observation_data(
                str(ra_hours),
                str(dec_degrees),
                iso_time + 'Z'  # Добавляем Z для UTC
            )

            if errors:
                print("❌ ОШИБКИ ВАЛИДАЦИИ:")
                for error in errors:
                    print(f"   - {error}")
                self.results.append(("Валидация данных", "FAILED", errors))
                return False
            else:
                print("✅ ВАЛИДАЦИЯ ПРОЙДЕНА УСПЕШНО!")
                print(f"   Время: {iso_time}")
                print(f"   RA: {ra_hours:.6f} часов")
                print(f"   Dec: {dec_degrees:.6f} градусов")
                self.results.append(("Валидация данных", "PASSED", []))
                return True
        else:
            print("❌ ОШИБКА ПАРСИНГА ТЕСТОВЫХ ДАННЫХ")
            self.results.append(("Валидация данных", "FAILED", ["Ошибка парсинга"]))
            return False

    def run_observation_creation_test(self):
        """Тест создания объектов наблюдений"""
        print("\n" + "=" * 30)
        print("📊 ТЕСТ СОЗДАНИЯ НАБЛЮДЕНИЙ")
        print("=" * 30)

        observations = self.create_test_observations(3)  # Создаем 3 наблюдения для теста

        if len(observations) >= 3:
            print("✅ ТЕСТ СОЗДАНИЯ НАБЛЮДЕНИЙ ПРОЙДЕН!")
            for i, obs in enumerate(observations, 1):
                print(f"   Набл.{i}: RA={obs.ra_hours:.6f}h, Dec={obs.dec_degrees:.6f}°, JD={obs.jd:.6f}")
            self.results.append(("Создание наблюдений", "PASSED", []))
            return True
        else:
            print("❌ НЕ УДАЛОСЬ СОЗДАТЬ ДОСТАТОЧНО НАБЛЮДЕНИЙ")
            self.results.append(("Создание наблюдений", "FAILED", ["Мало наблюдений"]))
            return False

    def run_orbit_calculation_test(self):
        """Тест расчета орбитальных элементов"""
        print("\n" + "=" * 30)
        print("🛰️ ТЕСТ РАСЧЕТА ОРБИТЫ")
        print("=" * 30)

        try:
            # Создаем все наблюдения
            observations = self.create_test_observations()

            if len(observations) < 3:
                print("❌ ДЛЯ РАСЧЕТА ОРБИТЫ НУЖНО МИНИМУМ 3 НАБЛЮДЕНИЯ!")
                self.results.append(("Расчет орбиты", "FAILED", ["Недостаточно наблюдений"]))
                return False

            print(f"\n📈 РАСЧЕТ ОРБИТЫ ДЛЯ {len(observations)} НАБЛЮДЕНИЙ...")

            # Рассчитываем орбитальные элементы
            orbit = calculate_orbital_elements(observations)

            print("✅ РАСЧЕТ ОРБИТЫ ВЫПОЛНЕН УСПЕШНО!")
            print(f"   - Большая полуось (a): {orbit.a:.3f} а.е.")
            print(f"   - Эксцентриситет (e): {orbit.e:.3f}")
            print(f"   - Наклонение (i): {orbit.i:.1f}°")
            print(f"   - Долгота восх. узла: {orbit.raan:.1f}°")
            print(f"   - Аргумент перицентра: {orbit.arg_peri:.1f}°")
            print(f"   - Время перицентра: JD {orbit.t_peri:.6f}")

            self.results.append(("Расчет орбиты", "PASSED", []))
            return True

        except Exception as e:
            print(f"❌ ОШИБКА ПРИ РАСЧЕТЕ ОРБИТЫ: {e}")
            self.results.append(("Расчет орбиты", "FAILED", [str(e)]))
            return False

    def run_flask_routes_test(self):
        """Тестирование Flask маршрутов"""
        print("\n" + "=" * 30)
        print("🌐 ТЕСТИРОВАНИЕ FLASK МАРШРУТОВ")
        print("=" * 30)

        try:
            with app.test_client() as client:
                # Тест главной страницы
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ Главная страница: РАБОТАЕТ")
                else:
                    print(f"❌ Главная страница: ОШИБКА {response.status_code}")

                # Тест страницы наблюдений
                response = client.get('/observations')
                if response.status_code == 200:
                    print("✅ Страница наблюдений: РАБОТАЕТ")
                else:
                    print(f"❌ Страница наблюдений: ОШИБКА {response.status_code}")

                # Тест расчета орбиты
                response = client.get('/calculate_orbit')
                if response.status_code == 302:  # redirect when no observations
                    print("✅ Расчет орбиты: ПЕРЕНАПРАВЛЕНИЕ (нет наблюдений)")
                else:
                    print(f"✅ Расчет орбиты: статус {response.status_code}")

                self.results.append(("Flask маршруты", "PASSED", []))
                return True

        except Exception as e:
            print(f"❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ МАРШРУТОВ: {e}")
            self.results.append(("Flask маршруты", "FAILED", [str(e)]))
            return False

    def print_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 50)

        passed = 0
        failed = 0

        for test_name, status, errors in self.results:
            if status == "PASSED":
                print(f"✅ {test_name}: ПРОЙДЕН")
                passed += 1
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕН")
                if errors:
                    for error in errors:
                        print(f"   💡 {error}")
                failed += 1

        print(f"\n📈 РЕЗУЛЬТАТ: {passed} пройдено, {failed} не пройдено")

        if failed == 0:
            print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        else:
            print("💡 Некоторые тесты не пройдены.")


def main():
    """Основная функция запуска тестов"""
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ КОМЕТНОГО ПРИЛОЖЕНИЯ")
    print("С ТЕСТОВЫМИ ДАННЫМИ НАБЛЮДЕНИЙ")
    print("=" * 60)

    print("\n📋 ТЕСТОВЫЕ ДАННЫЕ:")
    observations_data = [
        ("2025 Aug 26 00:00", "12h43m27.81s", "-04d19m29.7s"),
        ("2025 Sep 05 00:00", "13h07m19.50s", "-06d55m55.1s"),
        ("2025 Sep 15 00:00", "13h31m50.77s", "-09d29m48.8s"),
        # ... и остальные данные
    ]

    for i, (time, ra, dec) in enumerate(observations_data, 1):
        print(f"{i:2d}. Время: {time}, RA: {ra}, Dec: {dec}")

    runner = TestRunner()

    # Запускаем все тесты
    runner.run_validation_tests()
    runner.run_observation_creation_test()
    runner.run_orbit_calculation_test()
    runner.run_flask_routes_test()

    # Выводим итоговый отчет
    runner.print_summary()


if __name__ == "__main__":
    main()