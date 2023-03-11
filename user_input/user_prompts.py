#!/usr/bin/env python3

def user_continue(prompt):
    should_continue = None
    while should_continue not in ("y","n","q"):
        should_continue = input("%s (y/n): "%prompt).lower()
        if should_continue not in ("y","n","q"):
            print("Unrecognized argument")
    if should_continue in ("n","q"):
        return False
    else:
        return True