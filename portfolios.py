# Carteras modelo con los nuevos activos

MODEL_PORTFOLIOS = {
    0: {  # Conservador
        "BIL": 0.30,   # Efectivo/T-Bills
        "AGG": 0.50,   # Bonos
        "ACWI": 0.10,  # Acciones globales
        "GLD": 0.10,   # Oro
    },
    1: {  # Moderado
        "BIL": 0.15,
        "AGG": 0.35,
        "ACWI": 0.30,
        "VNQ": 0.10,   # REITs
        "GLD": 0.10,
    },
    2: {  # Balanceado
        "BIL": 0.05,
        "AGG": 0.25,
        "ACWI": 0.45,
        "VNQ": 0.15,
        "GLD": 0.10,
    },
    3: {  # Crecimiento
        "AGG": 0.15,
        "ACWI": 0.65,
        "VNQ": 0.15,
        "GLD": 0.05,
    },
    4: {  # Agresivo
        "ACWI": 0.80,
        "VNQ": 0.15,
        "GLD": 0.05,
    },
}
