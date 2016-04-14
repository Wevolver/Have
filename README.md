# Multiple 

Storing complex objects in a version system.

## Goals
### Functional goals
#### Minimal working application

Be able to manipulate in python multiple versions of one object with a git 
based backend and a remote object storage.

#### Short-term goals 

Manipulate multiple versions of multiple objects with concurrent access.

#### Long-term goals


### Implementation goals 

Be agnostic as possible and make components easily swappable through a 
clear API.
Implement and support by default:
    - a git backend as version system
    - a postgres as cache system

## Code style

- Google docstrings style 
- pep8 
- tox 
