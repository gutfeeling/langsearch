from io import BytesIO

import streamlit as st

from langsearch.pipelines.types.image.imageindex import ImageIndexPipeline

st.title("Image Search Demo")
question = st.text_input("Type your search query here")
if len(question) != 0:
    pipeline = ImageIndexPipeline()
    results = pipeline.get_similar_images_from_text(question)
    for index, result in enumerate(results):
        url = result["url"]
        data = BytesIO(pipeline.get_image_bytes(result["image"]))
        st.markdown(f"[{index + 1}] [{url}]({url})")
        st.image(data, use_column_width="auto")
