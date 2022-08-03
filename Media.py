from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Media:
    caption: str
    accessibility_caption: str 
    image_url: str
    image_height: int
    image_width: int
    is_video: bool
