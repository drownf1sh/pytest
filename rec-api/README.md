# Recommendation - API

==============================

## Steps for setting up environment:
#### in your terminal run:
0. Set up local environment variables:
    - In terminal, type: `nano ~/.bash_profile`
    - Add Database configuration lines to your bash_profile:"
    `export REC_DB_URI="mongodb://username:password@host:port/db_name?authSource=admin"`
    `export GLB_DB_URI="mongodb://username:password@host:port/db_name?authSource=admin"`
    ...
    - Add Profanity Screening API to your bash_profile:
    `export PROFANITY_SCREEN_API="http://cms_profanity_screen_api_url"`
    - Add Store Name Duplicate Check API to your bash_profile:
    `export STORE_NAME_DUP_CHECK_API="http://mcu_store_name_dup_check_api_url"`
    - Add Redis DB config to your bash_profile:
    `REDIS_HOST_STR = host`
    `REDIS_PORT = port`
    `REDIS_PASSWORD = password`
    - Add Google credential json file path to your bash_profile:
    `
     export PUBSUB_CREDENTIAL=[local path for dev.json]
    `
    - Save then exit
    - Load edited bash_profile:
    `source ~/.bash_profile`
1. python3 -m venv env(optional)
2. source env/bin/activate(optional)
3. pip3 install -r requirements.txt
4. python3(or python) src/main.py run
5. click the local url in terminal for api service: default on http://0.0.0.0:5000/api/rec/doc/
6. (optional) python src/api_test.py "https://mik.dev.platform.michaels.com" to test all dev APIs. You can change the arg in this command and environment variables like REC_DB_URI to test tst APIs

###### Step 1 is to install virtual environment for your project
###### Step 2 is to activate the virtual environment
###### Step 3 is to install all necessary packages into env folder that specified by requirements.txt

## Steps for building and running Docker image
#### Because rec-api was deployed as Docker image, it's also recommended to build and run docker image in your local environment to avoid any issues like missing packages in requirements.txt
0. Download and install uwsgi image 
    - https://bitbucket.org/miktechnology/python-uwsgi/src/master/
1. Create a file named Dockerfile under project folder, paralleling with README.md
2. Copy and paste following code into Dockerfile:
```
FROM python38-uwsgi:latest
WORKDIR /app
ARG APP_BRANCH
ARG APP_NAME
ARG APP_PROJ
ARG APP_VERSION
ENV APP_BRANCH=$APP_BRANCH \
 APP_NAME=$APP_NAME \
 APP_PROJ=$APP_PROJ \
 APP_VERSION=$APP_VERSION
ENV NLTK_DATA /nltk_data/
COPY requirements.txt .
RUN set -ex && \
    mkdir -p $NLTK_DATA && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
COPY src/ /app/
```
3. In the terminal, navigate to the project folder
4. Run following commend to build docker image
```
docker build -t any_image_name .
```
5. Run following commend to run the docker image you just built
```
docker run -t -p 8080:8080 any_image_name
```
6. Check your app at http://localhost:8080/
7. Trouble shot for error:  `File "./app/main/configuration/vault_vars_config.py", line 75, in <module>
    read_secret_result = client.secrets.kv.v1.read_secret(`
   1. go to vault_vars_config.py and update every path in the `if not APP_ENV` session
   2. For gcp credential files, put them under `src/main/gcp_credential` folder
   3. update PUBSUB_CREDENTIAL path
   ``` 
    cur_path = os.path.dirname(os.path.abspath(__file__))
    PUBSUB_CREDENTIAL = (cur_path[: cur_path.rfind("/")] + "/gcp_credential/dev.json")
   ```

## Notice:
If you need to install any packages, please also include the package with version number in requirement.txt file
 
## Coding Guidance:
All business logic should be written in app/main folder and tests should be written in app/tests folder.
All common functions are recommended to be placed in utils folder
