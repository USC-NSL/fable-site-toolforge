import re
import json
from urllib.parse import urlparse, parse_qs, urlencode
from collections import defaultdict

def is_likely_title(segment):
    return bool(re.match(r'^[a-z0-9-]+$', segment) and not segment.isdigit())

def tokenize_url(url):
    parsed = urlparse(url.replace('url=', '', 1)) 
    path = parsed.path.strip('/').split('/')
    query = parse_qs(parsed.query)
    
    extension = None
    if path and '.' in path[-1]:
        path[-1], extension = path[-1].rsplit('.', 1)
    
    return {
        'scheme': parsed.scheme,
        'domain': parsed.netloc,
        'path': path,
        'query': query,
        'extension': extension
    }

def identify_pattern(old_urls, new_urls):
    old_tokens = [tokenize_url(url) for url in old_urls]
    new_tokens = [tokenize_url(url) for url in new_urls]
    
    pattern = {
        'scheme': 'change' if any(old['scheme'] != new['scheme'] for old, new in zip(old_tokens, new_tokens)) else 'keep',
        'domain': ('change', old_tokens[0]['domain'], new_tokens[0]['domain']) if old_tokens[0]['domain'] != new_tokens[0]['domain'] else 'keep',
        'path': [],
        'query': [],
        'extension': 'change' if any(old['extension'] != new['extension'] for old, new in zip(old_tokens, new_tokens)) else 'keep'
    }
    
    max_path_len = max(max(len(old['path']), len(new['path'])) for old, new in zip(old_tokens, new_tokens))
    
    for i in range(max_path_len):
        old_segments = [old['path'][i] if i < len(old['path']) else None for old in old_tokens]
        new_segments = [new['path'][i] if i < len(new['path']) else None for new in new_tokens]
        
        if all(new == 'archive' for new in new_segments if new is not None):
            pattern['path'].append(('keep', 'archive'))
        elif all(seg is not None and seg.isdigit() and len(seg) == 4 for seg in old_segments):
            pattern['path'].append(('year',))
        elif all(seg is not None and seg.isdigit() and len(seg) <= 2 for seg in old_segments):
            pattern['path'].append(('month_or_day',))
        elif all(seg is not None and seg.isdigit() and len(seg) > 4 for seg in old_segments):
            pattern['path'].append(('article_id',))
        else:
            pattern['path'].append(('variable',))
    
    all_query_keys = set().union(*(old['query'].keys() for old in old_tokens)).union(*(new['query'].keys() for new in new_tokens))
    
    for key in all_query_keys:
        old_values = [old['query'].get(key, [None])[0] for old in old_tokens]
        new_values = [new['query'].get(key, [None])[0] for new in new_tokens]
        
        if all(old == new for old, new in zip(old_values, new_values) if old is not None and new is not None):
            pattern['query'].append(('keep', key))
        elif all(new == new_values[0] for new in new_values if new is not None):
            pattern['query'].append(('change', key, new_values[0]))
        elif all(new is None for new in new_values):
            pattern['query'].append(('remove', key))
        elif all(old is None for old in old_values):
            pattern['query'].append(('add', key, new_values[0]))
        else:
            pattern['query'].append(('variable', key))
    
    return pattern

def tokenize_url_segments(old_url, new_url):
    def parse_url(url):
        parsed = urlparse(url)
        path = parsed.path.strip('/').split('/')
        if path[-1].endswith('.html'):
            path[-1] = path[-1][:-5]  
        return parsed.netloc, path, parse_qs(parsed.query)

    old_netloc, old_path, old_query = parse_url(old_url)
    new_netloc, new_path, new_query = parse_url(new_url)

    old_tokenized = f"{old_netloc}"
    new_tokenized = f"{new_netloc}"

    segment_map = {}
    next_token = 1

    for segment in old_path:
        if segment not in segment_map:
            segment_map[segment] = f"${next_token}"
            next_token += 1
        old_tokenized += f"/{segment_map[segment]}"

    for segment in new_path:
        if segment in segment_map:
            new_tokenized += f"/{segment_map[segment]}"
        else:
            new_tokenized += f"/${next_token}"
            next_token += 1

    if new_url.endswith('.html'):
        new_tokenized += '.html'

    return old_tokenized, new_tokenized

def process_urls(data):
    domains = defaultdict(lambda: {'old': [], 'new': []})
    for item in data:
        domain = urlparse(item['link']).netloc
        domains[domain]['old'].append(item['link'])
        domains[domain]['new'].append(item['alias'])
    
    domains = {k: v for k, v in domains.items() if len(v['old']) > 1}
    
    patterns = {}
    for domain, urls in domains.items():
        patterns[domain] = identify_pattern(urls['old'], urls['new'])
    
    return patterns, domains

def main():
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    patterns, domains = process_urls(data)
    
    while True:
        print("\nAvailable domains:")
        for i, domain in enumerate(patterns.keys(), 1):
            print(f"{i}. {domain}")
        
        choice = input("\nEnter the number of the domain to see its pattern (or 'q' to quit): ")
        
        if choice.lower() == 'q':
            break
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(patterns):
                domain = list(patterns.keys())[choice - 1]
                pattern = patterns[domain]
                print(f"\nPattern for {domain}:")
                
                old_urls = domains[domain]['old'][:2]
                new_urls = domains[domain]['new'][:2]
                for i, (old, new) in enumerate(zip(old_urls, new_urls), 1):
                    print(f"\nExample {i}:")
                    print(f"Old URL: {old}")
                    print(f"New URL: {new}")
                    old_tokenized, new_tokenized = tokenize_url_segments(old, new)
                    print(f"Old URL (tokenized): {old_tokenized}")
                    print(f"New URL (tokenized): {new_tokenized}")
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
        
        input("\nPress Enter to continue...")



if __name__ == "__main__":
    main()