from honeypot.database import count_logs, get_last_logs

print("Összes esemény:", count_logs())

print()

print("Utolsó események:")

for log in get_last_logs():
    print(log)