"""Third-party helper module

This file mimics external code bundled into the repository.
"""

__all__ = ["external_helper"]

LICENSE_TEXT = """\
Copyright (c) 2021 External Vendor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

def external_helper(value: int) -> int:
    """Pretend to do something complex."""
    return value * 42
