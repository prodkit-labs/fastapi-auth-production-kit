# Password Hashing

The default local app uses bcrypt because it is widely available, easy to inspect, and works well for a small starter. Bcrypt has a 72-byte input limit, so this repo enforces that limit on the default register and password reset flows.

For modern production systems, Argon2id is usually a stronger default when your runtime can support it.

## Bcrypt Path

Install:

```bash
python -m pip install -e .
```

Behavior:

- Uses `passlib` bcrypt hashing.
- Enforces passwords of 72 bytes or fewer.
- Keeps the quickstart dependency set small.

Good fit:

- local demos
- internal prototypes
- compatibility-first apps

Watch:

- 72-byte input limit
- migration planning if you later move to Argon2id

## Argon2id Track

Install:

```bash
python -m pip install -e '.[argon2]'
```

Helpers:

```python
from prodkit_auth.security import hash_password_argon2id, verify_password_argon2id

password_hash = hash_password_argon2id("correct horse battery staple")
assert verify_password_argon2id("correct horse battery staple", password_hash)
```

Good fit:

- new production apps
- apps with stricter password storage requirements
- teams that can tune memory and time cost for their runtime

Watch:

- memory cost in small containers
- latency impact during login spikes
- migration for existing bcrypt hashes

## Migration Pattern

A common migration path:

1. Keep bcrypt verification enabled for existing users.
2. Hash new passwords with Argon2id.
3. On successful bcrypt login, rehash the password with Argon2id.
4. Track migration progress.
5. Remove bcrypt only when no bcrypt hashes remain.

`verify_password_any()` can verify either bcrypt or Argon2id hashes based on the stored hash prefix.
