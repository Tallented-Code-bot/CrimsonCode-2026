# CrimsonCode-2026

# Theme:
Reinventing the Wheel

# Members:
- Jamieson Mansker
- Noah Manuel
- Owen Moore
- Calvin Tallent

# Project Description: 
We are reinventing the Ring doorbell camera to recognize faces/identites and brands and sends a notification to an application. These notifications allow us to give users more context in who is at the door.

# Materials used:
- Raspberry Pi Zero 2W
- Raspberry Pi Cam 3 Wide NoIR Module 

# Live face recognition

## Encode known faces
Place labeled face images under `training/<name>/` then run:

```bash
python detector.py --encode
```

## Run the camera app

```bash
python detector.py --camera 0 --model hog --scale 0.25 --tolerance 0.6
```

Quit with `q` or `Esc`.

## Smoke test (single image)

```bash
python scripts/smoke_recognize.py
```


