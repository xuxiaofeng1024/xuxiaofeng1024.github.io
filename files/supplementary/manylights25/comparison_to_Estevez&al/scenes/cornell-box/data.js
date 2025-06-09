const data =
{
    "imageBoxes": [
        {
            "title": "Images",
            "elements": [
                {
                    "title": "Reference",
                    "version": "-",
                    "image": "Reference.png"
                },             
                {
                    "title": "Estevez et al.(adaptive tree splitting)",
                    "version": "-",
                    "image": "bvh_cornell-box_dl_spp316.png"
                },
                {
                    "title": "Ours Order 1 polynomial",
                    "version": "-",
                    "image": "Ours.png"
                }
            ]
        },
        {
            "title": "relMSE",
            "elements": [
                  {
                    "title": "Reference",
                    "version": "-",
                    "image": "Reference.png"
                },
                {
                    "title": "Estevez et al.(adaptive tree splitting)",
                    "version": "-",
                    "image": "relMSE_bvh_cornell-box_dl_spp316.png"
                },
                {
                    "title": "Ours Order 1 polynomial",
                    "version": "-",
                    "image": "relMSE_Ours.png"
                }
            ]
        }
    ],
    "stats": [
        {
            "title": "Stats",
            "labels": [
                "Estevez et al.(adaptive tree splitting)",
                "Ours Order 1 polynomial"
            ],
            "series": [
                {
                    "label": "Time(s)",
                    "data": [
                        "73.5",
                        "81.5"         
                    ],
                    "track": {
                        "x": [],
                        "y": []
                    }
                },
                {
                    "label": "relMSE",
                    "data": [
                        "0.028165",
                        "0.027410"
                    ],
                    "track": {
                        "x": [],
                        "y": []
                    }
                }
            ]
        }
    ]
}
