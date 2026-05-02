# Contribution

This repository contains several packages and examples that to support the fastapi_starkit. The main components of fastapi_startkit stay inside `fastapi_startkit/src` directory and docs are available in `fastapi_startkit.github.io`, examples in examples and starter application in application.

## Fastapi_startkit Contribution Guides
1. This is the core components of this starter kit/framework, while making change, or adding any feature, or fixing anything in examples, application or even in the starterkit, always consider not to CHANGE `fastapi_startkit/src` unless Explict necessary.
2. If there is an absolute necessary to make any changes in the `fastapi_startkit/src`, please consider any alternatives approaches, or any potential impacts on the other sides of the components, and if it's not possbile unless making change, consider creating a document explaining the chnages that you are going to make, and it's potential affects and impacts, and submit for review.

3. Add potential test cases that can be used to validate the changes made to the codebase. Consider looking into the existing code structure, fixtures, database structures, etc., before writing any 
   test cases.
4. You are allowed to run test suite and self-verify if the fixes are correct or not, but don't try to wipe the database, nor any destructive operations that could break the system or loss data. 
   To run the tests, go the `fastapi_startkit` directory and run with `uv run pytest {path}`, to run startkit's component-related tests. 
