from config import CONFIG


# Analytic M/M/1 mean waiting time (deterministic; no random arrivals).
# 250 is a calibrated scaling of the mean wait, in ms.
def queue_delay_ms(arrival_rate):
    mu = CONFIG['service_rate']
    lam = float(arrival_rate)
    if lam <= 0:
        return 0.0
    if lam >= mu:
        return CONFIG['congestion_cap_ms']
    # M/M/1 queue waiting time in seconds => lambda / (mu * (mu - lambda))
    wait_s = lam / (mu * (mu - lam))
    return 250.0 * wait_s


def throughput(arrival_rate, success_ratio=1.0):
    service_rate = CONFIG['service_rate']
    return min(arrival_rate, service_rate) * success_ratio
