---
uid: 1
layout: publication
title: Efficient Caustics Rendering via Spatial and Temporal Path Reuse
authors: <b>Xiaofeng Xu</b>, <a href="https://wanglusdu.github.io/" target="_blank">Lu Wang</a>, <a href="https://wangningbei.github.io/" target="_blank">Beibei Wang</a>

publication: Computer Graphics Forum (Proceedings of Pacific Graphics 2023)
doi:   https://doi.org/10.1111/cgf.14975
paper: /files/PG23_PathReuseCaustics-compressed.pdf
code:  https://github.com/xuxiaofeng1024/specular-manifold-sampling-spatiotemporal-reuse
slides_ppt: 
presentation_slides_video: 
supplementary:
supplemental_video: 
---

## Abstract

Caustics are complex optical effects caused by the light being concentrated in a small area due to reflection or refraction on surfaces with low roughness, typically under a sharp light source. Rendering caustic effects is challenging for Monte Carlo-based approaches, due to the difficulties of sampling the specular paths. One effective solution is using the specular manifold to locate these valid specular paths. Unfortunately, it needs many iterations to find these paths, leading to a long rendering time. To address this issue, our key insight is that the specular paths tend to be similar for neighboring shading points. To this end, we propose to reuse the specular paths spatially. More specifically, we generate some specular path samples with a low sample rate and then reuse these specular path samples as the initialization for specular manifold walk among neighboring shading points. In this way, much fewer specular path-searching iterations are performed, due to the efficient initialization close to the final solution. Furthermore, this reuse strategy can be extended for dynamic scenes in a temporal manner, such as light moving or specular geometry deformation. Our method outperforms current state-of-the-art methods and can handle multiple bounces of light and various scenes.

## Downloads

[Paper (37MB)]({{page.paper}}){: .btn .btn--primary}
[Slides (PPT, 24MB)]({{page.slides_ppt}}){: .btn .btn--primary}
[Presentation slides video (45MB)]({{page.presentation_slides_video}}){: .btn .btn--primary}
[Supplemental video (629MB)]({{page.supplemental_video}}){: .btn .btn--primary}


<!--
## Videos
**Presentation slides video**
{% include video provider="google-drive" id="1KYr1M6VvAITp_PmoRZRk0wgqUIKcTeP5" %}

**Supplemental video**

{% include video provider="google-drive" id="1UkiWnzqS-3kgfQM8rFczyy1JW638jT87" %}
-->

## Cite

```bib
@inproceedings{xu2023efficient,
  title={Efficient Caustics Rendering via Spatial and Temporal Path Reuse},
  author={Xu, Xiaofeng and Wang, Lu and Wang, Beibei},
  booktitle={Computer Graphics Forum},
  pages={e14975},
  year={2023},
  organization={Wiley Online Library}
}
```
## Copyright Disclaimer
© The Author(s). This is the author’s version of the work. It is posted here for your personal use. Not forredistribution. The definitive Version of Record is available at <a href="{{page.doi}}">DOI</a>.
