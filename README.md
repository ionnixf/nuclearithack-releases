# Нейро-стенографист — автономный комплект Android (RC1)

- [**Скачать комплект APK + модели**](https://github.com/ionnixf/nuclearithack-releases/releases/download/v0.2.0-rc1/nuclear-rc1-x86_64.tar.gz) (`nuclear-rc1-x86_64.tar.gz`, 847 191 242 байт, SHA-256: `74dc4f47f4aca520310a374d3901d5cd65ac1919b794893728f2518b81577129`)
- [**Посмотреть демонстрацию**](https://github.com/ionnixf/nuclearithack-releases/releases/download/v0.2.0-rc1/rc1-demo.mp4) (`rc1-demo.mp4`, 5 494 957 байт, SHA-256: `6baf8ac6bed878d7192cbbcd1c3c5a70451051e8d27f3b5d16790c513d6d0c68`)
- [**Скачать исходники приложения**](https://github.com/ionnixf/nuclearithack-releases/releases/download/v0.2.0-rc1/nuclear-rc1-source.tar.gz) (`nuclear-rc1-source.tar.gz`, 177 450 байт, SHA-256: `ecb69a2e6d6f677538b39d0e4483abb1900a6446c073907e709908983c760ebe`)

> **Важно:** для установки и проверки на эмуляторе нужен **полный архив** `nuclear-rc1-x86_64.tar.gz` (APK + все 7 speech/LLM-моделей + `install.py` + контрольный WAV). Автоматический **GitHub Source code (zip / tar.gz)** самого репозитория доставки (`nuclearithack-releases`) содержит только файлы доставки и **не содержит Android-проект** — полный исходный код Android-приложения выложен отдельным архивом `nuclear-rc1-source.tar.gz`.

Страница релиза со всеми вложениями: <https://github.com/ionnixf/nuclearithack-releases/releases/tag/v0.2.0-rc1>

Android x86_64, проверенный AVD: API 35, 4096 МБ RAM, 2 vCPU.
Полный pipeline на устройстве: WAV → automatic diarization → GigaAM ASR →
Qwen3 LLM → JSON. INTERNET permission отсутствует.

Скачайте `nuclear-rc1-x86_64.tar.gz` и `.sha256`, проверьте:

```bash
sha256sum -c nuclear-rc1-x86_64.tar.gz.sha256
tar -xzf nuclear-rc1-x86_64.tar.gz
cd nuclear-rc1-x86_64
python3 install.py --serial emulator-5554
```

Последняя строка — единственная команда установки. Нужны Python 3.11+,
Android adb и запущенный чистый AVD. Замените serial на свой из `adb devices`.
Установщик очищает приватные данные приложения, проверяет SHA-256 APK и всех
моделей на компьютере и устройстве, доставляет контрольный WAV в Downloads,
выключает сеть и запускает приложение. Никаких загрузок и кэша разработчика.

[Инструкция жюри](JURY.md): Выбрать WAV → Downloads/Nuclear/jury-speech.wav →
дождаться реплик → Экспортировать JSON → сохранить в Downloads →
Открыть сохранённый JSON.

APK SHA-256: `896a877ebceed4b9030fdeb3d3712121876905ead2c563c14eb0b1909711db35`.
Архив SHA-256: `74dc4f47f4aca520310a374d3901d5cd65ac1919b794893728f2518b81577129`.
Веса: 7 файлов, 926119801 байт. [Размеры, хеши, происхождение](manifest.json).
Лицензии моделей и runtime, ONNX notices и происхождение контрольного WAV
включены в архив. Runtime встроен в APK, дополнительные AAR не нужны.

APK подписан Android debug-ключом; доставка в sandbox использует `run-as`.
Это комплект для воспроизводимой проверки на эмуляторе. Вход — PCM16 WAV
mono/stereo, 16/44.1/48 кГц, до 10 минут. ARM и другие API не приняты.
Синтетический WAV проверяет доставку и исполнение pipeline; качество живого
2/3-голосного диалога и WER/DER этим smoke не установлены.

Источник продуктового APK: `c4d0e82` (базовая интеграция `fba9afa`);
окончательный установщик: `debf9c8`. Репозиторий исходного приложения остаётся
приватным; этот публичный репозиторий содержит разрешённый комплект доставки.

Чистая приёмка: два полных прогона после Wipe Data из двух распаковок одного
архива. Decode → Ready: 16681 / 18703 мс, экспорт 97 / 69 мс. Оба JSON
сохранены и повторно открыты; содержимое совпало. Sampled peak PSS:
905725 / 909383 kB (253 / 222 замера); это не гарантированный абсолютный пик.
Протоколы и скриншоты: release asset `nuclear-rc1-evidence.tar.gz`.
