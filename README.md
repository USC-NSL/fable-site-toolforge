# Basic Repo Layout

You can ignore the starter_files folder. In the ```sql``` folder, you'll find the main schema for the DB. I don't believe this will need to change, but if so, let me know and we can reset the DB accordingly. 

As for the actual website logic, all of it lives under the ```fablesite``` directory. Under the ```js``` folder here, you'll find all the React code for the front end for this project. The chain starts from ```index.js``` and goes from there to ```GlobalViewPage.jsx``` and so on in terms of components. We use React Query to handle our API calls and TailWindCSS for the styling. You may find a lot of the files here extrenous and unnecessary, feel free to delete them. A lot of them are hold overs from a different verison of this project, but I still thought were necessary to keep just in case they were needed again. 

In the ```views``` and ```API``` folder, you'll find the Flask code for this project. I believe it's fairly self-explanatory. We only have one main view (index.py), that uses the API described in ```voteInfo.py```. 

# Testing

Run ```npm install``` from the root folder to install all necessary packages. 

To run the local server use the following commands, each in a seperate terminal. 

```npx webpack```
```flask --app insta485 --debug run --host 0.0.0.0 --port 8000```

This is a good resource regarding the environemnt set up as well: https://eecs485staff.github.io/p3-insta485-clientside/#reactjs

You'll probably want to make a python requirements.txt file, for all the python dependencies. When you run the flask command, you'll get errors to install certain packages, which you'll need to do. 

Note: Due to the Wikimedia DB needing a VPN, you can't really test the backend code at the moment. However, at least for making changes to the front-end of the website, you can configure the API to return a mock data structure, which should be good enough for testing. 

# FableForge Deployment Guide

## Setting Up Your Wikimedia Developer Account

Before you can deploy to Toolforge, you need to set up a Wikimedia developer account:

1. Create a developer account at https://admin.toolforge.org/
2. Request approval for your account 
   - Example request: https://toolsadmin.wikimedia.org/tools/membership/status/1690
3. Once approved, contact Professor Madhyastha who can grant your account admin access

## SSH Key Setup

1. Navigate to your SSH directory:
   ```
   cd .ssh
   ```

2. Generate an SSH key:
   ```
   ssh-keygen -t ed25519 -C "your_toolforge_email_id"
   ```
   Example: `ssh-keygen -t ed25519 -C "dacharya@usc.edu"`

   **Note**: You'll be prompted for a passphrase. Record this passphrase as you'll need it every time you log in to the Toolforge console.

3. Display your public key:
   ```
   cat id_ed25519.pub
   ```
   The output will look like: `ssh-ed25519 [KEY] [your toolforge email id]`

4. **Important**: Add this SSH key to https://toolsadmin.wikimedia.org/profile/settings/ssh-keys/

## Deployment Process

1. Navigate to your SSH directory:
   ```
   cd ~/.ssh
   ```

2. Connect to Toolforge:
   ```
   ssh -i key [Toolforge_username]@login.toolforge.org
   ```
   Enter your passphrase when prompted.

3. After successful login to the Toolforge Console, access the "Fable" resources:
   ```
   become fable
   ```

4. Navigate to the project directory:
   ```
   cd /data/project/fable/www/python/src/fablesite-toolforge-nsl
   ```

5. Reset and update the codebase:
   ```
   git reset --hard
   git checkout develop-3.0
   git pull origin develop-3.0
   ```

6. Configure the database:
   ```
   cd fablesite
   ```
   
7. Edit the "config.py" file with the following database configuration (omitted the PASSWORD, CONSUMER_TOKEN and SECRET_TOKEN):
   ```python
   HOST = "tools.db.svc.wikimedia.cloud"
   USERNAME = "s55570"
   PASSWORD = "" 
   DB_NAME = "s55570__FABLE"
   CONSUMER_TOKEN = ""
   SECRET_TOKEN = ""
   ```

8. Restart the web service:
   ```
   webservice restart
   ```

## Database Access

After executing `become fable`:

1. Connect to the database:
   ```
   sql tools
   ```

2. List all databases:
   ```
   show databases;
   ```

3. Select the FableForge database:
   ```
   use s55570__FABLE;
   ```

4. View database tables:
   ```
   show tables;
   ```

## Troubleshooting

If you encounter any issues during deployment:
- Verify your SSH key has been properly added to Toolsadmin
- Check that you're using the correct passphrase
- Ensure you have the proper permissions for the Fable project
