import pandas as pd
import torch
from transformers import pipeline

if torch.cuda.is_available():
    print("Using GPU (cuda)")
    pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)
else:
    print("GPU-cuda not available, using CPU")
    pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_category(title_ls, vid_cat_ls):
    print("Classifying...")
    pipe_result = pipe(title_ls, candidate_labels=vid_cat_ls)
    result = [r["labels"][0] for r in pipe_result]
    print("Classification completed!")
    return result