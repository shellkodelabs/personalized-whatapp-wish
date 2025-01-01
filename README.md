# New Year Magic: Personalized Greetings Generator

## Overview
A Streamlit-based web application that generates personalized New Year greeting images using AI. Users can select themes or create custom prompts, and share the generated images via download, clipboard, or WhatsApp.

## Features
 - Personalized image generation with name integration
 - Multiple pre-defined themes
 - Custom prompt support
 
## Image sharing capabilities:
 - Direct download
 - Clipboard copying
 - WhatsApp sharing

## Prerequisites
 - Python 3.x

## Required packages:
 - streamlit
 - Pillow
 - boto3
 - pywhatkit
 - re 
 - subprocess

## Configuration
The application requires:
 - AWS Bedrock configuration in us-west-2 region
 - Proper environment setup for AWS credentials
 - WhatsApp Web access for message sending

## How to run
```sh
streamlit run app.py
```
