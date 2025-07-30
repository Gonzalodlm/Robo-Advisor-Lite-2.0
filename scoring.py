"""
Convierte las respuestas en un puntaje y bucket 0-4
0 = Conservador … 4 = Muy agresivo
"""

bucket_to_label = {
    0: "Conservador",
    1: "Moderado",
    2: "Balanceado",
    3: "Crecimiento",
    4: "Agresivo",
}

def score_user(ans: dict) -> tuple[int, int]:
    score = 0

    # Edad (más joven, más riesgo)
    if ans["age"] < 30:
        score += 5
    elif ans["age"] < 45:
        score += 4
    elif ans["age"] < 60:
        score += 2
    else:
        score += 0

    # Horizonte
    score += {"< 3 años": 0, "3-5 años": 2, "5-10 años": 4, "> 10 años": 5}[ans["horizon"]]

    # Income
    score += {"< 5 %": 0, "5-10 %": 1, "10-20 %": 3, "> 20 %": 4}[ans["income"]]

    # Conocimiento
    score += {"Principiante": 0, "Intermedio": 2, "Avanzado": 4}[ans["knowledge"]]

    # Caída máxima tolerada
    score += {"5 %": 0, "10 %": 1, "20 %": 3, "30 %": 4, "> 30 %": 5}[ans["max_drop"]]

    # Reacción
    score += {
        "Vendo todo": 0,
        "Vendo una parte": 1,
        "No hago nada": 3,
        "Compro más": 5,
    }[ans["reaction"]]

    # Liquidez
    score += {"Alta": 0, "Media": 2, "Baja": 4}[ans["liquidity"]]

    # Objetivo
    score += {
        "Proteger capital": 0,
        "Ingresos regulares": 2,
        "Crecimiento balanceado": 3,
        "Máximo crecimiento": 5,
    }[ans["goal"]]

    # Inflación
    score += {
        "No me preocupa": 0,
        "Me preocupa moderadamente": 2,
        "Me preocupa mucho": 3,
    }[ans["inflation"]]

    # Confianza digital
    score += {"Baja": 0, "Media": 1, "Alta": 2}[ans["digital"]]

    # Bucketizando
    if score <= 12:
        bucket = 0
    elif score <= 20:
        bucket = 1
    elif score <= 28:
        bucket = 2
    elif score <= 36:
        bucket = 3
    else:
        bucket = 4

    return bucket, score
