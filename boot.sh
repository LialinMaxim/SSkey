#!/bin/sh
source venv/Scripts/activate
flask db upgrade
flask translate compile
