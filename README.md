# MITRE Text Classification

    ##  Current State of Project:
    -   MITRE technique descriptions and cited articles have been scraped into the sqlite3 database here.
    -   Synthetic data generation is complete via immediate and batch avenues.
    -   Cosine similarity can be used to compare MITRE descriptions against synthetic text.
        -   Initial numbers here show that vastly different techniques tend to have lower similarity scores
        -   BUT the matching pairs (original and synthetic) are still hovering between .5 and .7
        -   It is worth remembering that a threshold to make distinctions is largely relative.
        -   That said, I'd still like to see a .8 threshold being possible.
        -   Looking at the texts, the MITRE original texts are very technical in style whereas the synthetic texts are much more like articles.
        -   We need to augment the original texts with varying styles and levels of technicality from the synthetic texts.
        -   From there we can begin comparing the cited articles against the augmented original texts.
    ##  Immediate TO DO:
    -   Continue human verification of synthetic texts.
    -   Begin augmentation of original texts to better capture stylistic and technical detail differences.
    -   Rerun comparisons based on these augmentations and new synthetic examples.
    -   Begin tests using augmented originals and article data.
