from typing import Dict
from Media import Media

def media_mapper(account_json: Dict) -> Media:
    account_data=account_json.get("node")
    try:
        caption = account_data.get("edge_media_to_caption").get("edges")[0].get("node").get("text")
    except:
        caption= "No Caption"
    accessibility_caption=account_data.get("accessibility_caption")
    image_url=account_data.get("display_url")
    image_height=account_data.get("dimensions").get("height")
    image_width=account_data.get("dimensions").get("width")
    is_video=account_data.get("is_video")

    #"edge_sidecar_to_children" attribute might be added in the future

    media = Media(
        caption = caption,
        accessibility_caption=accessibility_caption,
        image_url=image_url,
        image_height= image_height,
        image_width=image_width,
        is_video=is_video
    )
    return media