"""Optional UI tests: installed Streamlit required; core CI stays dependency-free."""
import unittest
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest=None

@unittest.skipUnless(AppTest,'Install requirements.txt to run UI smoke test')
class UITests(unittest.TestCase):
    def test_build_repair_and_security_flow(self):
        at=AppTest.from_file('app.py').run()
        next(b for b in at.button if b.label=='Build my itinerary →').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value,'₹29,480')
        next(n for n in at.number_input if n.label=='Revised budget · INR').set_value(18000)
        next(b for b in at.button if b.label=='Repair my itinerary').click().run()
        self.assertFalse(at.exception)
        self.assertLessEqual(at.session_state['trip']['total'],18000)
        next(b for b in at.button if b.label=='Inspect untrusted text').click().run()
        self.assertFalse(at.exception)
        self.assertIn('Quarantined',at.json[0].value)
    def test_understand_then_build(self):
        at=AppTest.from_file('app.py').run()
        at.text_area[0].set_value('3 days from Delhi for 3 people under ₹40k in Jaipur with culture')
        next(b for b in at.button if b.label=='Understand request').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.selectbox[0].value,'Jaipur')
        next(b for b in at.button if b.label=='Build my itinerary →').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['trip']['constraints']['people'],3)

    def test_expense_packing_and_comparison(self):
        at=AppTest.from_file('app.py').run()
        next(b for b in at.button if b.label=='Build my itinerary →').click().run()
        next(t for t in at.text_input if t.label=='Expense description').set_value('Lunch')
        next(b for b in at.button if b.label=='Add expense').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['expenses'][0]['amount'],500)
        next(c for c in at.checkbox if c.label=='Photo ID').check().run()
        next(b for b in at.button if b.label=='Choose Jaipur').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['trip']['destination'],'Jaipur')
        self.assertEqual(at.session_state['expenses'],[])
        self.assertFalse(next(c for c in at.checkbox if c.label=='Photo ID').value)
