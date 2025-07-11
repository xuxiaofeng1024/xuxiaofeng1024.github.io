---
uid: 2
layout: publication
title: Adaptive Multiple Control Variates for Many-Light Rendering
authors: <b>Xiaofeng Xu</b>, <a href="https://wanglusdu.github.io/" target="_blank">Lu Wang</a>

publication: Proceedings of Eurographics Symposium on Rendering 2025
doi: https://doi.org/10.2312/sr.20251184   
paper: /files/papers/manylights25.pdf
code (Coming soon):  
slides_pdf: /files/ppts/manylights25.pdf
presentation_slides_video: 
supplementary: /files/supplementary/manylights25/index.html
supplemental_video:
---

## Abstract

Monte Carlo integration estimates the path integral in light transport by randomly sampling light paths and averaging their contributions. However, in scenes with many lights, the resulting estimates suffer from noise and slow convergence due to highfrequency discontinuities introduced by complex light visibility, scattering functions, and emissive properties. To mitigate these challenges, control variates have been employed to approximate the integrand and reduce variance. While previous approaches have shown promise in direct illumination application, they struggle to effciently handle the discontinuities inherent in manylight environments, especially when relying on a single control variate. In this work, we introduce an adaptive method that generates multiple control variates tailored to the spatial distribution and number of lights in the scene. Drawing inspiration from hierarchical light clustering methods like Lightcuts, our approach dynamically determines the number of control variates. We validate our method on the direct illumination problem in scenes with many lights, demonstrating that our adaptive multiple control variates not only outperform single control variate strategy but also achieve a modest improvement over current stateof-the-art many-light sampling techniques.

## Downloads

[Paper (43MB)]({{page.paper}}){: .btn .btn--primary}
[Slides (129MB)]({{page.slides_pdf}}){: .btn .btn--primary}
<!--[Presentation slides video (45MB)]({{page.presentation_slides_video}}){: .btn .btn--primary} -->
[Supplemental results]({{page.supplementary}}){: .btn .btn--primary}
<!--[Supplemental video (629MB)]({{page.supplemental_video}}){: .btn .btn--primary}-->



## Cite

```bib
@inproceedings{xu2025adaptive,
booktitle = {Eurographics Symposium on Rendering},
editor = {Wang, Beibei and Wilkie, Alexander},
title = {{Adaptive Multiple Control Variates for Many-Light Rendering}},
author = {Xu, Xiaofeng and Wang, Lu},
year = {2025},
publisher = {The Eurographics Association},
ISSN = {1727-3463},
ISBN = {978-3-03868-292-9},
DOI = {10.2312/sr.20251184}
}
```
## Copyright Disclaimer
© The Author(s). This is the author’s version of the work. It is posted here for your personal use. Not for redistribution. The definitive version of record is available at <a href="{{page.doi}}">DOI</a>.
