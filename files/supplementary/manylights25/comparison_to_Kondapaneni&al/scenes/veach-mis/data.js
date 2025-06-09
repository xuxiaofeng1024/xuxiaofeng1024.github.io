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
                    "title": "Salaün et al. Order 1 polynomial",
                    "version": "-",
                    "image": "Salaün et al._O1.png"
                },
                {
                    "title": "Ours Order 1 polynomial",
                    "version": "-",
                    "image": "Ours(fixed).png"
                },
                {
                    "title": "BSDF + Light (balance)",
                    "version": "-",
                    "image": "BSDF_Light_balance_24i.png"
                },
                {
                    "title": "BSDF + Light (power)",
                    "version": "-",
                    "image": "BSDF_Light_power_24i.png"
                },
                {
                    "title": "Uniform + Trained (Optimal)",
                    "version": "-",
                    "image": "BSDF_Light_optimal_direct_24i.png"
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
                    "title": "Salaün et al. Order 1 polynomial",
                    "version": "-",
                    "image": "Salaün et al._O1-relMSE.png"
                },
                {
                    "title": "Ours Order 1 polynomial",
                    "version": "-",
                    "image": "Ours(fixed)-relMSE.png"
                },
                {
                    "title": "BSDF + Light (balance)",
                    "version": "-",
                    "image": "relMSE_BSDF_Light_balance_24i.png"
                },
                {
                    "title": "BSDF + Light (power)",
                    "version": "-",
                    "image": "relMSE_BSDF_Light_power_24i.png"
                },
                {
                    "title": "Uniform + Trained (Optimal)",
                    "version": "-",
                    "image": "relMSE_BSDF_Light_optimal_direct_24i.png"
                }
            ]
        }
    ],
    "stats": [
        {
            "title": "Stats",
            "labels": [
                "Salaün et al. Order 1 polynomial",
                "Ours Order 1 polynomial",
                "BSDF + Light (balance)",
                "BSDF + Light (power)",
                "BSDF + Light (optimal)"
            ],
            "series": [
                {
                    "label": "Time(s)",
                    "data": [
                        "5.0",
                        "5.5",
                        "5.0",
                        "5.0",
                        "5.0"
                    ],
                    "track": {
                        "x": [],
                        "y": []
                    }
                },
                {
                    "label": "relMSE",
                    "data": [
                        "0.008604",
                        "00.002557",
                        "0.002973",
                        "0.003036",
                        "0.002924"

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
