#!/usr/bin/env python3
"""
Quote of the Day updater - fetches a random quote and commits it to your repo
"""
import requests
import json
from datetime import datetime
import subprocess
import sys
import random
import traceback

def get_quote():
    """Fetch a random quote from type.fit API"""
    try:
        print("📡 Fetching quote from type.fit...")
        response = requests.get('https://type.fit/api/quotes', timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API returned status {response.status_code}")
            raise Exception(f"API error: {response.status_code}")
        
        quotes = response.json()
        print(f"Got {len(quotes)} quotes from API")
        
        if not quotes or len(quotes) == 0:
            print("❌ No quotes returned from API")
            raise Exception("Empty quotes list")
        
        quote = random.choice(quotes)
        print(f"Selected quote: {quote}")
        
        text = quote.get('text', 'Unknown quote')
        author = quote.get('author', 'Unknown')
        
        # Handle None author
        if author is None:
            author = 'Unknown'
        else:
            author = str(author).replace(', type.fit', '').strip()
        
        # Clean up text
        text = str(text).strip()
        
        print(f"✅ Quote fetched successfully!")
        print(f"   Text: {text[:60]}...")
        print(f"   Author: {author}")
        return text, author
        
    except Exception as e:
        print(f"❌ Error fetching quote: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return "The only way to do great work is to love what you do.", "Steve Jobs"

def update_quote_file(quote, author):
    """Update the quotes.md file with the new quote"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read existing quotes
    try:
        with open('quotes.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Quote of the Day\n\nDaily quotes tracked here.\n\n"
    
    # Add new quote at the top
    new_entry = f"## {timestamp}\n\n> {quote}\n\n— *{author}*\n\n---\n\n"
    updated_content = content.replace("---\n\n", new_entry, 1) if "---" in content else content + "\n" + new_entry
    
    # Write back
    with open('quotes.md', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return timestamp, quote, author

def git_commit_and_push():
    """Commit and push changes to GitHub"""
    try:
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not result.stdout.strip():
            print("No changes to commit")
            return False
        
        # Stage changes
        subprocess.run(['git', 'add', 'quotes.md'], check=True)
        
        # Commit
        today = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(['git', 'commit', '-m', f'Quote of the day: {today}'], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        print("✅ Successfully pushed to GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False

if __name__ == '__main__':
    print("🎯 Starting Quote of the Day updater...")
    quote, author = get_quote()
    
    print("📝 Updating quotes.md...")
    timestamp, quote_text, author_text = update_quote_file(quote, author)
    print(f"   {quote_text}\n   — {author_text}")
    
    print("📤 Committing and pushing...")
    if git_commit_and_push():
        print("✨ Done! Your GitHub graph just got greener!")
    else:
        print("⚠️  Script ran but push failed. Check your git config.")
