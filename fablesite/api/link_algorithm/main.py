import re
import random
from urllib.parse import urlparse, parse_qs, urlencode
import json
from collections import defaultdict
import logging
import difflib

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def tokenize_url(url):
    parsed = urlparse(url)
    path = parsed.path.strip('/').split('/')
    query = parse_qs(parsed.query)
    
    extension = None
    if path and '.' in path[-1]:
        path[-1], extension = path[-1].rsplit('.', 1)
    
    return {
        'scheme': parsed.scheme or 'http',
        'domain': parsed.netloc,
        'path': path,
        'query': query,
        'extension': extension
    }

def is_similar(s1, s2):
    return len(s1) == len(s2) and sum(a != b for a, b in zip(s1, s2)) <= 1

def identify_pattern(old_urls, new_urls):
    old_domains = [urlparse(url).netloc for url in old_urls]
    new_domains = [urlparse(url).netloc for url in new_urls]
    
    if len(set(old_domains)) != 1 or len(set(new_domains)) != 1:
        domain_change = None
    elif old_domains[0] != new_domains[0]:
        domain_change = new_domains[0]
    else:
        domain_change = None
    
    patterns = []
    for old, new in zip(old_urls, new_urls):
        old_tokens = tokenize_url(old)
        new_tokens = tokenize_url(new)
        
        pattern = {
            'path': [],
            'query': [],
            'extension': ('change', old_tokens['extension'], new_tokens['extension']) if old_tokens['extension'] != new_tokens['extension'] else ('keep', old_tokens['extension']),
            'repeat_last_segment': False
        }
        
        if new_tokens['path'] and new_tokens['path'][-1].isdigit():
            for segment in new_tokens['path'][:-1]:
                if segment == new_tokens['path'][-1]:
                    pattern['repeat_last_segment'] = True
                    break
        
        matcher = difflib.SequenceMatcher(None, old_tokens['path'], new_tokens['path'])
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    pattern['path'].append(('keep', i1 + k))
            elif tag == 'delete':
                for k in range(i2 - i1):
                    pattern['path'].append(('remove', i1 + k))
            elif tag == 'insert':
                for k in range(j2 - j1):
                    pattern['path'].append(('add', i1, new_tokens['path'][j1 + k]))
            elif tag == 'replace':
                for k in range(min(i2 - i1, j2 - j1)):
                    old_seg = old_tokens['path'][i1 + k]
                    new_seg = new_tokens['path'][j1 + k]
                    if old_seg.isdigit() and new_seg.isdigit() and len(old_seg) == 1 and len(new_seg) == 2 and new_seg[0] == '0':
                        pattern['path'].append(('pad_zero', i1 + k))
                    elif old_seg.isdigit() and new_seg.isdigit():
                        pattern['path'].append(('keep_number', i1 + k))
                    elif is_similar(old_seg, new_seg):
                        pattern['path'].append(('keep_similar', i1 + k, new_seg))
                    else:
                        pattern['path'].append(('change', i1 + k, old_seg, new_seg))
                if i2 - i1 > j2 - j1:
                    for k in range(j2 - j1, i2 - i1):
                        pattern['path'].append(('remove', i1 + k))
                elif j2 - j1 > i2 - i1:
                    for k in range(i2 - i1, j2 - j1):
                        pattern['path'].append(('add', i2, new_tokens['path'][j1 + k]))
        
        all_keys = set(old_tokens['query'].keys()) | set(new_tokens['query'].keys())
        for key in all_keys:
            if key in old_tokens['query'] and key in new_tokens['query']:
                if old_tokens['query'][key] != new_tokens['query'][key]:
                    pattern['query'].append(('change', key, old_tokens['query'][key][0], new_tokens['query'][key][0]))
                else:
                    pattern['query'].append(('keep', key))
            elif key in new_tokens['query']:
                pattern['query'].append(('add', key, new_tokens['query'][key][0]))
            else:
                pattern['query'].append(('move_to_path', key))
        
        patterns.append(pattern)
    
    final_pattern = {
        'domain_change': domain_change,
        'path': [],
        'query': patterns[0]['query'],
        'extension': patterns[0]['extension'],
        'repeat_last_segment': all(p['repeat_last_segment'] for p in patterns)
    }
    
    max_path_len = max(len(p['path']) for p in patterns)
    for i in range(max_path_len):
        actions = [p['path'][i] if i < len(p['path']) else ('keep', i) for p in patterns]
        if all(a == actions[0] for a in actions):
            final_pattern['path'].append(actions[0])
        else:
            final_pattern['path'].append(('variable', i, actions))
    
    # logging.debug(f"Identified pattern: {final_pattern}")
    return final_pattern

