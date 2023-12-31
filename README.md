# lol_highlight_detection
League of Legend Highlight Detection

## Approach

1. Downscale images to 480p to make sure size is OK
2. Reduce to 5 FPS
3. Extract Overlapping Videos (10s sequence, 5s overlap)
    - If > 5s is within time (is_highlight) - is_highlight
4. Extract Frames into folders

## TODOs

- [ ] Set up Pre-Commit
- [ ] Set up...

## Resources:

1. Fast.AI - https://docs.fast.ai/tutorial.image_sequence.html
2. TIMM/HF - https://github.com/huggingface/pytorch-image-models
3. HF/ViT - see `video_classification.ipynb`
4. VideoMAE - https://huggingface.co/docs/transformers/model_doc/videomae
5. Keras - https://keras.io/examples/vision/video_classification/ (keras-core??)
6. TF - https://www.tensorflow.org/tutorials/video/video_classification
7. Papers - https://paperswithcode.com/search?q_meta=&q_type=&q=videomae
8. Hiera - https://github.com/facebookresearch/hiera