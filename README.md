Policy Docs Retrieval System

Overview

This project explores using Google’s LangExtract library to retrieve specific structured variables from family law court documents.

The goal is to extract key legal fields — such as:

Legal Custody, Age, If there is certain previsions etc...

— directly from unstructured family court PDFs using LLM-powered extraction.

This repository is currently experimental and under active development.

Purpose

Family court documents are typically semi-structured but not machine-readable.

This project attempts to:

Convert PDF documents into text

Use LangExtract to identify and extract predefined legal variables

Structure those variables for downstream retrieval or analysis

Current Stack

Python

Google LangExtract

Ollama (local LLM inference)

Llama / Mistral models (testing)
