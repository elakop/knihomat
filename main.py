#!/usr/bin/env python3

import os
import sys

# Přidání aktuálního adresáře do Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PLIN053_bookswap import BookSellingApp

if __name__ == '__main__':
    BookSellingApp().run()
    