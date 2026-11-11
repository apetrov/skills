#!/usr/bin/env python3
"""Convert CSV files to Markdown, rounding numbers to four decimal places."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


def format_cell(value):
    try:
        number = Decimal(value)
        if number.is_finite():
            value = format(number, '.4f').rstrip('0').rstrip('.')
            if value == '-0':
                value = '0'
    except InvalidOperation:
        pass
    return (value.replace('\\', '\\\\').replace('|', '\\|')
            .replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>'))


def convert(source):
    with source.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.reader(stream))
    if not rows:
        raise ValueError(f'{source} is empty')
    lines = ['| ' + ' | '.join(map(format_cell, rows[0])) + ' |',
             '| ' + ' | '.join(['---'] * len(rows[0])) + ' |']
    lines.extend('| ' + ' | '.join(map(format_cell, row)) + ' |'
                 for row in rows[1:])
    target = source.with_suffix('.md')
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Created {target}: {len(rows) - 1} data rows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path, help='CSV files to convert')
    args = parser.parse_args()
    for source in args.files:
        convert(source)
