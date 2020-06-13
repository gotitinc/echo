# GotIt Early Developer Program - Code Name “ECHO”

## Overview
Welcome to the Got It Querychat Early Developer Program and community. We thank you very much for providing your expertise and feedback to our project.

Querychat is a new product, currently in development, that will enable the next generation of chatbots to retrieve data directly from databases in order to build richer, more capable experiences. This is achieved through a sophisticated classification system which automatically detects intents from customer data and translates them into SQL queries against a customer’s database schema.

This repo contains code and assets for Phase 1 of ECHO

## Provided resources

- Simplified InDiE file (data/InDiE_0.3_CCAI_20200608155202.simple.json): a set of intents, slots discovered by our InDiE library from a dataset of (question, SQL query) tuples. Your publisher will publish these intents to your target chatbot framework.

- Two web services
  - InDiE fulfillment service (endpoint only): Single API endpoint that returns query execution results for provided intent id and filled slot values.
  - DialogFlow fulfillment service (endpoint + code): Sample fulfillment endpoint demonstrating 
    - how to handle fulfillment call from DialogFlow
    - extract intent id, slot values from DialogFlow payload, 
    - call InDiE fulfillment endpoint to get response text
    - send response back to DialogFlow in DialogFlow specific format
  - A reference implementation for DialogFlow publisher (code)
[python jupyter notebook] publisher module that configures intents, custom entities, etc in a DialogFlow agent using DialogFlow APIs