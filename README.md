# AI Floorplan Assistant


This project provides a simple web interface to upload a plot layout (image, PDF, or IFC). The app interacts with the user to collect design requirements, asks for plot dimensions, and generates basic floor plan options that respect the given size.


## Features

- Upload plot files in image (`.png`, `.jpg`), PDF, or IFC format.

- Choose building type: villa, hotel, office, apartment, or hostel.
- Interactive questions adjust based on building type.
- Display floor plan options generated to fit within the provided plot dimensions.
- Optionally generate plans with GPT-4o via the OpenAI API for higher quality.
- Download the generated plans as a single PDF file.


## Requirements

- Python 3.10+
- Install packages:

```bash
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` to enable GPT-4o generation.


## Running

Start the web application with:

```bash
streamlit run app.py
```

## Notes


This prototype is inspired by Finch3D/TestFit. By default it uses a basic recursive splitting algorithm so that rooms always fit inside the given plot. When `OPENAI_API_KEY` is supplied you can enable GPT-4o generation for higher-quality layouts. Additional logic would be required for production use.

