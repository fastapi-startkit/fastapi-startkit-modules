1. Tasks:
we need refresh database as
Runs migrations once at the beginning of the test suite
Then wraps each test in a database transaction       
After each test → transaction is rolled back 
