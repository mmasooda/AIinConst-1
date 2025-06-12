# AI Floorplan Assistant

This project provides a simple web interface to upload a plot layout (image, PDF, or IFC). The app interacts with the user to collect design requirements and generates basic floor plan options.

## Features

- Upload plot files in image (`.png`, `.jpg`), PDF, or IFC format.
- Choose building type: villa, hotel, or office.
- Interactive questions adjust based on building type.
- Display placeholder floor plan options.

## Requirements

- Python 3.10+
- Install packages:

```bash
pip install -r requirements.txt
```

## Running

Start the web application with:

```bash
streamlit run app.py
```

## Notes

This is a minimal prototype inspired by Finch3D/TestFit. The floor plan generation uses simple geometric placeholders. Additional logic is needed for production use.
