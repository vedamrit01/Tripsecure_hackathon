import unittest
from core import Constraints, plan
from companion import calendar_export, compare_destinations, split_expenses, packing_list

class CompanionTests(unittest.TestCase):
    def test_calendar_india_time_and_event_count(self):
        trip=plan(Constraints())
        data=calendar_export(trip)
        self.assertEqual(data.count('BEGIN:VEVENT'),sum(len(d['activities']) for d in trip['days']))
        self.assertIn('DTSTART:20261011T043000Z',data)
        self.assertTrue(all(len(line.encode())<=75 for line in data.split('\r\n')))

    def test_settlement_conserves_every_rupee(self):
        result=split_expenses([{'amount':1001,'payer':0},{'amount':200,'payer':2}],3)
        self.assertEqual(sum(result['shares']),1201)
        balances=[paid-share for paid,share in zip(result['paid'],result['shares'])]
        for t in result['transfers']:
            balances[t['from']]+=t['amount']
            balances[t['to']]-=t['amount']
        self.assertEqual(balances,[0,0,0])

    def test_invalid_expense_rejected(self):
        for expense in [{'amount':-1,'payer':0},{'amount':100,'payer':3}]:
            with self.assertRaises(ValueError):split_expenses([expense],2)

    def test_comparison_preserves_constraints(self):
        c=Constraints(people=3,budget=30000)
        choices=compare_destinations(c)
        self.assertEqual({p['destination'] for p in choices},{'Jaipur','Rishikesh'})
        for p in choices:
            self.assertEqual(p['constraints']['people'],3)
            self.assertEqual(p['constraints']['budget'],30000)
        self.assertEqual(c.destination,'Auto')
        self.assertIn('Photo ID',packing_list(choices[0]))
