# Mis llamadas — app Android en Python (Kivy)

Lista de contactos: añades nombre + número, tocas uno y se abre el marcador del móvil con el número puesto. Se guardan en un JSON local.

## Probar en el PC
```bash
pip install kivy
python main.py
```

## Generar el APK (Linux o WSL en Windows)
```bash
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
  pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
pip install --user buildozer cython
buildozer android debug      # la primera vez tarda (descarga SDK/NDK)
```
El APK queda en `bin/`. Pásalo al móvil y ábrelo (activa "instalar apps de origen desconocido"),
o con el móvil conectado por USB: `buildozer android debug deploy run`.

## Cómo funciona la llamada
Android abre otras apps mediante *Intents*. Con `pyjnius` se usan las clases Java desde Python:
`Intent(ACTION_DIAL)` + `Uri.parse("tel:...")` → abre el marcador. No hace falta permiso.
Para llamar directamente sin confirmar, usa `ACTION_CALL` y añade el permiso `CALL_PHONE`
en `buildozer.spec` (y pedirlo en tiempo de ejecución con `android.permissions.request_permissions`).
