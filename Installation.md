## Installation
1\. Clone the repository
```
git clone https://github.com/BioB3/ku-polls.git
```
2\. Change directory to ku-polls
```
cd ku-polls
```
3\. Create a virtual environment
```
python -m venv env
```
4\. Activate the virtual environment
* On Linux and MacOS
    ```
    source env/bin/activate
    ```
* on MS Windows
    ```
    env\Scripts\activate
    ```
5\. Install dependencies
```
pip install -r requirements.txt
```
6\. Set values for externalized variables
* Copy the contents from sample.env
    * On Linux and MacOS
    ```
    cp sample.env .env
    ```
    * On MS Windows
    ```
    copy sample.env .env
    ```
* Set up values using console
    ```
    echo "SECRET_KEY=your_secret_key_here" >> .env
    echo "DEBUG=False" >> .env
    echo "ALLOWED_HOSTS=localhost,127.0.0.1,::1" >> .env
    echo "TIME_ZONE=Asia/Bangkok" >> .env
    ```
7\. Run migrations
```
python manage.py migrate
```
8\. Run tests
```
python manage.py test
```
9\. Load data from data fixtures
```
python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```