def apply_pattern(url, pattern):
    tokens = tokenize_url(url)
    new_tokens = tokens.copy()
    
    if pattern['domain_change']:
        new_tokens['domain'] = pattern['domain_change']
    
    new_path = []
    for action in pattern['path']:
        if action[0] == 'keep':
            if action[1] < len(tokens['path']):
                new_path.append(tokens['path'][action[1]])
        elif action[0] == 'change':
            if action[1] < len(tokens['path']):
                new_path.append(action[3])
        elif action[0] == 'add':
            new_path.insert(action[1], action[2])
        elif action[0] == 'remove':
            pass 
        elif action[0] == 'keep_number':
            if action[1] < len(tokens['path']):
                new_path.append(tokens['path'][action[1]])
        elif action[0] == 'keep_similar':
            if action[1] < len(tokens['path']):
                new_path.append(action[2])
        elif action[0] == 'pad_zero':
            if action[1] < len(tokens['path']) and tokens['path'][action[1]].isdigit() and len(tokens['path'][action[1]]) == 1:
                new_path.append(f"0{tokens['path'][action[1]]}")
            else:
                new_path.append(tokens['path'][action[1]])
        elif action[0] == 'variable':
            if action[1] < len(tokens['path']):
                for var_action in action[2]:
                    if var_action[0] == 'change' and tokens['path'][action[1]] == var_action[2]:
                        new_path.append(var_action[3])
                        break
                else:
                    new_path.append(tokens['path'][action[1]])
    
    new_tokens['path'] = new_path
    
    if pattern['repeat_last_segment']:
        last_numeric_segment = None
        for segment in reversed(new_tokens['path']):
            if segment.isdigit():
                last_numeric_segment = segment
                break
        if last_numeric_segment:
            new_tokens['path'][-1] = last_numeric_segment
    
    for action in pattern['query']:
        if action[0] == 'keep':
            if action[1] in tokens['query']:
                new_tokens['query'][action[1]] = tokens['query'][action[1]]
        elif action[0] == 'change':
            new_tokens['query'][action[1]] = [action[3]]
        elif action[0] == 'add':
            new_tokens['query'][action[1]] = [action[2]]
        elif action[0] == 'move_to_path':
            if action[1] in tokens['query']:
                new_tokens['path'].append(tokens['query'][action[1]][0])
                del new_tokens['query'][action[1]]
    
    if pattern['extension'][0] == 'change':
        new_tokens['extension'] = pattern['extension'][2]
    elif pattern['extension'][0] == 'keep' and pattern['extension'][1] is None:
        new_tokens['extension'] = None
    
    new_path = '/'.join(new_tokens['path'])
    if new_tokens['extension']:
        new_path = f"{new_path}.{new_tokens['extension']}"
    
    new_query = urlencode(new_tokens['query'], doseq=True)
    
    new_url = f"{new_tokens['scheme']}://{new_tokens['domain']}/{new_path}"
    if new_query:
        new_url += f"?{new_query}"
    
    # logging.debug(f"Original URL: {url}")
    # logging.debug(f"Predicted URL: {new_url}")
    
    return new_url

def is_unpredictable(old_url, new_url):
    old_tokens = tokenize_url(old_url)
    new_tokens = tokenize_url(new_url)
    
    if len(new_tokens['path']) > len(old_tokens['path']):
        added_segments = new_tokens['path'][len(old_tokens['path']):]
        if any(len(seg) > 20 for seg in added_segments):
            return True
    
    if re.search(r'/\d{4}/\d{2}/', new_url) and not re.search(r'/\d{4}/\d{2}/', old_url):
        return True
    
    if (old_tokens['path'][-1].isdigit() and new_tokens['path'][-1].replace('_', ' ').replace('+', ' ').isalpha()):
        return True
    
    return False

