import re
import json
from urllib.parse import urlparse, parse_qs, urlunsplit
from collections import defaultdict
import os

os.chdir('fablesite/api/link_algorithm')
def segment_to_regex(segment):
    if segment.isalpha():
        return r'[a-zA-Z]+'
    elif segment.isdigit():
        return r'\d+'
    else:
        return r'[a-zA-Z0-9]+'
def sanitize_url(url):
    if url.startswith('url='):
        url = url[4:]
    
    parsed = urlparse(url)
    
    scheme = parsed.scheme.lower() or 'http'
    
    domain = parsed.netloc.lower()
    
    path = parsed.path.strip('/').split('/')
    
    if path and '.' in path[-1]:
        name, ext = path[-1].rsplit('.', 1)
        path[-1] = f"{name}.{ext.lower()}"
    
    path = '/'.join(path)
    
    clean_url = urlunsplit((scheme, domain, f"/{path}", parsed.query, parsed.fragment))
    
    return clean_url

def tokenize_url(url):
    url = sanitize_url(url)
    parsed = urlparse(url)
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
    segments = []
    
    for segment in path:
        if segment in constants:
            tokenized += f"/{segment}"
        else:
            token = f"${len(segments) + 1}"
            tokenized += f"/{token}"
            segments.append(segment)
    
    return tokenized, segments

def generate_regex_pattern(url, constants):
    parsed = urlparse(url)
    path = parsed.path.strip('/').split('/')
    regex_parts = [re.escape(parsed.netloc)]
    
    for segment in path:
        if segment in constants:
            regex_parts.append(re.escape(segment))
        elif segment.isdigit():
            regex_parts.append(r'\d+')
        else:
            regex_parts.append(r'[a-zA-Z0-9-]+')
    
    return '/'.join(regex_parts)

def process_urls(data):
    domains = defaultdict(lambda: {'old': [], 'new': []})
    for item in data:
        domain = urlparse(item['link']).netloc
        domains[domain]['old'].append(item['link'])
        domains[domain]['new'].append(item['alias'])
    
    patterns = {}
    all_domains = {}
    for domain, urls in domains.items():
        if len(urls['old']) == 1:
            patterns[domain] = "Unpredictable due to missing training"
        else:
            old_constants = identify_constants(urls['old'])
            new_constants = identify_constants(urls['new'])
            
            old_tokenized = []
            new_tokenized = []
            old_regex = []
            new_regex = []
            is_predictable = True
            for old_url, new_url in zip(urls['old'], urls['new']):
                old_token, old_segments = tokenize_url_segments(old_url, old_constants)
                new_token, new_segments = tokenize_url_segments(new_url, new_constants)

                old_variables = [seg for seg in old_token.split('/') if seg.startswith('$')]
                new_variables = [seg for seg in new_token.split('/') if seg.startswith('$')]

                if len(new_variables) > len(old_variables):
                    is_predictable = False
                    break             
                
                
                old_mapping = {seg.lower(): f"${i+1}" for i, seg in enumerate(old_segments)}
                
                new_tokenized_segments = []
                next_token = len(old_segments) + 1
                for seg in new_segments:
                    if seg.lower() in old_mapping:
                        new_tokenized_segments.append(old_mapping[seg.lower()])
                    else:
                        new_tokenized_segments.append(f"${next_token}")
                        next_token += 1
                
                new_tokenized_url = f"{urlparse(new_url).netloc}"
                new_path = urlparse(new_url).path.strip('/').split('/')
                variable_segment_index = 0
                
                for seg in new_path:
                    if seg in new_constants:
                        new_tokenized_url += f"/{seg}"
                    else:
                        if variable_segment_index < len(new_tokenized_segments):
                            new_tokenized_url += f"/{new_tokenized_segments[variable_segment_index]}"
                            variable_segment_index += 1
                        else:
                            new_tokenized_url += f"/${next_token}"
                            next_token += 1
                
                if new_url.endswith('.html'):
                    new_tokenized_url += '.html'
                
                old_tokenized.append(old_token)
                new_tokenized.append(new_tokenized_url)
                
                old_regex.append(generate_regex_pattern(old_url, old_constants))
                new_regex.append(generate_regex_pattern(new_url, new_constants))
            
            if not is_predictable:
                patterns[domain] = "Unpredictable due to new information in alias URL"
            else:
                domain_data = {
                    'old_constants': old_constants,
                    'new_constants': new_constants,
                    'old_tokenized': old_tokenized[0] if old_tokenized else None,
                    'new_tokenized': new_tokenized[0] if new_tokenized else None,
                    'old_regex': old_regex[0] if old_regex else None,
                    'new_regex': new_regex[0] if new_regex else None,
                    'old_example': urls['old'][0] if urls['old'] else None,
                    'new_example': urls['new'][0] if urls['new'] else None
                }
                patterns[domain] = domain_data
                all_domains[domain] = domain_data
    with open('out.json', 'w') as f:
        json.dump(all_domains, f, indent=4)
    return patterns
