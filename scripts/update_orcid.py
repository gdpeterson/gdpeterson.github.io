#!/usr/bin/env python3
"""Fetch public ORCID works, merge DOI metadata where available, and update CSL JSON.

This script only updates machine-managed bibliographic fields. Human-reviewed themes,
questions, summaries, and featured status live in data/publication-curation.json.
"""
from __future__ import annotations
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORCID=os.environ.get('ORCID_ID','0000-0003-0173-0112')
MAILTO=os.environ.get('CROSSREF_MAILTO','garry.peterson@su.se')
UA=f'garrypeterson-academic-site/1.0 (mailto:{MAILTO})'

def get_json(url, accept='application/json'):
    req=urllib.request.Request(url,headers={'Accept':accept,'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=30) as response: return json.load(response)

def crossref(doi):
    try:
        return get_json('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))['message']
    except Exception as exc:
        print(f'Crossref lookup failed for {doi}: {exc}'); return {}

def issued(parts):
    if not parts: return {}
    return {'date-parts':[[int(x) for x in parts if x]]}

def main():
    record=get_json(f'https://pub.orcid.org/v3.0/{ORCID}/works','application/vnd.orcid+json')
    out=[]
    for group in record.get('group',[]):
        summaries=group.get('work-summary',[])
        if not summaries: continue
        summary=summaries[0]
        ids={x.get('external-id-type','').lower():x.get('external-id-value') for x in summary.get('external-ids',{}).get('external-id',[]) if x.get('external-id-value')}
        doi=(ids.get('doi') or '').lower().replace('https://doi.org/','').replace('http://doi.org/','')
        cr=crossref(doi) if doi else {}
        title=(summary.get('title',{}).get('title',{}) or {}).get('value') or (cr.get('title') or [''])[0]
        year=(summary.get('publication-date') or {}).get('year',{}).get('value')
        authors=[]
        for a in cr.get('author',[]): authors.append({'given':a.get('given',''),'family':a.get('family',''),'ORCID':a.get('ORCID','')})
        out.append({'id':f'orcid:{summary.get("put-code")}', 'orcid_put_code':str(summary.get('put-code')),'type':cr.get('type') or summary.get('type','').lower().replace('_','-'),'title':title,'author':authors,'container-title':(cr.get('container-title') or [summary.get('journal-title',{}).get('value','')])[0],'issued':cr.get('issued') or issued([year] if year else []),'volume':cr.get('volume',''),'issue':cr.get('issue',''),'page':cr.get('page',''),'DOI':doi,'URL':cr.get('URL') or summary.get('url',{}).get('value','')})
        time.sleep(.05)
    (ROOT/'data/publications-csl.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/orcid-sync.json').write_text(json.dumps({'orcid':ORCID,'last_synced':datetime.now(timezone.utc).date().isoformat(),'record_count':len(out)},indent=2)+'\n')
    print(f'Updated {len(out)} ORCID works')
if __name__=='__main__': main()
