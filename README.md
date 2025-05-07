# dsci551finale
[report on usage
](https://docs.google.com/document/d/1omEPalqPez8KLwBPnxVR-6ecH3T4l8JZ/edit?usp=sharing&ouid=110414194953995065482&rtpof=true&sd=true)

Install MongoDB in localhost port 27017. The installation instructions provided by Professor Wu on an EC2 instance will suffice.

populate MongoDB with your preferred collections. The code is designed to allow work with any sort of collections and dbs.

Install mysql server and create a local instance

Create sql root for sqlalchemy engine and leave database name as variable to be specified during implementation step.

##### pip install requirements.txt ###### on your venv to run the programs.

Acquire an OpenAI key to access ChatGPT, and put the key into ### key.txt ### in the same folder as the code.

For MongoDB specifically, you can run the two files for different goals:

api.py allows for direct execution of natural language requests to be executed immediately.

mongosh_suggestions gives you commands you can choose to run on mongosh, should you wish to see mongosh commands instead.