def validate_input_url(url, domain):
    parsed_url = urlparse(url)
    return parsed_url.netloc.lower() == domain.lower()

def match_old_pattern(url, old_regex):
    return re.match(old_regex, urlparse(url).netloc + urlparse(url).path) is not None

def transform_url(url, old_pattern, new_pattern):
    old_parsed = urlparse(url)
    old_path = old_parsed.path.strip('/').split('/')
    
    old_pattern_parts = old_pattern.split('/')
    new_pattern_parts = new_pattern.split('/')
    
    variable_mapping = {}
    
    for old_segment, pattern_segment in zip(old_path, old_pattern_parts[1:]):  
        if pattern_segment.startswith('$'):
            variable_mapping[pattern_segment] = old_segment
    
    new_path = []
    for segment in new_pattern_parts[1:]:  
        if segment.startswith('$'):
            if segment in variable_mapping:
                new_path.append(variable_mapping[segment])
            else:
                new_path.append(segment)
        else:
            new_path.append(segment)
    
    new_url = urlunsplit((
        old_parsed.scheme,
        new_pattern_parts[0],
        '/' + '/'.join(new_path),
        old_parsed.query,
        old_parsed.fragment
    ))
    
    return new_url

def predict_url(domain, patterns):
    while True:
        input_url = input("\nEnter an old URL to predict (or 'b' to go back): ").strip()
        
        if input_url.lower() == 'b':
            return
        
        if not validate_input_url(input_url, domain):
            print(f"The entered URL does not belong to the domain {domain}. Please try again.")
            continue
        
        if match_old_pattern(input_url, patterns['old_regex'][0]):
            predicted_url = transform_url(input_url, patterns['old_tokenized'][0], patterns['new_tokenized'][0])
            print(f"\nOriginal URL: {input_url}")
            print(f"Predicted New URL: {predicted_url}")
            print("\nNote: This prediction is based on observed patterns and may not be 100% accurate.")
        else:
            print("The entered URL does not match the expected pattern for this domain. Please try again.")

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
                if isinstance(pattern, str):
                    print(f"\nPattern for {domain}: {pattern}")
                else:
                    print(f"\nPattern for {domain}:")

                    print(f"Old URL: {pattern['old_example']}")
                    print(f"New URL: {pattern['new_example']}")
                    print(f"Old URL (regex pattern): {pattern['old_regex']}")
                    print(f"New URL (regex pattern): {pattern['new_regex']}")
                    print(f"Old URL (tokenized pattern): {pattern['old_tokenized']}")
                    print(f"New URL (tokenized pattern): {pattern['new_tokenized']}")
                    
                    
                    predict_url(domain, pattern)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
            
        input("\nPress Enter to continue...")
if __name__ == "__main__":
    main()