import json
import requests
import time

def get_potent_data(start_date, end_date, terms, token, class_cpc_prefix=None, operator="OR", progress_callback=None):
    
    url = 'https://api.lens.org/patent/search'
    include = ["lens_id", "date_published", "jurisdiction", "biblio", "doc_key", 
               "publication_type", "families", "biblio.publication_reference", 
               "biblio.invention_title.text", "abstract.text", "claims.claims.claim_text"]

    should_clauses = []
    for term in terms:
        should_clauses.extend([
            {
                "match_phrase": {
                    "title": term
                }
            },
            {
                "match_phrase": {
                    "abstract": term
                }
            },
            {
                "match_phrase": {
                    "claim": term
                }
            },
            {
                "match_phrase": {
                    "description": term
                }
            },
            {
                "match_phrase": {
                    "full_text": term
                }
            }
        ])

    if class_cpc_prefix:
        should_clauses.append({
            "prefix": {
                "class_cpc.symbol": class_cpc_prefix
            }
        })

    must_clauses = [
        {
            "bool": {
                "should": should_clauses
            }
        },
        {
            "range": {
                "date_published": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        }
    ]

    query_body = {
        "query": {
            "bool": {
                "must": must_clauses
            }
        },
        "size": 500,
        "scroll": "1m",
        "include": include
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    request_body = json.dumps(query_body)
    
    patents = []
    scroll_id = None

    while True:
        if scroll_id is not None:
            request_body = json.dumps({"scroll_id": scroll_id, "include": include}, ensure_ascii=False)
        response = requests.post(url, data=request_body.encode('utf-8'), headers=headers)
        if response.status_code == requests.codes.too_many_requests:
            print("TOO MANY REQUESTS, waiting...")
            time.sleep(8)
            continue
        if response.status_code != requests.codes.ok:
            print("ERROR:", response)
            break
        response = response.json()
        patents = patents + response['data']
        
        # Calculate progress
        if response['total'] > 0:  # Avoid division by zero
            progress = len(patents) / response['total']
            if progress_callback:
                progress_callback(progress)
        
        if response['scroll_id'] is not None:
            scroll_id = response['scroll_id']
        if len(patents) >= response['total'] or len(response['data']) == 0:
            break

    data_out = {"total": len(patents), "data": patents}
    q = json.dumps(data_out)
    json_data = json.loads(q)
    patent_data = json_data["data"]
    total_results = len(patent_data)
    return patent_data
