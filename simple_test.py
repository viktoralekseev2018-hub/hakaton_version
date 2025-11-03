from test_runner import TestRunner


def test_different_observation_counts():
    """Тестирование с разным количеством наблюдений"""
    test_cases = [
        {"name": "МИНИМУМ (3 наблюдения)", "count": 3},
        {"name": "СРЕДНЕЕ (5 наблюдений)", "count": 5},
        {"name": "ВСЕ наблюдения (10)", "count": 10},
    ]

    for test_case in test_cases:
        print(f"\n{'=' * 50}")
        print(f"🧪 ТЕСТ: {test_case['name']}")
        print(f"{'=' * 50}")

        runner = TestRunner()

        # Запускаем только тест орбиты с указанным количеством наблюдений
        observations = runner.create_test_observations(test_case["count"])

        if len(observations) >= 3:
            try:
                orbit = calculate_orbital_elements(observations)
                print("✅ ОРБИТА РАССЧИТАНА УСПЕШНО!")
                print(f"   a={orbit.a:.3f} а.е., e={orbit.e:.3f}, i={orbit.i:.1f}°")
            except Exception as e:
                print(f"❌ ОШИБКА: {e}")
        else:
            print("❌ НЕДОСТАТОЧНО НАБЛЮДЕНИЙ")


if __name__ == "__main__":
    # Запуск основных тестов
    from test_runner import main

    main()

    # Дополнительные тесты
    print("\n\n" + "=" * 60)
    run_extra = input("\nЗапустить тесты с разным количеством наблюдений? (y/n): ")
    if run_extra.lower() == 'y':
        test_different_observation_counts()