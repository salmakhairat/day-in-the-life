from datetime import datetime
import random
import string

def current_time() -> str:
    return datetime.now().strftime("%B %d, %Y at %H:%M:%S")

def gen_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
