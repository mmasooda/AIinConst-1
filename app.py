import streamlit as st
from PIL import Image
from pdf2image import convert_from_path
import ifcopenshell
import io

from floorplan_generator import (
    generate_random_plan,
    generate_plan_with_openai,
    plan_to_image,
    plans_to_pdf,
    extract_plot_metrics,
)

st.title("AI Floorplan Assistant")

# File upload
uploaded_file = st.file_uploader(
    label="Upload plot layout (image/PDF/IFC)",
    type=["png", "jpg", "jpeg", "pdf", "ifc"],
)

plot_image = None
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    suffix = uploaded_file.name.split(".")[-1].lower()
    if suffix in {"png", "jpg", "jpeg"}:
        plot_image = Image.open(io.BytesIO(file_bytes))
    elif suffix == "pdf":
        images = convert_from_path(uploaded_file)
        if images:
            plot_image = images[0]
    elif suffix == "ifc":
        try:
            ifc = ifcopenshell.file.from_string(file_bytes.decode("utf-8"))
            # Placeholder: create a blank image for display
            plot_image = Image.new("RGB", (400, 400), color="white")
        except Exception:
            st.error("Failed to read IFC file")

if plot_image is not None:
    st.image(plot_image, caption="Plot layout", use_column_width=True)

unit = st.selectbox("Units in plot image", ["meters", "feet"])
pixels_per_unit = st.number_input("Pixels per unit", 10, 1000, 100)
if plot_image is not None:
    width_m, height_m, area_m2 = extract_plot_metrics(
        plot_image, unit, pixels_per_unit
    )
else:
    width_m = height_m = area_m2 = 0

# ensure defaults are valid for number_input
default_width = width_m if width_m > 0 else 1.0
default_height = height_m if height_m > 0 else 1.0

# Plot dimensions
col1, col2 = st.columns(2)
with col1:
    plot_width = st.number_input(
        "Plot width (m)", min_value=1.0, value=float(default_width)
    )
with col2:
    plot_height = st.number_input(
        "Plot height (m)", min_value=1.0, value=float(default_height)
    )

st.write(f"Estimated plot area: {area_m2:.2f} m²")

# Step 1: building type
building_type = st.selectbox(
    "What type of building?",
    ["villa", "hotel", "office", "apartment", "hostel"],
)

# Additional questions
questions = []
if building_type == "villa":
    bedrooms = st.number_input("Number of bedrooms", 1, 10, 3)
    questions.append(("bedrooms", bedrooms))
elif building_type == "hotel":
    floors = st.number_input("Number of floors", 1, 20, 5)
    rooms_per_floor = st.number_input("Rooms per floor", 5, 50, 20)
    questions.extend([
        ("floors", floors),
        ("rooms_per_floor", rooms_per_floor),
    ])
elif building_type == "apartment":
    bedrooms = st.number_input("Bedrooms per apartment", 1, 5, 2)
    units_per_floor = st.number_input("Apartments per floor", 1, 20, 4)
    questions.extend([
        ("bedrooms_per_unit", bedrooms),
        ("units_per_floor", units_per_floor),
    ])
elif building_type == "hostel":
    floors = st.number_input("Number of floors", 1, 10, 3)
    rooms_per_floor = st.number_input("Rooms per floor", 5, 50, 15)
    questions.extend([
        ("floors", floors),
        ("rooms_per_floor", rooms_per_floor),
    ])
else:  # office
    floors = st.number_input("Number of floors", 1, 50, 10)
    questions.append(("floors", floors))

# Option to use GPT-4o via OpenAI API
use_gpt = st.checkbox("Use GPT-4o for plan generation")

if st.button("Generate floor plan options"):
    # basic estimate of rooms influenced by plot area
    base_rooms = max(4, int(area_m2 / 20))
    if building_type == "villa":
        room_count = base_rooms + bedrooms
    elif building_type == "hotel":
        room_count = max(base_rooms, int(rooms_per_floor * 0.3))
    elif building_type == "apartment":
        room_count = max(base_rooms, units_per_floor)
    elif building_type == "hostel":
        room_count = max(base_rooms, int(rooms_per_floor * 0.5))
    else:
        room_count = max(base_rooms, 10)

    if use_gpt:
        generator = lambda: generate_plan_with_openai(
            plot_width, plot_height, room_count, building_type
        )
    else:
        generator = lambda: generate_random_plan(plot_width, plot_height, room_count)

    plans = [generator() for _ in range(5)]
    images = []
    for idx, plan in enumerate(plans, 1):
        st.subheader(f"Option {idx}")
        image = plan_to_image(plan)
        images.append(image)
        st.image(image, caption=f"Plan {idx}", use_column_width=True)
    pdf_bytes = plans_to_pdf(plans)
    st.download_button("Download PDF", pdf_bytes, file_name="floorplans.pdf", mime="application/pdf")
