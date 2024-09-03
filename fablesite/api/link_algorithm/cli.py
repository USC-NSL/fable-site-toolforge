import re
import json
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import os

os.chdir('fablesite/api/link_algorithm')

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

def identify_constants(urls):
    if not urls:
        return []
    
    tokenized_urls = [tokenize_url(url)['path'] for url in urls]
    min_length = min(len(path) for path in tokenized_urls)
    
    constants = []
    for i in range(min_length):
        if all(path[i] == tokenized_urls[0][i] for path in tokenized_urls):
            constants.append(tokenized_urls[0][i])
        else:
            break
    
    return constants

def tokenize_url_segments(url, constants):
    parsed = urlparse(url)
    path = parsed.path.strip('/').split('/')
    
    tokenized = f"{parsed.netloc}"
    next_token = 1
    
    for segment in path:
        if segment in constants:
            tokenized += f"/{segment}"
        else:
            tokenized += f"/${next_token}"
            next_token += 1
    
    if url.endswith('.html'):
        tokenized += '.html'
    
    return tokenized

def process_urls(data):
    domains = defaultdict(lambda: {'old': [], 'new': []})
    for item in data:
        domain = urlparse(item['link']).netloc
        domains[domain]['old'].append(item['link'])
        domains[domain]['new'].append(item['alias'])
    
    patterns = {}
    for domain, urls in domains.items():
        old_constants = identify_constants(urls['old'])
        new_constants = identify_constants(urls['new'])
        
        old_tokenized = [tokenize_url_segments(url, old_constants) for url in urls['old']]
        new_tokenized = [tokenize_url_segments(url, new_constants) for url in urls['new']]
        
        patterns[domain] = {
            'old_constants': old_constants,
            'new_constants': new_constants,
            'old_tokenized': old_tokenized[:2],  
            'new_tokenized': new_tokenized[:2], 
            'old_urls': urls['old'][:2], 
            'new_urls': urls['new'][:2] 
        }
    
    return patterns

def main():
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    patterns = process_urls(data)
    
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
                print(f"Constants in old URLs: {pattern['old_constants']}")
                print(f"Constants in new URLs: {pattern['new_constants']}")
                
                for i in range(min(len(pattern['old_urls']), len(pattern['new_urls']))):
                    print(f"\nExample {i+1}:")
                    print(f"Old URL: {pattern['old_urls'][i]}")
                    print(f"New URL: {pattern['new_urls'][i]}")
                    print(f"Old URL (tokenized): {pattern['old_tokenized'][i]}")
                    print(f"New URL (tokenized): {pattern['new_tokenized'][i]}")
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()