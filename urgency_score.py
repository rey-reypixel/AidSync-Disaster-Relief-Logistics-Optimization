def urgency(deaths, severity, weather, population):
    score = (
        (deaths / 100) * 0.8+
        (severity / 10) * 0.6 +
        (weather / 3) * 0.4 +
        (population / 1000) * 0.2
    )
    return min(score, 1.0)