def process_urls(data, training_size, randomness):
    domains = defaultdict(list)
    for item in data:
        domain = urlparse(item['link']).netloc
        domains[domain].append(item)
    
    results = []
    correct_predictions = 0 
    total = 0
    unsolvable_few_urls = 0
    urls_used_for_training = 0
    unpredictable_urls = 0
    
    for domain, items in domains.items():
        logging.debug(f"Processing domain: {domain} with {len(items)} items")
        
        if len(items) < training_size + 1:
            logging.debug(f"Domain {domain} has too few items: {len(items)}")
            unsolvable_few_urls += len(items)
            continue

        if randomness:
            random.shuffle(items)

        training_items = items[:training_size]
        test_items = items[training_size:]
        
        urls_used_for_training += len(training_items)
        
        old_urls = [item['link'] for item in training_items]
        new_urls = [item['alias'] for item in training_items]
        
        if any(is_unpredictable(old, new) for old, new in zip(old_urls, new_urls)):
            unpredictable_urls += len(items)
            continue
        
        pattern = identify_pattern(old_urls, new_urls)
        
        for item in test_items:
            old_url = item['link']
            actual_new_url = item['alias']
            
            if is_unpredictable(old_url, actual_new_url):
                unpredictable_urls += 1
                continue
            
            predicted_url = apply_pattern(old_url, pattern)
            
            if predicted_url.startswith('http://') and actual_new_url.startswith('https://'):
                predicted_url = 'https://' + predicted_url[7:]
            
            predicted_url = predicted_url.rstrip('/')
            actual_new_url = actual_new_url.rstrip('/')
            
            is_correct = predicted_url.lower() == actual_new_url.lower()
            
            if is_correct:
                correct_predictions += 1  
            total += 1
            
            results.append({
                'broken_url': old_url,
                'predicted_url': predicted_url,
                'actual_new_url': actual_new_url,
                'is_correct': is_correct
            })
    
    logging.debug(f"Processed URLs: {total}, Correct predictions: {correct_predictions}, Unpredictable URLs: {unpredictable_urls}")
    
    if total - unpredictable_urls == 0:
        logging.warning("All processed URLs were unpredictable")
        accuracy = 0
    else:
        accuracy = correct_predictions / (total - unpredictable_urls)
    
    return results, accuracy, unsolvable_few_urls, total, urls_used_for_training, unpredictable_urls, correct_predictions
def print_and_write(file, message):
    print(message)
    file.write(message + "\n")

