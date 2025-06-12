import streamlit as st
from PIL import Image
from pdf2image import convert_from_path
import ifcopenshell
import io

from floorplan_generator import generate_random_plan

st.title("AI Floorplan Assistant")

# File upload
uploaded_file = st.file_uploader(
    "Upload plot layout (image/PDF/IFC)",
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

# Step 1: building type
building_type = st.selectbox(
    "What type of building?",
    ["villa", "hotel", "office"],
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
else:  # office
    floors = st.number_input("Number of floors", 1, 50, 10)
    questions.append(("floors", floors))

if st.button("Generate floor plan options"):
    plans = [generate_random_plan() for _ in range(3)]
    for idx, plan in enumerate(plans, 1):
        st.subheader(f"Option {idx}")
        # simple text representation
        for room in plan.rooms:
            st.write(f"Room at ({room.x},{room.y}) size {room.width}x{room.height}")
