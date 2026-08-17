# AI model weights

This folder holds the Dentex disease-detection models used by
`app/services/ai_inference.py`:

```
app/ai_models/
├── seunet_arch.py                    # U-Net architecture definition (tracked in git)
└── weights/
    ├── dentex_disease_yolov8x.pt       # YOLOv8: detects 4 disease classes (NOT tracked — too large)
    └── dentex_enumeration32_seunet.pth # U-Net: FDI tooth enumeration, 32 teeth (NOT tracked — too large)
```

The `.pt` / `.pth` weight files are **git-ignored** (see `.gitignore`) because
they're ~370MB combined. Copy them into `app/ai_models/weights/` manually on
every machine that needs to run inference (they are not fetched
automatically).

Override the location with the `AI_MODEL_DIR` environment variable if you
keep the weights elsewhere.

## Dependencies

```bash
pip install torch torchvision ultralytics pillow numpy
```

(Install the CUDA build of torch from https://pytorch.org if you have an
NVIDIA GPU — CPU-only works too, just slower.)
