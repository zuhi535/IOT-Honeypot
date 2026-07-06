from honeypot.database import get_logs

logs = get_logs()

print("\n===== MQTT Naplók =====\n")

for log in logs:
    print(log)