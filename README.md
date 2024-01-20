# Basic Repo Layout

You can ignore the starter_files folder. In the ```sql``` folder, you'll find the main schema for the DB. I don't believe this will need to change, but if so, let me know and we can reset the DB accordingly. 

As for the actual website logic, all of it lives under the ```fablesite``` directory. Under the ```js``` folder here, you'll find all the React code for the front end for this project. The chain starts from ```index.js``` and goes from there to ```GlobalViewPage.jsx``` and so on in terms of components. We use React Query to handle our API calls and TailWindCSS for the styling. You may find a lot of the files here extrenous and unnecessary, feel free to delete them. A lot of them are hold overs from a different verison of this project, but I still thought were necessary to keep just in case they were needed again. 

In the views and API folder, you'll find the Flask code for this project. I believe it's fairly self-explanatory. We only have one main view (index.py), that uses the API described in voteInfo.py. 

# Testing

Run ```npm install``` from the root folder to install all necessary packages. 

To run the local server use the following commands, each in a seperate terminal. 

```npx webpack```
```flask --app insta485 --debug run --host 0.0.0.0 --port 8000```

This is a good resource regarding the environemnt set up as well: https://eecs485staff.github.io/p3-insta485-clientside/#reactjs

You'll probably want to make a python requirements.txt file, for all the python dependencies. When you run the flask command, you'll get errors to install certain packages, which you'll need to do. 

Note: Due to the Wikimedia DB needing a VPN, you can't really test the backend code at the moment. However, at least for making changes to the front-end of the website, you can configure the API to return a mock data structure, which should be good enough for testing. 

