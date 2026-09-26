"""Deterministic planning and validation. Never executes model-generated code or URLs."""
from dataclasses import dataclass, asdict, replace
from datetime import date, timedelta
from math import ceil
import re
from catalog import ACTIVITIES, DESTINATIONS

@dataclass(frozen=True)
class Constraints:
    origin: str = 'Delhi'
    destination: str = 'Auto'
    days: int = 5
    people: int = 2
    budget: int = 50000
    start_date: str = '2026-10-10'
    interests: tuple = ('nature', 'food')
    pace: str = 'relaxed'

    def validate(self):
        if not isinstance(self.origin,str) or self.origin.strip().lower() not in ('delhi', 'new delhi'):
            raise ValueError('This prototype supports departures from Delhi only. Other origins require transport data.')
        if self.destination not in ('Auto', *DESTINATIONS):
            raise ValueError('Choose Auto, Rishikesh or Jaipur; other destinations are outside the curated demo.')
        for key, low, high in [('days',3,7),('people',1,8),('budget',1000,1000000)]:
            value = getattr(self,key)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f'{key} must be an integer from {low} to {high}.')
        if not isinstance(self.start_date,str):raise ValueError('start_date must be YYYY-MM-DD.')
        date.fromisoformat(self.start_date)
        if self.pace not in ('relaxed','balanced'):
            raise ValueError('Pace must be relaxed or balanced.')
        if not isinstance(self.interests, (list,tuple)) or not 1 <= len(self.interests) <= 6 or any(x not in ('nature','food','culture','wellness','shopping','adventure') for x in self.interests):
            raise ValueError('Choose supported interests.')
        return self

def merge_constraints(base, patch):
    allowed = set(asdict(base))
    if not isinstance(patch, dict) or set(patch) - allowed:
        raise ValueError('Model returned unsupported fields; no changes applied.')
    return replace(base, **patch).validate()

def offline_extract(text, base):
    """Small explicit fallback parser, not an LLM; form values cover unsupported phrasing."""
    if len(text) > 2000:
        raise ValueError('Please keep the request below 2,000 characters.')
    lower = text.lower()
    patch = {}
    for pattern, key in [(r'(\d+)\s*[- ]?days?','days'), (r'(\d+)\s*(?:people|persons|travell?ers)','people')]:
        match = re.search(pattern,lower)
        if match: patch[key] = int(match.group(1))
    match = re.search(r'(?:under|budget(?:\s+is)?|₹|rs\.?|inr)\s*₹?\s*([\d,]+)\s*(k|lakh)?', lower)
    if match: patch['budget'] = int(match.group(1).replace(',','')) * {'k':1000,'lakh':100000,None:1}[match.group(2)]
    for city in DESTINATIONS:
        if city.lower() in lower: patch['destination'] = city
    origin = re.search(r'from\s+([a-z ]+?)(?:\s+for|\s+to|\s+under|[,.]|$)', lower)
    if origin: patch['origin'] = origin.group(1).strip().title()
    interests = [x for x in ('nature','food','culture','wellness','shopping','adventure') if x in lower]
    if interests: patch['interests'] = tuple(interests)
    for pace in ('relaxed','balanced'):
        if pace in lower: patch['pace'] = pace
    return merge_constraints(base,patch)

def _cost(c, dest, items, tier):
    d = DESTINATIONS[dest]
    rooms = ceil(c.people/2)
    lines = {
      'Return transport': d['transport_pp'] * c.people,
      f'Accommodation · {c.days-1} nights / {rooms} room(s)': d[tier+'_room'] * (c.days-1) * rooms,
      'Daily meals': (700 if tier=='comfort' else 450) * c.days * c.people,
      'Local transport': (600 if tier=='comfort' else 350) * c.days,
      'Activities / tasting extras': sum(a['cost_pp']*c.people for a in items),
    }
    subtotal = sum(lines.values())
    lines['Contingency (10%)'] = ceil(subtotal/10)
    return lines

