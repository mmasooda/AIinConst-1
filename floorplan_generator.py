import random
import io
import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw
import openai

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int

@dataclass
class FloorPlan:
    rooms: List[Room]


def extract_plot_metrics(
    image: Image.Image,
    unit: str = "meters",
    pixels_per_unit: int = 100,
) -> Tuple[float, float, float]:
    """Return (width_m, height_m, area_m2) from an image mask."""

    width_px, height_px = image.size
    width = width_px / pixels_per_unit
    height = height_px / pixels_per_unit

    gray = image.convert("L")
    arr = np.array(gray)
    mask = arr < 250
    area_px = mask.sum()
    area = area_px / (pixels_per_unit ** 2)

    if unit == "feet":
        width *= 0.3048
        height *= 0.3048
        area *= 0.092903

    return float(width), float(height), float(area)


def generate_random_plan(plot_width: int = 20, plot_height: int = 20, num_rooms: int = 6) -> FloorPlan:
    """Generate a simple floor plan that fits within the plot dimensions."""

    rooms = [Room(0, 0, plot_width, plot_height)]

    def split_room(room: Room) -> List[Room]:
        """Split the room either horizontally or vertically."""
        if room.width <= 2 and room.height <= 2:
            return [room]

        if room.width > room.height:
            orientation = "vertical"
        elif room.height > room.width:
            orientation = "horizontal"
        else:
            orientation = random.choice(["horizontal", "vertical"])

        if orientation == "vertical" and room.width >= 2:
            min_split = max(1, int(room.width * 0.3))
            max_split = max(1, int(room.width * 0.7))
            if max_split <= min_split:
                return [room]
            split = random.randint(min_split, max_split)
            return [
                Room(room.x, room.y, split, room.height),
                Room(room.x + split, room.y, room.width - split, room.height),
            ]
        elif orientation == "horizontal" and room.height >= 2:
            min_split = max(1, int(room.height * 0.3))
            max_split = max(1, int(room.height * 0.7))
            if max_split <= min_split:
                return [room]
            split = random.randint(min_split, max_split)
            return [
                Room(room.x, room.y, room.width, split),
                Room(room.x, room.y + split, room.width, room.height - split),
            ]
        return [room]

    # Recursively split rooms until we reach the desired count
    while len(rooms) < num_rooms:
        # choose a room with area > 1 to split
        candidates = [r for r in rooms if r.width * r.height > 1]
        if not candidates:
            break
        room = random.choice(candidates)
        rooms.remove(room)
        rooms.extend(split_room(room))

    return FloorPlan(rooms=rooms)


def generate_plan_with_openai(
    plot_width: int,
    plot_height: int,
    num_rooms: int,
    building_type: str,
) -> FloorPlan:
    """Use GPT-4o via OpenAI API to generate a floor plan."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    openai.api_key = api_key

    prompt = (
        "Generate a JSON floor plan with a list of rooms. "
        f"Plot width: {plot_width}, height: {plot_height}. "
        f"Building type: {building_type}. Room count: {num_rooms}. "
        "Each room should have x, y, width, and height in meters."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    text = response["choices"][0]["message"]["content"].strip()
    try:
        data = json.loads(text)
        rooms = [
            Room(r["x"], r["y"], r["width"], r["height"]) for r in data.get("rooms", [])
        ]
        return FloorPlan(rooms=rooms)
    except json.JSONDecodeError:
        # fall back to a random plan when JSON is invalid
        return generate_random_plan(plot_width, plot_height, num_rooms)


def plan_to_image(plan: FloorPlan, cell_size: int = 40) -> Image:
    """Convert a FloorPlan into a simple PIL Image drawing."""
    width = max(r.x + r.width for r in plan.rooms) * cell_size
    height = max(r.y + r.height for r in plan.rooms) * cell_size
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    for room in plan.rooms:
        rect = [
            room.x * cell_size,
            room.y * cell_size,
            (room.x + room.width) * cell_size,
            (room.y + room.height) * cell_size,
        ]
        draw.rectangle(rect, outline="black", fill="#dddddd")
    return img


def plans_to_pdf(plans: List[FloorPlan]) -> bytes:
    """Return PDF bytes containing one page per plan."""
    images = [plan_to_image(p) for p in plans]
    if not images:
        return b""
    buf = io.BytesIO()
    images[0].save(buf, format="PDF", save_all=True, append_images=images[1:])
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
