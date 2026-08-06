from honeypot.database import count_logs, get_last_logs, count_suspicious_logs
from honeypot.logger import get_logger

logger = get_logger(__name__)

print("Osszes esemeny:", count_logs())
print("Ebbol gyanus:", count_suspicious_logs())
print()

print("Utolso esemenyek:")
for log in get_last_logs():
    print(log)