def plan(c, previous=None, locks=(), keep_stay=False, rain_day=None):
    c.validate()
    locks = set(locks)
    if locks and not previous: raise ValueError('Activity locks require an existing plan.')
    if rain_day is not None and (type(rain_day) is not int or not 2 <= rain_day < c.days):
        raise ValueError('Choose an interior trip day for the simulated rain event.')
    if previous and (locks or keep_stay):
        dest = previous['destination']
        if c.destination not in ('Auto', dest): raise ValueError('Unlock saved items before changing destination.')
        if locks and c.start_date != previous['constraints']['start_date']:
            raise ValueError('Unlock activities before changing dates.')
    else:
        dest = c.destination if c.destination != 'Auto' else max(DESTINATIONS,key=lambda d:sum(t in c.interests for t in DESTINATIONS[d]['tags']))
    by_id = {a['id']:a for a in ACTIVITIES[dest]}
    prev_items = {a['id']:a for day in (previous or {}).get('days',[]) for a in day['activities']}
    if locks - set(prev_items): raise ValueError('A locked activity is missing from the previous itinerary.')
    fixed = {}
    for id_ in locks:
        old = prev_items[id_]
        if old['day'] >= c.days: raise ValueError('A locked activity would fall on or after the return day. Unlock it or retain the trip length.')
        if rain_day == old['day'] and old['outdoor']:
            raise ValueError('Rain conflicts with a locked outdoor activity. Unlock it to find an indoor alternative.')
        fixed[(old['day'],old['slot'])] = old
    wanted = set(c.interests)
    candidates = []
    tiers = [previous['tier']] if keep_stay and previous else ['comfort','value']
    for tier in tiers:
      for economy in (False,True):
        used=set(locks); items=[]; days=[]
        for daynum in range(1,c.days+1):
            day = {'day':daynum,'date':(date.fromisoformat(c.start_date)+timedelta(days=daynum-1)).isoformat(),'activities':[]}
            if daynum in (1,c.days):
                day['note'] = f"{'Delhi → '+dest if daynum==1 else dest+' → Delhi'} · allow ~{DESTINATIONS[dest]['travel_hours']} hours (estimate); rest and meals, no fixed sightseeing."
            else:
                for slot in range(2):
                    if (daynum,slot) in fixed:
                        selected=by_id[fixed[(daynum,slot)]['id']]
                    else:
                        available=[a for a in by_id.values() if a['id'] not in used and not (rain_day==daynum and a['outdoor'])]
                        if not available: continue
                        def score(a):
                            match=len(wanted.intersection(a['tags']))
                            return (-(a['cost_pp']) if economy else match*1000-a['cost_pp'], match)
                        selected=max(available,key=score)
                    used.add(selected['id'])
                    item=dict(selected,day=daynum,slot=slot,start='10:00' if slot==0 else '15:00',end=f"{(10 if slot==0 else 15)+selected['hours']:02}:00",locked=selected['id'] in locks)
                    day['activities'].append(item);items.append(item)
                day['note']='Two spacious activity windows; lunch, rest and a transfer buffer between them. Times are proposals; opening hours and local transfers need confirmation.'
            days.append(day)
        costs=_cost(c,dest,items,tier)
        matched = sum(len(wanted.intersection(a['tags'])) for a in items)
        candidates.append({'destination':dest,'constraints':asdict(c),'days':days,'tier':tier,'costs':costs,'total':sum(costs.values()),'preference_matches':matched,'rain_day':rain_day})
    feasible=[p for p in candidates if p['total']<=c.budget]
    result=max(feasible,key=lambda p:(p['preference_matches'],p['tier']=='comfort')) if feasible else min(candidates,key=lambda p:p['total'])
    result['within_budget']=result['total']<=c.budget
    result['checks'] = validate_plan(result, previous, locks, keep_stay)
    result['trace'] = [f"catalog_lookup: {dest}; {len(by_id)} curated activities",f"constraint_solver: evaluated {len(candidates)} price/preference combinations",f"calculate_costs: integer INR; {ceil(c.people/2)} rooms; {c.days-1} nights; 10% contingency",f"validate_plan: {sum(result['checks'].values())}/{len(result['checks'])} internal checks passed"]
    return result

def validate_plan(p, previous=None, locks=(), keep_stay=False):
    c = Constraints(**p['constraints']).validate()
    items=[a for d in p['days'] for a in d['activities']]
    current={a['id']:a for a in items}
    old={a['id']:a for d in (previous or {}).get('days',[]) for a in d['activities']}
    return {
      'Budget including contingency':p['total']<=c.budget,
      'Cost arithmetic':sum(p['costs'].values())==p['total'],
      'Requested trip length':len(p['days'])==c.days,
      'No duplicate activities':len(current)==len(items),
      'At most two activities per day':all(len(d['activities'])<=2 for d in p['days']),
      'No overlapping activity windows':all(all(a['end']<=b['start'] for a,b in zip(d['activities'],d['activities'][1:])) for d in p['days']),
      'Arrival and return days reserved':not p['days'][0]['activities'] and not p['days'][-1]['activities'],
      'Locked activities preserved':all(id_ in current and current[id_]['day']==old[id_]['day'] and current[id_]['slot']==old[id_]['slot'] for id_ in locks),
      'Accommodation tier preserved':not keep_stay or previous is None or p['tier']==previous['tier'],
      'Rain scenario respected':all(not a['outdoor'] for a in items if a['day']==p['rain_day']),
      'Activities have source references':all(a['source'] for a in items),
    }

def differences(old,new):
    changes=[]
    if old['total'] != new['total']:changes.append(f"Estimated total: ₹{old['total']:,} → ₹{new['total']:,} ({new['total']-old['total']:+,} INR)")
    if old['tier'] != new['tier']:changes.append(f"Accommodation: {old['tier']} → {new['tier']}")
    before={(d['day'],a['slot']):a['title'] for d in old['days'] for a in d['activities']}
    after={(d['day'],a['slot']):a['title'] for d in new['days'] for a in d['activities']}
    for key in sorted(set(before)|set(after)):
        if before.get(key)!=after.get(key):changes.append(f"Day {key[0]}, {'morning' if key[1]==0 else 'afternoon'}: {before.get(key,'free time')} → {after.get(key,'free time')}")
    return changes or ['No itinerary or cost changes were needed.']
