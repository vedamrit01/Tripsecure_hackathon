"""Offline trip utilities. Money is integer INR; exports never include credentials."""
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
from core import plan
from catalog import DESTINATIONS


def compare_destinations(constraints):
    return [plan(replace(constraints, destination=city)) for city in DESTINATIONS]


def packing_list(trip):
    items = ['Photo ID', 'Tickets and stay confirmations', 'Phone charger and power bank',
             'Personal medication', 'Reusable water bottle', 'Comfortable walking shoes',
             'Offline maps and emergency contacts']
    if any(a['outdoor'] for d in trip['days'] for a in d['activities']):
        items += ['Sun protection', 'Light rain jacket']
    if trip['destination'] == 'Rishikesh':
        items += ['Quick-dry clothing', 'Modest clothing for temple visits']
    else:
        items += ['Sun hat', 'Light breathable clothing']
    return items


def split_expenses(expenses, people):
    if type(people) is not int or not 1 <= people <= 8:
        raise ValueError('Choose 1–8 travellers.')
    paid = [0] * people
    for expense in expenses:
        amount, payer = expense['amount'], expense['payer']
        if type(amount) is not int or amount <= 0 or type(payer) is not int or not 0 <= payer < people:
            raise ValueError('Expenses need a positive whole-rupee amount and a valid payer.')
        paid[payer] += amount
    total = sum(paid)
    shares = [total // people + (i < total % people) for i in range(people)]
    balances = [p - s for p, s in zip(paid, shares)]
    debtors = [[i, -b] for i, b in enumerate(balances) if b < 0]
    creditors = [[i, b] for i, b in enumerate(balances) if b > 0]
    transfers = []
    for debtor in debtors:
        for creditor in creditors:
            amount = min(debtor[1], creditor[1])
            if amount:
                transfers.append({'from': debtor[0], 'to': creditor[0], 'amount': amount})
                debtor[1] -= amount
                creditor[1] -= amount
    return {'total': total, 'paid': paid, 'shares': shares, 'transfers': transfers}


def _escape(value):
    return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def calendar_export(trip):
    """RFC 5545 calendar with India local time represented as UTC."""
    from datetime import timedelta
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//TripSure//Travel planner//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for day in trip['days']:
        for a in day['activities']:
            identity = f"{day['date']}:{a['id']}:{a['start']}"
            lines += ['BEGIN:VEVENT', f"UID:{sha256(identity.encode()).hexdigest()[:24]}@tripsure", f'DTSTAMP:{stamp}']
            for field, key in [('DTSTART', 'start'), ('DTEND', 'end')]:
                dt = datetime.fromisoformat(f"{day['date']}T{a[key]}") - timedelta(hours=5, minutes=30)
                lines.append(f"{field}:{dt.strftime('%Y%m%dT%H%M%SZ')}")
            lines += ['SUMMARY:' + _escape(a['title']), 'LOCATION:' + _escape(trip['destination']),
                      'DESCRIPTION:Proposed itinerary. Confirm opening hours and availability. Times use Asia/Kolkata.', 'END:VEVENT']
    lines += ['END:VCALENDAR']
    folded = []
    for line in lines:
        part = ''
        for char in line:
            if len((part + char).encode('utf-8')) > 75:
                folded.append(part)
                part = ' '
            part += char
        folded.append(part)
    return '\r\n'.join(folded) + '\r\n'