if __name__ == "__main__":
    with open('data.json', 'r') as f:
        data = json.load(f)

    training_size = int(input("Enter the number of URLs to use for training per domain: "))
    randomness = input("Enter 'y' to use random URLs for training, or 'n' to use the first " +
                       f"{training_size} URLs for training: ").lower() == 'y'

    if randomness:
        num_runs = int(input("Enter the number of random runs to perform: "))
        best_accuracy = 0
        best_results = None
        best_stats = None
        run_accuracies = []

        for run in range(num_runs):
            with open('stats.txt', 'a') as stats_file:  
                print_and_write(stats_file, f"\nPerforming run {run + 1} of {num_runs}...")
            results, accuracy, unsolvable_few_urls, total, urls_used_for_training, unpredictable_urls, correct_predictions = process_urls(data, training_size, randomness)
            
            run_accuracies.append(accuracy)
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_results = results
                best_stats = (accuracy, unsolvable_few_urls, total, urls_used_for_training, unpredictable_urls, correct_predictions)
            with open('stats.txt', 'a') as stats_file:  
                print_and_write(stats_file, f"\nRun {run + 1} accuracy: {accuracy:.2%}")

        print("\n--------- Best Results ---------")
        accuracy, unsolvable_few_urls, total, urls_used_for_training, unpredictable_urls, correct_predictions = best_stats
        results_to_save = best_results
    else:
        results, accuracy, unsolvable_few_urls, total, urls_used_for_training, unpredictable_urls, correct_predictions = process_urls(data, training_size, randomness)
        print("\n--------- Results ---------")
        results_to_save = results

    with open('stats.txt', 'w') as stats_file: 
        total_predictable = total - unpredictable_urls
        accuracy_predictable = correct_predictions / total_predictable if total_predictable > 0 else 0       
        print_and_write(stats_file, f"1. Total URLs in dataset: {len(data)}")
        print_and_write(stats_file, "   Context: This is the total number of URL pairs (old and new) in the input data.\n")
        
        print_and_write(stats_file, f"2. Training size per domain: {training_size}")
        print_and_write(stats_file, "   Context: This is the number of URL pairs used for training the model for each domain.\n")
        
        print_and_write(stats_file, f"3. Randomness: {'Yes' if randomness else 'No'}")
        print_and_write(stats_file, "   Context: Indicates whether the training URLs were randomly selected or not.\n")
        
        if randomness:
            print_and_write(stats_file, f"4. Number of random runs: {num_runs}")
            print_and_write(stats_file, "   Context: The number of times the process was repeated with different random samples.\n")
            
            print_and_write(stats_file, "5. Run Accuracies:")
            for i, acc in enumerate(run_accuracies, 1):
                print_and_write(stats_file, f"   Run {i}: {acc:.2%}")
        
        print_and_write(stats_file, f"\n6. Best Accuracy: {accuracy:.2%}")
        print_and_write(stats_file, "   Context: The highest percentage of correctly predicted new URLs out of all processed URLs.")
        # print_and_write(stats_file, "   Mean: {:.2%}".format(sum(run_accuracies) / num_runs) if randomness else "")
        # print_and_write(stats_file, "   Mode: {:.2%}".format(max(set(run_accuracies), key=run_accuracies.count)) if randomness else "")
        print_and_write(stats_file, f"\n    Accuracy (predictable URLs only): {accuracy_predictable:.2%}")
        print_and_write(stats_file, "       Context: The percentage of correctly predicted new URLs out of URLs that were deemed predictable.")

        print_and_write(stats_file, f"\n7. Unsolvable due to few URLs in the domain: {unsolvable_few_urls}")
        print_and_write(stats_file, "   Context: Number of URLs in domains that had fewer URLs than the specified training size.\n")
        
        print_and_write(stats_file, f"8. Unpredictable URLs: {unpredictable_urls}")
        print_and_write(stats_file, "   Context: Number of URLs that were too complex or random to predict reliably.\n")
        
        print_and_write(stats_file, f"9. URLs Processed: {total}")
        print_and_write(stats_file, "   Context: The number of URLs that were actually processed for prediction (excluding unsolvable and unpredictable).\n")
        
        print_and_write(stats_file, f"10. URLs used for training: {urls_used_for_training}")
        print_and_write(stats_file, "   Context: Total number of URLs used to train the model across all domains.\n")
        
        total_accounted = unsolvable_few_urls + total + urls_used_for_training + unpredictable_urls
        print_and_write(stats_file, f"11. Total URLs accounted for: {total_accounted}")
        print_and_write(stats_file, "    Context: Sum of unsolvable, processed, training, and unpredictable URLs.\n")

        print_and_write(stats_file, "\nUSER INTERACTION BUCKETS")
        print_and_write(stats_file, "--------------------------------")
        print_and_write(stats_file, f"1. URLs used for training:      {urls_used_for_training:5d} ({urls_used_for_training/total_accounted:.2%})")
        print_and_write(stats_file, f"2. Manual user intervention:    {unsolvable_few_urls + unpredictable_urls + (total - correct_predictions):5d} ({(unsolvable_few_urls + unpredictable_urls + (total - correct_predictions))/total_accounted:.2%})")
        print_and_write(stats_file, f"   a. Unsolvable (few URLs):    {unsolvable_few_urls:5d} ({unsolvable_few_urls/total_accounted:.2%})")
        print_and_write(stats_file, f"   b. Unpredictable:            {unpredictable_urls:5d} ({unpredictable_urls/total_accounted:.2%})")
        print_and_write(stats_file, f"   c. Incorrectly predicted:    {total - correct_predictions:5d} ({(total - correct_predictions)/total_accounted:.2%})")
        print_and_write(stats_file, f"3. Correctly predicted:         {correct_predictions:5d} ({correct_predictions/total_accounted:.2%})")
        print_and_write(stats_file, f"                                -----")
        print_and_write(stats_file, f"   Total:                       {total_accounted:5d} (100.00%)")
    with open('output.json', 'w') as f:
        json.dump(results_to_save, f, indent=2)
    print("Prediction results saved to output.json")