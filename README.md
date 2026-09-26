# Disjoint-Set-Union

Proyecto
Estructura asignada: **Disjoint Set Union (DSU)**

## Contenido del repositorio
- `dsu.cpp` — implementación instrumentada de DSU. Cada llamada a `find` y `unite` registra su estado en un archivo JSON dentro de `logs/`.
- `dsu_basic.cpp` — misma estructura, sin path compression ni unión por tamaño, usada como comparación.
- `logs/` — trazas generadas por `dsu.cpp`: `dsu_log_main.json`, `dsu_log_single.json`, `dsu_log_worstcase.json`.
- `animacion/dsu.py` — script de Manim que lee los archivos de `logs/` y genera el video.
- `animacion/audio/` — narración grabada por escena, más `narracion_completa.m4a` (los 8 audios ya unidos).

## Software requerido
- Un compilador de C++17.
- Python 3.9 o superior.
- Manim Community **0.19.1**.
- FFmpeg (lo usan tanto Manim como el paso de unir video y audio).

## Instalación

```powershell
python -m pip install manim==0.19.1
winget install -e --id Gyan.FFmpeg
```

## Pasos para reproducir el video

**1. Compilar y correr la implementación en C++**:
```powershell
g++ -std=c++17 dsu.cpp -o dsu.exe
.\dsu.exe
```

**2. Renderizar la animación con Manim** (alta calidad):
```powershell
python -m manim -pqh animacion/dsu.py DSUVideo
```
El video sin audio queda en `media/videos/dsu/1080p60/DSUVideo.mp4`.

**3. Unir el video renderizado con la narración**, parado en la raíz del repo:
```powershell
ffmpeg -i media\videos\dsu\1080p60\DSUVideo.mp4 -i animacion\audio\narracion_completa.m4a -c:v copy -c:a aac -b:a 192k -shortest DSUVideo_final.mp4
```

`DSUVideo_final.mp4` es el video con audio, entregado como parte de este proyecto.

## Integrantes

Fabiana Ameri · Joaquín Justo