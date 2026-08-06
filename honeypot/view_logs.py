from honeypot.database import get_logs, count_suspicious_logs
from honeypot.logger import get_logger

logger = get_logger(__name__)


def main():
    logs = get_logs()

    print("\n===== MQTT Naploak =====\n")

    for log in logs:
        (log_id, timestamp, topic, payload, client_id, payload_size, is_suspicious) = log
        flag = "GYANUS" if is_suspicious else "-"
        print(
            f"[{log_id}] {timestamp} | topic={topic} | client_id={client_id} "
            f"| meret={payload_size}B | {flag} | payload={payload}"
        )

    print(f"\nOsszesen gyanus uzenet: {count_suspicious_logs()}")


if __name__ == "__main__":
    main()
