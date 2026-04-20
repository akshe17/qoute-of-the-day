#!/usr/bin/env python3
"""
Quote of the Day updater - fetches a random quote and commits it to your repo
"""

import requests
import json
from datetime import datetime
import subprocess
import sys

def get_quote():
    """Fetch a random quote from type.fit API"""
    try:
        print("📡 Fetching quote...")
        response = requests.get('https://type.fit/api/quotes', timeout=5)
        response.raise_for_status()
        quotes = response.json()
        
        import random
        quote = random.choice(quotes)
        text = quote.get('text', 'Unknown quote')
        author = quote.get('author', 'Unknown')
        
        # Handle None author
        if author is None:
            author = 'Unknown'
        
        # Clean up author name
        if isinstance(author, str):
            author = author.replace(', type.fit', '')
        
        print(f"✅ Quote fetched: {text[:50]}...")
        return text, author
    except Exception as e:
        print(f"❌ Error fetching quote: {e}")
        import traceback
        traceback.print_exc()
        return "The only way to do great work is to love what you do.", "Steve Jobs"

def update_quote_file(quote, author):
    """Update the quotes.md file with the new quote"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read existing quotes
    try:
        with open('quotes.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Quote of the Day\n\nDaily quotes tracked here.\n\n"
    
    # Add new quote at the top
    new_entry = f"## {timestamp}\n\n> {quote}\n\n— *{author}*\n\n---\n\n"
    updated_content = content.replace("---\n\n", new_entry, 1) if "---" in content else content + "\n" + new_entry
    
    # Write back
    with open('quotes.md', 'w') as f:
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
    print("🎯 Fetching quote of the day...")
    quote, author = get_quote()
    
    print("📝 Updating quotes.md...")
    timestamp, quote_text, author_text = update_quote_file(quote, author)
    print(f"   {quote_text}\n   — {author_text}")
    
    print("📤 Committing and pushing...")
    if git_commit_and_push():
        print("✨ Done! Your GitHub graph just got greener!")
    else:
        print("⚠️  Script ran but push failed. Check your git config.")
