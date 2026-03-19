# Product Overview

This workspace contains two related projects:

## price-alert
A focused price monitoring tool. Users add Amazon product URLs with a target price and WhatsApp number. The backend scrapes Amazon every 30 minutes and sends a WhatsApp notification via Meta Business Cloud API when the price drops to or below the target.

## ai-shopping-assistant
An extension of price-alert that adds a conversational AI layer. Users can describe what they want in natural language (e.g. "running shoes under 5000"), and the assistant parses intent (category, use-case, budget), recommends products from a local catalog, and also supports the same price alert/watchlist functionality.

## Core User Flow
1. User submits a natural language query or product URL + target price
2. System parses intent or monitors price
3. User receives recommendations or a WhatsApp alert when price drops

## Target Market
Indian consumers (prices in ₹, WhatsApp-first notification, Amazon.in focus).
