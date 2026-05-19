#!/bin/bash

# Create config.json from example
echo "Creating config.json from example..."

# Check if config.json exists
if [ -f "config/config.json" ]; then
    echo "⚠️  config.json already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
fi

# Copy example to config
cp config/config.example.json config/config.json

echo "✅ config.json created!"
echo "📝 Please edit config/config.json and add:"
echo "   - Your Gmail address"
echo "   - Your App Password (16 characters)"
echo "   - (Optional) Telegram bot token and chat ID"
