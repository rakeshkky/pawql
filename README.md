# PawQL

A comprehensive pet care management system built with Hasura DDN (Data Delivery Network) that provides natural language querying capabilities for pet care data through PromptQL integration.

## Overview

PawQL is a modern pet care management platform that combines:
- **Natural Language SQL Generation**: Query pet care data using natural language through PromptQL
- **Real-time Dashboard**: Interactive web dashboard for monitoring pet care locations
- **Weather Integration**: Location-based weather data for operational insights
- **Evaluation Framework**: Comprehensive testing and evaluation system for query accuracy

## Architecture

The project consists of three main components:

### 🏗️ DDN Backend (`ddn/`)
- **Hasura DDN Supergraph**: GraphQL API with multiple subgraphs
- **Database Connector**: Integration for pet care data from Snowflake
- **Logic Connector**: Python functions for coordinates and weather data
- **PromptQL Integration**: The AI agent for interacting with the PawQL data domain ()
- **Project URL**: https://promptql.console.hasura.io/project/enabled-stork-1938

### 🎨 Dashboard UI (`dashboard-ui/`)
- **React + TypeScript**: Modern web interface
- **Location Management**: Select and monitor pet care facilities
- **Visual Analytics**: Charts and metrics for operational insights
- **Real-time Data**: Live dashboard updates with weather integration

### 🧪 Evaluation System (`evals/`)
- **Automated Testing**: Evaluate PromptQL query accuracy
- **LLM-as-a-Judge**: AI-powered evaluation using Anthropic Claude
- **Comprehensive Reports**: Detailed markdown reports with metrics
- **Multiple Difficulty Levels**: Easy, medium, and hard query test sets
