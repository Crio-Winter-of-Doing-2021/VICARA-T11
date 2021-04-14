Frontend

1. HTML, CSS, JS
2. VueJs
3. Vuetify

Backend

1. FastAPI (Python)
2. Postgres DB

Initial setup:
Frontend

- Install Nodejs from the official [Nodejs page](https://nodejs.org/en/)
- Install yarn from the official [Yarn installation page](https://classic.yarnpkg.com/en/docs/install/#windows-stable).
- Open your terminal
- Navigate to the project
- Run `yarn install`
- Run `yarn upgrade`
- Run `yarn serve` to start a local development server

Backend

- Install Python 3.9, Postgres on the system
- Run `pip install -r requirements.txt` in current directory
- Create an S3 bucket and a user with required permissions.
- Fill in the config.py file in backend/config.py with appropriate values
- Run the server using `uvicorn backend.app.main:app --reload`
- Before using any routes...
- Start the postgres shell and insert the following rows:
  `INSERT INTO user_states VALUES (1,'activated'), (2, 'deactivated');`
  `INSERT INTO object_scopes VALUES (1, 'private'), (2, 'public'), (3, 'unlisted');`
  `INSERT INTO object_states VALUES (1, 'active'), (2, 'inactive'), (3, 'deleted'), (4, 'destroyed');`
- Complete.

Incase of any issues, mail@nate.77.devcc@gmail.com
