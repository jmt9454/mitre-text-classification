# MITRE Text Classification

## Big Picture Plan

The key idea here is to leverage NLP techniques to classify likely MITRE techniques present within text. This will allow us to see whether attacks across industries use the same techniques or if certain industries see a disproportionate amount of certain techniques compared to others or all industries combined.

### The Data

MITRE has text descriptions of each technique publicly available online. Furthermore, outside sources are referenced in most technique descriptions either to justify a description or provide an example of the technique in the wild. Lastly, synthetic data generation is possible via GPT-style LLMs.

We can use the MITRE descriptions and synthetic texts for the training portion. We can hold the referenced text for the testing portion under the assumption that a human expert with MITRE has already reviewed the source and deemed it appropriate for the technique (We are essentially assuming it is accurately hand-labeled for that technique). Additional synthetic data can be used for testing as well.

Regarding the synthetic data, we need to have varying degrees of technicality and style to better reflect what types of text can be encountered in the wild. Nine different sets of synthetic data will be used with 3 degrees of technicality (non-technical, semi-technical, and technical) and 3 different styles (conversation, news article, internal report). I preemptively admit that defining and judging levels of technicality and style can be subjective - humans need to spot check the synthetic data and perhaps use a rubric?

Data for now is vectorized with the all-MiniLM-L6-v2 Sentence Transformer from HuggingFace. Maybe distilBERT or something else could be tested as well.

### The Methods

I'd probably break this down into three different methods - cosine similarity, traditional ML, and deep learning/LLM.

Cosine similarity seems to be a decent baseline for our classification task. I'd venture to say that the other methods will outperform it. That said, I want to see a high threshold of .7 or .8 to ensure we are classifying with high confidence.

Traditional ML models can include logistic regression, naive bayes, SVM, and perhaps XGBoost and K-NearestNeighbor given their initial ease of testing in sklearn. I'd personally be happy with anything above a .9 on accuracy ()

I think the final and most worthwhile method would be fine-tuning some variation of a BERT model for classification. I've read conflicting research where fine-tuning sometimes outperforms and other times underperforms. My guess is that the data curation might vary on these projects.

## Current State of Project:

- MITRE technique descriptions and cited articles have been scraped into the sqlite3 database here.
- Synthetic data generation is complete via immediate and batch avenues.
- Cosine similarity can be used to compare MITRE descriptions against synthetic text.
  - Initial numbers here show that vastly different techniques tend to have lower similarity scores
  - BUT the matching pairs (original and synthetic) are still hovering between .5 and .7
  - It is worth remembering that a threshold to make distinctions is largely relative.
  - That said, I'd still like to see a .8 threshold being possible.
  - Looking at the texts, the MITRE original texts are very technical in style whereas the synthetic texts are much more like articles.
  - We need to augment the original texts with varying styles and levels of technicality from the synthetic texts.
  - From there we can begin comparing the cited articles against the augmented original texts.

## Immediate TO DO:

- Continue human verification of synthetic texts.
- Begin augmentation of original texts to better capture stylistic and technical detail differences.
- Rerun comparisons based on these augmentations and new synthetic examples.
- Begin tests using augmented originals and article data.
