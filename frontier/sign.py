"""The acceptance ceremony: a human signs the frontier's root hash with an Ed25519 key.
This is the ONLY step that turns re-derived state into accepted state. No model is anywhere
in this path — the signature is over frozen, re-derivable content, produced by a person.

  python frontier/sign.py            # prompts for one confirmation
  python frontier/sign.py --yes      # non-interactive (demo)
"""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from frontier.verify import verify

FR = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(FR, ".prospect_signing_key")     # gitignored
SIG = os.path.join(FR, "frontier.sig.json")

def load_key():
    if os.path.exists(KEY):
        return serialization.load_pem_private_key(open(KEY, "rb").read(), password=None)
    k = Ed25519PrivateKey.generate()
    open(KEY, "wb").write(k.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    os.chmod(KEY, 0o600)
    return k

def main():
    ok, root = verify()
    if not ok:
        sys.exit("refusing to sign: frontier does not re-derive from frozen data")
    if "--yes" not in sys.argv:
        ans = input(f"\nSign frontier {root} as accepted state? [type 'sign'] ")
        if ans.strip() != "sign":
            sys.exit("not signed")
    k = load_key()
    sig = k.sign(root.encode()).hex()
    pub = k.public_key().public_bytes(serialization.Encoding.Raw,
        serialization.PublicFormat.Raw).hex()
    rec = {"root": root, "signature": sig, "pubkey": pub,
           "signer": os.environ.get("USER", "human"),
           "signed_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "note": "signed over frozen re-derivable content; no model in the trust path"}
    json.dump(rec, open(SIG, "w"), indent=2)
    print(f"\nsigned: {root} by {rec['signer']} -> {SIG}")

if __name__ == "__main__":
    main()
