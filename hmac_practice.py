import hashlib
import hmac

#h1
word1 = "Apple"
word2 = "apple"

hash1 = hashlib.sha256(word1.encode("utf-8")).hexdigest()
hash2 = hashlib.sha256(word2.encode("utf-8")).hexdigest()

print(f"Word: '{word1}' -> Hash: {hash1}")
print(f"Word: '{word2}' -> Hash: {hash2}")
print(f"Length of hash: {len(hash1)} characters\n")


#h2
def sign(secret: str, message: str) -> str:
    """Signs raw bytes of a message using a secret key with HMAC-SHA256."""
    # H4 Reminder: We convert to raw bytes (utf-8) because cryptographic 
    # functions operate on exact byte streams, not parsed/reordered structures.
    secret_bytes = secret.encode("utf-8")
    message_bytes = message.encode("utf-8")
    
    signature = hmac.new(secret_bytes, message_bytes, hashlib.sha256)
    return signature.hexdigest()

my_secret = "super_secret_club_key"
my_message = "Hello world!"

valid_signature = sign(my_secret, my_message)
print(f"Generated Signature: {valid_signature}\n")


#h3
def verify(secret: str, message: str, provided_signature: str) -> bool:
    """
    Recomputes the expected signature and compares it safely 
    using hmac.compare_digest to prevent timing attacks.
    """
    if not provided_signature:
        return False
        
    expected_signature = sign(secret, message)
    return hmac.compare_digest(expected_signature, provided_signature)


#h5
def run_tests():
    secret = "my_safe_password"
    message = "Webhook payload data"
    
    good_sig = sign(secret, message)
    
    assert verify(secret, message, good_sig) == True, "Test 1 Failed!"
    print(" [X] Test 1: Right secret passes -> PASSED")
    
    assert verify("wrong_password", message, good_sig) == False, "Test 2 Failed!"
    print(" [X] Test 2: Wrong secret fails -> PASSED")
    
    corrupted_message = "Webhook payload datA"  
    assert verify(secret, corrupted_message, good_sig) == False, "Test 3 Failed!"
    print(" [X] Test 3: One changed letter fails -> PASSED")

    assert verify(secret, message, "") == False, "Test 4 Failed!"
    print(" [X] Test 4: Empty signature fails -> PASSED")

if __name__ == "__main__":
    run_tests()

